import requests
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, Category, Purchase, Usage
from django.utils.timezone import timedelta, now, datetime
from.forms import PurchaseForm, UsageForm, UserRegistrationForm
from django.db.models import Prefetch, Avg, Sum, F
from django.contrib import messages
from django.contrib.auth import login
from django.db.models.functions import TruncMonth
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


def get_available_months():
    purchase_months = Purchase.objects.annotate(month=TruncMonth('purchased_on')).values('month').distinct()
    usage_months = Usage.objects.annotate(month=TruncMonth('used_on')).values('month').distinct()
    # Combine and deduplicate months from purchases and usages
    months = {month['month'].strftime("%Y-%m") for month in list(purchase_months) + list(usage_months)}
    # Convert to sorted list of (month, year) tuples
    return sorted([(datetime.strptime(m, "%Y-%m").month, datetime.strptime(m, "%Y-%m").year) for m in months], reverse=True)

@login_required
def report_download_page(request):
    available_months = get_available_months()
    # For form month and year options
    months = [{'value': i, 'label': datetime(2023, i, 1).strftime('%B')} for i in range(1, 13)]
    years = range(datetime.now().year - 5, datetime.now().year + 1)
    return render(request, 'reports/monthly_inventory.html', {'available_months': available_months, 'months': months, 'years': years})

@login_required
def monthly_inventory_report(request):
    if request.GET.get('format') == 'pdf':
        month = int(request.GET.get('month'))
        year = int(request.GET.get('year'))
        purchases = Purchase.objects.filter(
            user=request.user, purchased_on__year=year, purchased_on__month=month
        ).annotate(total_price=F('quantity') * F('unit_price'))
        usages = Usage.objects.filter(
            user=request.user, used_on__year=year, used_on__month=month
        )
        total_purchase_cost = purchases.aggregate(Sum('total_price'))['total_price__sum'] or 0
        total_purchased_qty = purchases.aggregate(total_qty=Sum('quantity'))['total_qty'] or 0
        total_usage_quantity = usages.aggregate(total_qty=Sum('used_quantity'))['total_qty'] or 0
        net_change = total_purchased_qty - total_usage_quantity
        most_purchased = purchases.values('item__name').annotate(total_qty=Sum('quantity')).order_by('-total_qty').first()
        most_purchased_item_name = most_purchased['item__name'] if most_purchased else 'N/A'
        most_purchased_item_quantity = most_purchased['total_qty'] if most_purchased else 0
        most_used = usages.values('item__name').annotate(total_qty=Sum('used_quantity')).order_by('-total_qty').first()
        most_used_item_name = most_used['item__name'] if most_used else 'N/A'
        most_used_item_quantity = most_used['total_qty'] if most_used else 0
        average_purchase_cost_per_item = purchases.aggregate(avg_cost=Avg('total_price'))['avg_cost'] or 0
        total_unique_items_purchased = purchases.values('item').distinct().count()
        total_unique_items_used = usages.values('item').distinct().count()

        data = {
            'headers': [['Date', 'Item', 'Quantity', 'Unit Price', 'Total Cost'], ['Date', 'Item', 'Quantity Used']],
            'rows': [[(p.purchased_on.strftime("%Y-%m-%d"), p.item.name, str(p.quantity)+f' {p.item.category.unit}', 'Rs. '+str(p.unit_price), 'Rs. '+str(p.total_price)) for p in purchases],
                     [(u.used_on.strftime("%Y-%m-%d"), u.item.name, str(u.used_quantity)+f' {u.item.category.unit}') for u in usages]]
        }
        summary = {
            'total_purchase_cost': total_purchase_cost,  # Sum of all purchases
            'total_purchase_quantity': total_purchased_qty,
            'total_usage_quantity': total_usage_quantity,  # Sum of all quantities used
            'net_change': net_change,  # Purchased quantity - used quantity
            'most_purchased_item': {'name': most_purchased_item_name, 'quantity': most_purchased_item_quantity},
            'most_used_item': {'name': most_used_item_name, 'quantity': most_used_item_quantity},
            'average_purchase_cost_per_item': average_purchase_cost_per_item,  # Average cost of each purchase
            'total_unique_items_purchased': total_unique_items_purchased,
            'total_unique_items_used': total_unique_items_used
        }
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Inventory_Report_{year}_{month}.pdf"'
        generate_pdf(response, "Monthly Inventory Report", data, summary)
        return response

    return HttpResponse("Only PDF download is available for this report.")

# TODO: Allow AI category assignment
# TODO: Forward misc items info to front-end