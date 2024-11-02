from django.urls import path
from . import views

app_name = 'SmartGhrWali'
urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("purchases/", views.purchases, name="purchases"),
    path("purchases/<int:purchase_id>/delete/", views.delete_purchase, name="delete_purchase"),
    path("usages/", views.usages, name="usages"),
    path("usages/<int:usage_id>/delete/", views.delete_usage, name="delete_usage"),
    path("recipes/", views.recipe_page, name="recipe_page"),
    path("recipes/fetch_recipes/", views.fetch_recipes, name="fetch_recipes"),
    path("register/", views.register, name="register"),
    path("reports/monthly-expense/", views.monthly_expense_report, name='monthly_expense_report'),
    # path("<int:item_id>/edit/", views.edit_item, name="edit_item"),
    # path("<int:item_id>/delete/", views.delete_item, name="delete_item"),
    # path("", views.index, name="index"),
    # path("", views.index, name="index"),
]
