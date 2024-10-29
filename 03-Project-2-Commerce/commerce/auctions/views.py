from urllib.parse import urlparse

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, is_valid_path
from django import forms

from .models import User, Listing, Bid, Comment, Category


def index(request):
    # Get only active listings
    active_listings = Listing.objects.filter(is_active=True)

    if len(active_listings) > 0:
        return render(request, "auctions/index.html", {
            "active_listings": active_listings,
        })
    else:
        return render(request, "auctions/index.html", {
            "message": "No listings to show."
        })


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            next_url = request.POST.get('next')

            if next_url:
                return redirect(next_url)

            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url="/login")
def create_listing(request):
    categories = Category.objects.all()
    user = request.user

    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        starting_price = request.POST["starting_price"]
        image_URL = request.POST["image_URL"]
        category_ids = request.POST.getlist("category")

        if not Listing.objects.filter(title=title).exists():
            created_listing = Listing.objects.create(title=title, description=description,
                                                     starting_price=starting_price,
                                                     image_URL=image_URL, owner=user)

            # Convert category_ids (strings) to a list of Category instances
            category_objects = Category.objects.filter(id__in=category_ids)
            created_listing.category.set(category_objects)
            created_listing.save()

            return redirect("get_listing", id=created_listing.id)
        else:
            return render(request, "auctions/create_listing.html", {
                "message": "Listing already exists."
            })

    # If GET request, render the form
    return render(request, "auctions/create_listing.html", {
        "categories": categories
    })


def get_categories(request):
    categories = Category.objects.annotate(listings_count=Count("categories"))

    if categories is not None and len(categories) > 0:
        return render(request, "auctions/categories.html", {
            "categories": categories,
        })
    else:
        return render(request, "auctions/categories.html", {
            "message": "No categories to show."
        })


def get_category(request, id):
    category = Category.objects.get(pk=id)
    active_listings_in_category = Listing.objects.filter(category=category.id, is_active=True)

    if category is not None:
        if len(active_listings_in_category) == 0:
            return render(request, "auctions/category.html", {
                "category": category,
                "message": "No active listings to show in this category."
            })
        else:
            return render(request, "auctions/category.html", {
                "category": category,
                "active_listings_in_category": active_listings_in_category
            })


def get_listing(request, id):
    user = request.user
    listing = Listing.objects.get(pk=id)
    is_listing_owner = listing.owner.id == user.id
    placed_bids = Bid.objects.filter(listing=listing)
    is_valid_bid = placed_bids.filter(is_valid=True)
    current_bid = placed_bids.last()
    username_current_bid = ""
    is_current_bid_owner = False
    comments = Comment.objects.filter(listing=listing)

    if placed_bids:
        username_current_bid = User.objects.filter(id=current_bid.owner_id)[0]
        if user.id == current_bid.owner_id:
            is_current_bid_owner = True

    # Retrieve and clear the message from the session
    bid_message_error = request.session.pop("bid_message_error", None)
    bid_message_success = request.session.pop("bid_message_success", None)

    comment_message_error = request.session.pop("comment_message_error", None)
    comment_message_success = request.session.pop("comment_message_success", None)
    comments_list_message_success = request.session.pop("comments_list_message_success", None)

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "is_listing_owner": is_listing_owner,
        "placed_bids": placed_bids,
        "is_valid_bid": is_valid_bid,
        "is_current_bid_owner": is_current_bid_owner,
        "username_current_bid": username_current_bid,
        "bid_message_error": bid_message_error,
        "bid_message_success": bid_message_success,
        "comment_message_error": comment_message_error,
        "comment_message_success": comment_message_success,
        "comments_list_message_success": comments_list_message_success,
        "comments": comments
    })


@login_required(login_url="/login")
def get_watchlist(request):
    user = request.user
    listings = Listing.objects.filter(watchlist=user.id).order_by("-is_active")

    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })


