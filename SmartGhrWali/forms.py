from inflect import engine
from django import forms
from django.utils.safestring import mark_safe
from .models import Item, Category, Purchase, Usage

# class ItemForm(forms.ModelForm):
#     class Meta:
#         model = Item
#         fields = ['name', 'category', 'curr_quantity', 'min_quantity']

# class PurchaseForm(forms.ModelForm):
#     class Meta:
#         model = Purchase
#         fields = ['item', 'purchased_on', 'quantity', 'unit_price']
    
class PurchaseForm(forms.ModelForm):
    # Single field for item name
    item_name = forms.CharField(max_length=70, required=True, help_text="Enter or select the item name")

    # Additional fields that should only appear if the item is new
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
    min_quantity = forms.IntegerField(required=False)
    expiry_date = forms.DateField(required=False, help_text="Optional", widget=forms.SelectDateWidget)

    class Meta:
        model = Purchase
        fields = ['item_name', 'purchased_on', 'quantity', 'unit_price']

    def clean(self):
        cleaned_data = super().clean()
        item_name = cleaned_data.get('item_name')

        # Check if the item already exists
        try:
            p = engine()
            singular_item_name = p.singular_noun(item_name) or item_name    # convert item name to singular
            item = Item.objects.get(name=singular_item_name)
            self.cleaned_data['item'] = item
        except Item.DoesNotExist:
            # If the item doesn't exist, ensure the user provides additional fields for the new item
            if not cleaned_data.get('category'):
                raise forms.ValidationError(mark_safe(
                    f"This is a new item. Please provide the additional details for <strong>{item_name}</strong>."))
            
            # Ensure other fields for a new item are filled out
            if not cleaned_data.get('min_quantity'):
                raise forms.ValidationError("Please provide a minimum quantity for the new item.")
            
            # Mark the form to save the new item later
            self.cleaned_data['new_item'] = True

        return cleaned_data

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('new_item'):
            # Save the new item first
            new_item = Item.objects.create(
                name=cleaned_data['item_name'],
                category=cleaned_data['category'],
                curr_quantity=cleaned_data['quantity'],  # Set the current quantity to the purchased quantity
                min_quantity=cleaned_data['min_quantity'],
                expiry_date=cleaned_data.get('expiry_date')
            )
            # Add the new item to the purchase
            self.instance.item = new_item
        else:
            # If the item exists, use it for the purchase
            self.instance.item = cleaned_data['item']

        # Finally save the purchase
        return super().save(commit=commit)
    
class UsageForm(forms.ModelForm):
    class Meta:
        model = Usage
        fields = ['item', 'used_quantity']
