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
    path("reports/inventory/", views.monthly_inventory_report, name='inventory_report'),
    path("reports/monthly-inventory/", views.report_download_page, name='monthly_inventory_report'),
]