@login_required(login_url="/login")
def add_to_watchlist(request, id):
    user = request.user
    listing = Listing.objects.get(pk=id)

    if user in listing.watchlist.all():
        # Remove from watchlist if it's already there
        listing.watchlist.remove(user)
    else:
        listing.watchlist.add(user)

    return redirect("get_listing", id=listing.id)


@login_required(login_url="/login")
def place_bid(request, id):
    listing = Listing.objects.get(pk=id)

    if request.method == "POST" and listing.is_active:
        placed_bid = request.POST["bid"]
        current_bid = listing.current_bid

        if not placed_bid.isnumeric():
            # Store the error message in the session temporarily
            request.session["bid_message_error"] = "Invalid input. Please enter a valid number for your bid."
            return redirect("get_listing", id=listing.id)

        placed_bid = float(placed_bid)

        if placed_bid <= 0:
            # Store the error message in the session temporarily
            request.session["bid_message_error"] = "Your bid must be greater than zero."
            return redirect("get_listing", id=listing.id)

        if placed_bid > current_bid and placed_bid is not None:
            listing.current_bid = placed_bid
            listing.save()

            bid = Bid(bid=placed_bid, listing=listing, owner=request.user)
            bid.save()

            # Store the success message in the session temporarily
            request.session["bid_message_success"] = "Bid placed successfully."
            return redirect("get_listing", id=listing.id)
        else:
            # Store the error message in the session temporarily
            request.session["bid_message_error"] = (f"Your bid (${'{:.2f}'.format(placed_bid)}) must be higher than "
                                                    f"the current price ${'{:.2f}'.format(current_bid)}.")
            return redirect("get_listing", id=listing.id)

    return redirect("get_listing", id=listing.id)


@login_required(login_url="/login")
def delete_bid(request, listing_id, bid_id):
    user = request.user

    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        bid = Bid.objects.get(pk=bid_id, listing=listing.id)
        is_bid_owner = user.id == bid.owner.id

        if is_bid_owner:
            bid.delete()
            if listing.bids.count() > 0:
                previous_price = listing.bids.last().bid
                listing.current_bid = previous_price
                listing.save()
            else:
                listing.current_bid = listing.starting_price
                listing.save()

            # Store the success message in the session temporarily
            request.session["bid_message_success"] = "Bid retracted successfully."
            return redirect("get_listing", id=listing.id)


@login_required(login_url="/login")
def close_listing(request, id):
    listing = Listing.objects.get(pk=id)
    is_owner = request.user.id == listing.owner.id

    if request.method == "POST":
        if is_owner and listing.is_active:
            listing.is_active = False
            listing.save()

            return redirect("get_listing", id=listing.id)
    return render(request, "auctions/listing.html")


@login_required(login_url="/login")
def add_comment(request, id):
    listing = Listing.objects.get(pk=id)
    user = request.user

    if request.method == "POST":
        comment_content = request.POST["content"]

        if len(comment_content) <= 0:
            # Store the error message in the session temporarily
            request.session["comment_message_error"] = "Comment must be longer than zero."
            return redirect("get_listing", id=listing.id)

        if len(comment_content) > 1000:
            # Store the error message in the session temporarily
            request.session["comment_message_error"] = "Comment must be not longer than 1000 characters."
            return redirect("get_listing", id=listing.id)

        if 0 < len(comment_content) <= 1000 and comment_content is not None:
            added_comment = Comment.objects.create(author=user, listing=listing, content=comment_content)
            added_comment.save()
            listing.comments.add(added_comment)
            listing.save()

            # Store the success message in the session temporarily
            request.session["comment_message_success"] = "Comment placed successfully."
            return redirect("get_listing", id=listing.id)


@login_required(login_url="/login")
def delete_comment(request, listing_id, comment_id):
    user = request.user
    listing = Listing.objects.get(pk=listing_id)
    comment = Comment.objects.get(pk=comment_id, listing=listing_id)
    is_comment_owner = user.id == comment.author.id

    if request.method == "POST":
        if is_comment_owner is True:
            comment.delete()

            # Store the success message in the session temporarily
            request.session["comments_list_message_success"] = "Comment deleted successfully."
            return redirect("get_listing", id=listing.id)
