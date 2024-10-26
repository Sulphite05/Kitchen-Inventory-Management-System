from inflect import engine
from django import forms
from django.utils.safestring import mark_safe
from .models import Item, Category, Purchase, Usage
from django.utils.timezone import now

CATEGORY_ERROR = ""
    
class PurchaseForm(forms.ModelForm):

    item_name = forms.CharField(max_length=70, required=True)
    quantity = forms.DecimalField(required=True, label="Quantity", initial="0.25", min_value=0.01)
    purchased_on = forms.DateField(required=True, widget=forms.SelectDateWidget, initial=now().date()) 

    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
    min_quantity = forms.DecimalField(required=False, label="Minimum Quantity", initial="0.25", min_value=0)
    expiry_date = forms.DateField(required=False, help_text="Optional", widget=forms.SelectDateWidget) 
   

    class Meta:
        model = Purchase
        fields = ['item_name', 'quantity', 'unit_price', 'purchased_on']
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        item_name = cleaned_data.get('item_name')

        # Check if the item already exists
        try:
            p = engine()
            singular_item_name = p.singular_noun(item_name) or item_name    # convert item name to singular
            self.cleaned_data['item_name'] = singular_item_name
            self.cleaned_data['item'] = Item.objects.get(user = self.user, name=singular_item_name) # this line will throw error if the item does not exist for the user
        
        except Item.DoesNotExist:
            # If the item doesn't exist, ensure the user provides additional fields for the new item
            if not cleaned_data.get('category'):
                self.add_error('category', "This is a new item. Please provide the category.")
            
            # Mark the form to save the new item later
            self.cleaned_data['new_item'] = True
            self.cleaned_data['item_name'] = singular_item_name

        return cleaned_data

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('new_item'):
            # Save the new item first
            new_item = Item.objects.create(
                user=self.user,
                name=cleaned_data['item_name'],
                category=cleaned_data['category'],
                curr_quantity=cleaned_data['quantity'],  # Set the current quantity to the purchased quantity
                min_quantity=cleaned_data['min_quantity'],
                expiry_date=cleaned_data.get('expiry_date')
            )
            # Add the new item to the purchase
            self.instance.item = new_item
        else:
            # If the item exists, update it
            item = self.cleaned_data["item"]
            item.category = self.cleaned_data["category"] or item.category
            item.min_quantity = self.cleaned_data["min_quantity"] or item.min_quantity
            item.expiry_date = self.cleaned_data.get("expiry_date") or item.expiry_date
            item.curr_quantity += self.cleaned_data["quantity"]  # Update quantity by adding the purchased amount
            item.save()
            self.instance.item = item
        # Finally save the purchase
        return super().save(commit=commit)
    
class UsageForm(forms.ModelForm):
    class Meta:
        model = Usage
        fields = ['item', 'used_quantity']

