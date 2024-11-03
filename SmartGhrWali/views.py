import requests
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, Category, Purchase, Usage
from django.utils.timezone import timedelta, now
from.forms import PurchaseForm, UsageForm, UserRegistrationForm
from django.db.models import Prefetch, Sum, F, Q
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .utils import generate_pdf
import logging


def index(request):
    return render(request, 'index.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request, user)
            return redirect('SmartGhrWali:dashboard')

    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    categories = Category.objects.prefetch_related(Prefetch('item_set', queryset=Item.objects.filter(user=request.user)))
    return render(request, 'dashboard.html', {'categories': categories})

@login_required
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
            messages.success(request, 'Purchase has been added successfully!')
            return redirect('purchases')  
    else:
        form = PurchaseForm()

    context = {
        'form': form,
        'purchases': purchases,
    }
    
    return render(request, 'purchases.html', context)

@login_required
def delete_purchase(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id, user=request.user)
    purchase.delete()
    messages.success(request, 'Purchase has been deleted successfully!')
    return redirect('purchases')

@login_required
def usages(request):
    today = now().date()
    # Fetch purchases made by the current user in the last 30 days
    usages = Usage.objects.filter(user=request.user,used_on__gte=today - timedelta(days=30)).order_by('-used_on')

    if request.method == 'POST':
        form = UsageForm(request.POST)
        if form.is_valid():
            usage = form.save(commit=False)
            usage.user = request.user 
            usage.save()
            messages.success(request, 'Usage has been added successfully!')
            return redirect('usages')
    else:
        form = UsageForm()

    context = {
        'form': form,
        'usages': usages,
    }
    
    return render(request, 'usages.html', context)

@login_required
def delete_usage(request, usage_id):
    usage = get_object_or_404(Usage, id=usage_id, user=request.user)
    usage.delete()
    messages.success(request, 'Usage has been deleted successfully!')
    return redirect('usages')


@login_required
def recipe_page(request):
    return render(request, "recipes.html")



logger = logging.getLogger(__name__)

@login_required
def fetch_recipes(request):
    if request.method == "POST":
        selected_item_ids = request.POST.getlist("selected_items")

        # Check if any items were selected
        if not selected_item_ids:
            return render(request, "recipes.html", {"error": "No ingredients selected."})

        ingredients = ",".join(
            item.name for item in Item.objects.filter(id__in=selected_item_ids)
        )

        url = "https://api.edamam.com/search"

        try:
            response = requests.get(
                url,
                params={
                    "q": ingredients,
                    "app_id": settings.EDAMAM_APP_ID,
                    "app_key": settings.EDAMAM_APP_KEY,
                    "from": 0,
                    "to": 5, 
                },
            )
            response.raise_for_status()  
            data = response.json()

            # Handle cases where the data structure might not be as expected
            recipes = [
                {
                    "title": recipe["recipe"].get("label", "No Title"),
                    "ingredients": ", ".join([ing["food"] for ing in recipe["recipe"].get("ingredients", [])]),
                    "link": recipe["recipe"].get("url", "#"),
                }
                for recipe in data.get("hits", [])
            ]
            return render(request, "recipes.html", {"recipes": recipes})

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching recipes: {e}")
            return render(request, "recipes.html", {"error": "Failed to fetch recipes."})

    return redirect('SmartGhrWali:dashboard') 

@login_required
def monthly_expense_report(request):
    # Query purchases and calculate total per month
    expenses = Purchase.objects.filter(user=request.user).annotate(total_price=F('quantity') * F('unit_price')).order_by('purchased_on')
    data = {
        'headers': ['Date', 'Item', 'Quantity', 'Unit Price', 'Total Price'],
        'rows': [(e.purchased_on, e.item.name, e.quantity, e.unit_price, e.total_price) for e in expenses],
    }

    if request.GET.get('format') == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Monthly_Expense_Report.pdf"'
        generate_pdf(response, "Monthly Expense Report", data)
        return response

    # Otherwise render HTML template
    return render(request, 'reports/monthly_expense.html', {'expenses': expenses})

@login_required
def monthly_inventory_report(request):
    month = now().month - 1
    year = now().year
    purchases = Purchase.objects.filter(
        user=request.user, purchased_on__year=year, purchased_on__month=month
    ).annotate(total_price=F('quantity') * F('unit_price'))

    usages = Usage.objects.filter(
        user=request.user, used_on__year=year, used_on__month=month
    )

    total_purchase_cost = purchases.aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_usage_quantity = usages.aggregate(Sum('used_quantity'))['used_quantity__sum'] or 0
    net_change = total_purchase_cost - total_usage_quantity

    if request.GET.get('format') == 'pdf':
        data = {
        'headers': [['Date', 'Item', 'Quantity', 'Unit Price', 'Total Cost'], ['Date', 'Item', 'Quantity Used']],
        'rows': [[(p.purchased_on.strftime("%Y-%m-%d"), p.item.name, p.quantity, p.unit_price, p.total_price) for p in purchases],
                 [(u.used_on.strftime("%Y-%m-%d"), u.item.name, u.used_quantity) for u in usages]]}
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Monthly_Expense_Report.pdf"'
        generate_pdf(response, "Monthly Inventory Report", data)
        return response

    context = {
        'report_month': month,
        'report_year': year,
        'purchases': purchases,
        'usages': usages,
        'total_purchase_cost': total_purchase_cost,
        'total_usage_quantity': total_usage_quantity,
        'net_change': net_change,
    }
    return render(request, 'reports/monthly_inventory.html', context)

# TODO: Add Report functionality
# TODO: Allow AI category assignment
# TODO: Forward misc items info to front-end