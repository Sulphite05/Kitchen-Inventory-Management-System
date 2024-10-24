from inflect import engine
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

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
    min_quantity = models.DecimalField(blank=False, null=False, default=0.25, decimal_places=2, max_digits=10)
    expiry_date = models.DateField(blank=True, null=True)
    # created_at = models.DateTimeField(auto_now_add=True)  # Automatically set the field when the object is created
    # updated_at = models.DateTimeField(auto_now=True)      # Automatically update the field every time the object is saved

    def clean(self):
        p = engine()
        # Automatically convert name to singular if it's plural
        if p.singular_noun(self.name):  # If the word is detected as plural
            self.name = p.singular_noun(self.name)

    def __str__(self):
        return self.name


class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=False, blank=False)  
    purchased_on = models.DateField(default=now, null=False, blank=False) 
    quantity = models.IntegerField(blank=False, null=False)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0) 

    def __str__(self):
        return f"{self.item.name} - {self.quantity} units"


class Usage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.PROTECT, null=False, blank=False) 
    used_on = models.DateField(default=now, null=False, blank=False) 
    used_quantity = models.IntegerField(blank=False, null=False)

    def __str__(self):
        return f"{self.item.name} - {self.used_quantity} units used"
