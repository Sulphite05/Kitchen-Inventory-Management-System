from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Item, Category, Purchase
from django.utils import timezone

class ItemModelTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Fruits', unit='kg')
        self.item = Item.objects.create(name='Apple', category=self.category, curr_quantity=10, min_quantity=5)

    def test_item_creation(self):
        item = Item.objects.get(name='Apple')
        self.assertEqual(item.name, 'Apple')
        self.assertEqual(item.category.name, 'Fruits')
        self.assertEqual(item.curr_quantity, 10)
        self.assertEqual(item.min_quantity, 5)

class PurchaseModelTestCase(TestCase):
    def setUp(self):
        self.item = Item.objects.create(name='Rice', category=self.category, curr_quantity=20, min_quantity=5)

    def test_purchase_creation(self):
        purchase = Purchase.objects.create(
            item=self.item,
            quantity=10,
            unit_price=50,
            purchased_on=timezone.now()
        )
        self.assertEqual(purchase.item.name, 'Rice')
        self.assertEqual(purchase.quantity, 10)
        self.assertEqual(purchase.unit_price, 50)
        self.assertIsInstance(purchase.purchased_on, timezone.datetime)

class RegistrationAndViewItemsIntegrationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.category = Category.objects.create(name='Vegetables', unit='kg')
        self.item = Item.objects.create(name='Carrot', category=self.category, curr_quantity=10, min_quantity=5)

    def test_registration_and_view_items(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('SmartGhrWali:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Carrot')
        self.assertContains(response, 'Vegetables')
        self.assertContains(response, 'Carrot')


class AddItemAndViewInDashboardIntegrationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.category = Category.objects.create(name='Dairy', unit='liters')

    def test_add_item_and_view_in_dashboard(self):
        self.client.login(username='testuser', password='password123')
        item_data = {
            'name': 'Milk',
            'category': self.category.id,
            'curr_quantity': 50,
            'min_quantity': 10,
        }
        response = self.client.post(reverse('SmartGhrWali:add_item'), item_data)
        self.assertRedirects(response, reverse('SmartGhrWali:dashboard'))
        response = self.client.get(reverse('SmartGhrWali:dashboard'))
        self.assertContains(response, 'Milk')
        self.assertContains(response, 'Dairy')
        self.assertContains(response, '50')
        self.assertContains(response, '10')