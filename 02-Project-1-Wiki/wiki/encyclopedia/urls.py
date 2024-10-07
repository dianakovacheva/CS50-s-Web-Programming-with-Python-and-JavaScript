from django.urls import path, include

from . import views


app_name = "encyclopedia"
urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:entry>", views.get_entry, name="entry"),
    path("new_entry", views.new_entry, name="new_entry"),
]
