from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # many-to-many relation with AuctionListing
    owned_auctions = models.ManyToManyField("Listing", blank=True, related_name="auctions_list")

    def __str__(self):
        return f"{self.username} {self.first_name} {self.last_name}"


class Listing(models.Model):
    title = models.CharField(max_length=64, unique=True, help_text="Enter title")
    description = models.TextField(max_length=1000, help_text="Enter a brief description of the auction")
    image_URL = models.URLField(max_length=200, help_text="Add image URL")
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_bid = models.DecimalField(max_digits=10, decimal_places=2)
    # foreign key User
    owner = models.ForeignKey("User", on_delete=models.CASCADE, related_name="auction_owner")
    # many-to-many relation with AuctionCategory
    category = models.ManyToManyField("Category", help_text="Select a category", related_name="categories")
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    # foreign key Comment
    comments = models.ManyToManyField("Comment", blank=True, related_name="auction_comments")
    watchlist = models.ManyToManyField("User", blank=True, related_name="watchlist")

    def __str__(self):
        return f"{self.title}"


class Bid(models.Model):
    bid = models.DecimalField(max_digits=10, decimal_places=2)
    # foreign key AuctionListing
    listing = models.ForeignKey("Listing", on_delete=models.CASCADE, related_name="bids")
    # foreign key User
    owner = models.ForeignKey("User", on_delete=models.CASCADE, related_name="bids")
    is_valid = models.BooleanField(default=True)
    bid_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bid} {self.listing} {self.owner}"


class Comment(models.Model):
    # foreign key User
    author = models.ForeignKey("User", on_delete=models.CASCADE, related_name="comment_author")
    # foreign key AuctionListing
    listing = models.ForeignKey("Listing", on_delete=models.CASCADE, related_name="auction_listing")
    content = models.TextField(max_length=1000, help_text="Enter comment")
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author} {self.listing} {self.content} {self.pub_date}"


class Category(models.Model):
    AUCTION_CATEGORIES = (
        ("Fashion", "Fashion"),
        ("Toys", "Toys"),
        ("Electronics", "Electronics"),
        ("Home", "Home")
    )

    category = models.CharField(max_length=64, choices=AUCTION_CATEGORIES, blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f"{self.category}"
