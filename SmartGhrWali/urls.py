from django.urls import path
from . import views

urlpatterns = [
    # path("", views.index, name="index"),
    path("", views.dashboard, name="dashboard"),
    path("purchases", views.purchases, name="purchases"),
    path("purchases/<int:purchase_id>/delete/", views.delete_purchase, name="delete_purchase"),
    # path("<int:item_id>/edit/", views.edit_item, name="edit_item"),
    # path("<int:item_id>/delete/", views.delete_item, name="delete_item"),
    # path("", views.index, name="index"),
    # path("", views.index, name="index"),
]
