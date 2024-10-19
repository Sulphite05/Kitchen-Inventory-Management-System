from django import forms
from .models import Item, Purchase, Usage

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'category', 'curr_quantity', 'min_quantity']

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['item', 'purchased_on', 'quantity', 'unit_price']

class UsageForm(forms.ModelForm):
    class Meta:
        model = Usage
        fields = ['item', 'used_quantity', 'curr_quantity', 'min_quantity']
