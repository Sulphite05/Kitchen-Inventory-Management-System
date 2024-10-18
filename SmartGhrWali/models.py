from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # if I delete the user, their item(s) will also get deleted
    text = models.CharField(max_length=70)
    price = models.IntegerField(blank=False, null=False)
    createdAt = models.DateTimeField(auto_now_add=True) # only runs when added
    updatedAt = models.DateTimeField(auto_now=True)     # runs as soon as updated

