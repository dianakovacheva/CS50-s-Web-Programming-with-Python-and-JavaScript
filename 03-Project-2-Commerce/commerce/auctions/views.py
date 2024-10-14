from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
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
            "message": "No listings to show"
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
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
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


def create_listing(request):
    categories = Category.objects.all()

    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        price = request.POST["price"]
        image_URL = request.POST["image_URL"]
        category = request.POST.getlist("category")

        try:
            if not Listing.objects.filter(title=title).exists():
                created_listing = Listing.objects.create(title=title, description=description, price=price, image_URL=image_URL, owner=request.user)
                created_listing.category.set(category)
                created_listing.save()

                return redirect("listing", id=created_listing.id)
        except IntegrityError:
            return render(request, "auctions/create_listing.html", {
                "message": "Listing already exists."
            })
    # If GET request, render the form
    return render(request, "auctions/create_listing.html", {
        "categories": categories
    })


def get_categories(request):
    pass


def listing(request, id):
    listing = Listing.objects.get(pk=id)

    return render(request, "auctions/listing.html", {
        "listing": listing
    })
