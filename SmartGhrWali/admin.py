from django.contrib import admin
from .models import Item, Category, Purchase, Usage


admin.site.register(Item)
admin.site.register(Category)
admin.site.register(Purchase)
admin.site.register(Usage)