from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("create_listing/", views.create_listing, name="create_listing"),
    path("listing/<int:id>/", views.get_listing, name="get_listing"),
    path("listing/<int:id>/place_bid/", views.place_bid, name="place_bid"),
    path("listing/<int:listing_id>/delete_bid/<int:bid_id>/", views.delete_bid, name="delete_bid"),
    path("listing/<int:id>/close_listing/", views.close_listing, name="close_listing"),
    path("listing/<int:id>/add_comment/", views.add_comment, name="add_comment"),
    path("categories/", views.get_categories, name="categories"),
    path("categories/<int:id>/", views.get_category, name="category"),
    path("listing/<int:id>/add_to_watchlist/", views.add_to_watchlist, name="add_to_watchlist"),
    path("watchlist/", views.get_watchlist, name="get_watchlist"),
]
