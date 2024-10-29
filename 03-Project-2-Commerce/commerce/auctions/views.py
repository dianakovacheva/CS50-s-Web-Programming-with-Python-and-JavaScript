from urllib.parse import urlparse

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
        price = request.POST["price"]
        image_URL = request.POST["image_URL"]
        category_ids = request.POST.getlist("category")

        if not Listing.objects.filter(title=title).exists():
            created_listing = Listing.objects.create(title=title, description=description,
                                                     price=price,
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
    active_listings_in_category = Listing.objects.filter(category=category.id)

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
    current_bid = placed_bids.last()
    username_current_bid = ""
    is_current_bid_owner = False

    if placed_bids:
        username_current_bid = User.objects.filter(id=current_bid.owner_id)[0]
        if request.user.id == current_bid.owner_id:
            is_current_bid_owner = True

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "is_listing_owner": is_listing_owner,
        "placed_bids": placed_bids,
        "is_current_bid_owner": is_current_bid_owner,
        "username_current_bid": username_current_bid
    })


@login_required(login_url="/login")
def get_watchlist(request):
    return render(request, "auctions/watchlist.html")


@login_required(login_url="/login")
def add_to_watchlist(request, id):
    user = request.user
    listing = Listing.objects.get(pk=id)

    if user in listing.watchlist.all():
        # Remove from watchlist if it's already there
        listing.watchlist.remove(user)
    else:
        listing.watchlist.add(user)

    return redirect('get_listing', id=listing.id)


@login_required(login_url="/login")
def place_bid(request, id):
    listing = Listing.objects.get(pk=id)

    if request.method == "POST" and listing.is_active:
        placed_bid = float(request.POST["bid"])
        price = listing.price

        try:
            placed_bid = float(placed_bid)
        except ValueError:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "bid_message": "Invalid input. Please enter a valid number for your bid.",
            })

        if placed_bid <= 0:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "bid_message": "Your bid must be greater than zero.",
            })

        if placed_bid > price and placed_bid is not None:
            listing.price = placed_bid
            listing.save()

            bid = Bid(bid=placed_bid, listing=listing, owner=request.user)
            bid.save()

            return redirect("get_listing", id=listing.id)
        else:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "bid_message": f"Your bid (${'{:.2f}'.format(placed_bid)}) must be higher than the current price ${'{:.2f}'.format(price)}."
            })

    return redirect('get_listing', id=listing.id)


@login_required(login_url="/login")
def delete_bid(request, listing_id, bid_id):
    user = request.user

    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        bid = Bid.objects.get(pk=bid_id, listing=listing.id)

        if user.id == bid.owner.id:
            bid.delete()
            previous_price = listing.bids.last().bid
            listing.price = previous_price
            listing.save()

            return redirect("get_listing", id=listing.id)


def close_listing(request, id):
    listing = Listing.objects.get(pk=id)
    is_owner = request.user.id == listing.owner.id

    if request.method == "POST":
        if is_owner and listing.is_active:
            listing.is_active = False
            listing.save()

            return redirect("get_listing", id=listing.id)
    return render(request, "auctions/listing.html")
