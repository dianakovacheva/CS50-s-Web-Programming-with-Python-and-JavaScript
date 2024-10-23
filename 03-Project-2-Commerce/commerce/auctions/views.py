from urllib.parse import urlparse

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, is_valid_path
from django import forms

from .models import User, Listing, Bid, Comment, Category


def index(request):
    try:
        listings = Listing.objects.all()

        if listings:
            return render(request, "auctions/index.html", {
                "listings": listings
            })
    except IntegrityError:
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
            user = User.objects.create_xuser(username, email, password)
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

    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        price = request.POST["price"]
        image_URL = request.POST["image_URL"]
        category_ids = request.POST.getlist("category")

        try:
            if not Listing.objects.filter(title=title).exists():
                created_listing = Listing.objects.create(title=title, description=description, price=price,
                                                         image_URL=image_URL, owner=request.user)

                # Convert category_ids (strings) to a list of Category instances
                category_objects = Category.objects.filter(id__in=category_ids)
                created_listing.category.set(category_objects)
                created_listing.save()

                return redirect("get_listing", id=created_listing.id)
        except IntegrityError:
            return render(request, "auctions/create_listing.html", {
                "message": "Listing already exists."
            })
    # If GET request, render the form
    return render(request, "auctions/create_listing.html", {
        "categories": categories
    })


def get_categories(request):
    categories = Category.objects.all()

    if categories is not None and len(categories) > 0:

        return render(request, "auctions/categories.html", {
            "categories": categories
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
    listing = Listing.objects.get(pk=id)

    if request.method == "POST":
        placed_bid = int(request.POST["bid"])
        listing_starting_bid = int(listing.starting_bid)

        is_bigger = False

@login_required(login_url="/login")
def place_bid(request, id):
    return render(request, "auctions/listing.html", {
        "bid": 0
    })


@login_required(login_url="/login")
def get_watchlist(request):
    user = request.user

    # Get user's watchlist data
    watchlist = request.user.watchlist.all()

    if len(watchlist) > 0:
        return render(request, "auctions/watchlist.html", {
            "watchlist": watchlist
        })
    else:
        return render(request, "auctions/watchlist.html", {
            "message": "Watchlist is empty."
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

    return redirect('get_listing', id=listing.id)
