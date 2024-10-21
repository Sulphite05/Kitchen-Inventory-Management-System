from django.urls import path
from . import views

urlpatterns = [
    # path("", views.index, name="index"),
    path("", views.dashboard, name="dashboard"),
    path("create/", views.create_item, name="create_item"),
    path("<int:item_id>/edit/", views.edit_item, name="edit_item"),
    path("<int:item_id>/delete/", views.delete_item, name="delete_item"),
    # path("", views.index, name="index"),
    # path("", views.index, name="index"),
]
