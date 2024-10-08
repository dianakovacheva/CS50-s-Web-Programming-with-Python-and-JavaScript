from django.urls import path

from . import views

app_name = "encyclopedia"
urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/new_entry", views.new_entry, name="new_entry"),
    path("wiki/random", views.get_random, name="get_random"),
    path("wiki/search", views.search_entry, name="q"),
    path("wiki/<str:entry>", views.get_entry, name="entry"),
    path("wiki/<str:title>/edit_entry", views.edit_entry, name="edit_entry"),
]
