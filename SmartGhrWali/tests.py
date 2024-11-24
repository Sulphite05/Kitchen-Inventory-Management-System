from django.test import TestCase
from .models import Category, Item, Purchase, Usage
from django.contrib.auth.models import User
from datetime import date

class ModelsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = Category.objects.create(name='Vegetables', unit='kg')
        self.item = Item.objects.create(
            name='Tomato',
            user=self.user,
            category=self.category,
            curr_quantity=5,
            expiry_date=date(2024, 12, 31)
        )
        self.purchase = Purchase.objects.create(
            user=self.user,
            item=self.item,
            purchased_on=date(2024, 10, 1),
            quantity=3,
            unit_price=15.0
        )
        self.usage = Usage.objects.create(
            user=self.user,
            item=self.item,
            used_on=date(2024, 10, 5),
            used_quantity=2
        )

    def test_item_creation(self):
        self.assertEqual(Item.objects.count(), 1)
        self.assertEqual(self.item.name, 'Tomato')
        self.assertEqual(self.item.curr_quantity, 6)

    def test_purchase_updates_item_quantity(self):
        self.item.curr_quantity += self.purchase.quantity
        self.item.save()
        self.assertEqual(self.item.curr_quantity, 9)

    def test_usage_updates_item_quantity(self):
        self.item.curr_quantity -= self.usage.used_quantity
        self.item.save()
        self.assertEqual(self.item.curr_quantity, 4)

    def test_category_relationship(self):
        self.assertEqual(self.item.category.name, 'Vegetables')