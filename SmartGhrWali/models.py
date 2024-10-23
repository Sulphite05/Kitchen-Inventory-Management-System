from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=70)
    unit = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name}({self.unit})"


class Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=70, unique=True, blank=False, null=False)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)  # Protect category from deletion
    curr_quantity = models.IntegerField(blank=False, null=False)
    min_quantity = models.IntegerField(blank=False, null=False)
    # created_at = models.DateTimeField(auto_now_add=True)  # Automatically set the field when the object is created
    # updated_at = models.DateTimeField(auto_now=True)      # Automatically update the field every time the object is saved

    def __str__(self):
        return self.name


class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)  
    purchased_on = models.DateTimeField(blank=False, null=False)
    quantity = models.IntegerField(blank=False, null=False)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0) 

    def __str__(self):
        return f"{self.item.name} - {self.quantity} units"


class Usage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.PROTECT) 
    used_on = models.DateTimeField() 
    used_quantity = models.IntegerField(blank=False, null=False)

    def __str__(self):
        return f"{self.item.name} - {self.used_quantity} units used"
