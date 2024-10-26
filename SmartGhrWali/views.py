from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, Category, Purchase, Usage
from django.utils.timezone import timedelta, now
from.forms import PurchaseForm
from django.db.models import Prefetch
from django.contrib import messages
# Create your views here.

def index(request):
    return render(request, 'index.html')

def dashboard(request):
    categories = Category.objects.prefetch_related(Prefetch('item_set', queryset=Item.objects.filter(user=request.user)))
    return render(request, 'dashboard.html', {'categories': categories})

def purchases(request):
    today = now().date()
    # Fetch purchases made by the current user in the last 30 days
    purchases = Purchase.objects.filter(user=request.user,purchased_on__gte=today - timedelta(days=30)).order_by('-purchased_on')

    if request.method == 'POST':
        form = PurchaseForm(request.POST, user=request.user)
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.user = request.user  # Associate the purchase with the current user
            purchase.save()
            messages.success(request, 'Item has been added successfully!')
            return redirect('purchases')  # Redirect to a 'purchases' page or wherever you want
    else:
        form = PurchaseForm()

    context = {
        'form': form,
        'purchases': purchases,
    }
    
    return render(request, 'purchases.html', context)


# def create_item(request):
#     if request.method == "POST":
#         form  = ItemForm(request.POST, request.FILES) # gonna see the purpose of FILES
#         if form.is_valid():
#             item = form.save(commit=False) # commit is False, we don't wanna save it to database wihout user
#             item.user = request.user
#             item.save()
#             return redirect('dashboard')
#     else:
#         form = ItemForm()
#     return render(request, 'item_form.html', {'form': form})

# def edit_item(request, item_id):
#     item = get_object_or_404(Item, pk=item_id, user=request.user)
#     if request.method == "POST":
#         form  = ItemForm(request.POST, request.FILES, instance=item) # gonna see the purpose of FILES
#         if form.is_valid:
#             item = form.save(commit=False)
#             item.user = request.user
#             item.save()
#             return redirect("dashboard")
#     else:
#         form = ItemForm(instance=item) # previous instance
#     return render(request, 'item_form.html', {'form': form})

# def delete_item(request, item_id):
#     item = get_object_or_404(Item, pk=item_id, user=request.user)
#     if request.method == "POST":
#         item.delete()
#         return redirect("dashboard")
#     return render(request, 'item_confirm_delete.html', {'item': item})

# items shouldn't be deleted or edited by the user
# only manage purchases and usage