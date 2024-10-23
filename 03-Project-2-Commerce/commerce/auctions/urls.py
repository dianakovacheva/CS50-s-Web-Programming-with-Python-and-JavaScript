from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing/<int:id>", views.get_listing, name="get_listing"),
    path("listing/<int:id>/add_to_watchlist", views.add_to_watchlist, name="add_to_watchlist"),
    path("categories", views.get_categories, name="categories"),
    path("categories/<int:id>", views.get_category, name="category"),
    path("watchlist", views.get_watchlist, name="get_watchlist"),

]
