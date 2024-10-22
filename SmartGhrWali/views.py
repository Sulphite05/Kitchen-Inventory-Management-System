from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, Category, Purchase, Usage
from.forms import ItemForm, PurchaseForm, UsageForm
# Create your views here.

def index(request):
    return render(request, 'index.html')

def dashboard(request):
    items = Item.objects.filter(user=request.user).order_by('-curr_quantity')
    return render(request, 'dashboard.html', {'items': items})

def create_item(request):
    if request.method == "POST":
        form  = ItemForm(request.POST, request.FILES) # gonna see the purpose of FILES
        if form.is_valid():
            item = form.save(commit=False) # commit is False, we don't wanna save it to database wihout user
            item.user = request.user
            item.save()
            return redirect('dashboard')
    else:
        form = ItemForm()
    return render(request, 'item_form.html', {'form': form})

def edit_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id, user=request.user)
    if request.method == "POST":
        form  = ItemForm(request.POST, request.FILES, instance=item) # gonna see the purpose of FILES
        if form.is_valid:
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            return redirect("dashboard")
    else:
        form = ItemForm(instance=item) # previous instance
    return render(request, 'item_form.html', {'form': form})

def delete_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id, user=request.user)
    if request.method == "POST":
        item.delete()
        redirect("dashboard")
    return render(request, 'item_confirm_delete.html', {'item': item})

# items shouldn't be deleted or edited by the user
# only manage purchases and usage