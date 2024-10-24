from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Purchase, Usage


# Signal to track the previous state before an update (for Purchase)
@receiver(pre_save, sender=Purchase)
def track_old_purchase_quantity(sender, instance, **kwargs):
    if instance.pk:
        old_instance = Purchase.objects.get(pk=instance.pk)
        instance._old_quantity = old_instance.quantity
    else:
        instance._old_quantity = 0


# Signal to track the previous state before an update (for Usage)
@receiver(pre_save, sender=Usage)
def track_old_usage_quantity(sender, instance, **kwargs):
    if instance.pk:
        old_instance = Usage.objects.get(pk=instance.pk)
        instance._old_quantity = old_instance.used_quantity
    else:
        instance._old_quantity = 0


# Signal to update item quantity when a purchase is made or updated
@receiver(post_save, sender=Purchase)
def update_item_quantity_on_purchase(sender, instance, created, **kwargs):
    if created:
        # New purchase: Add quantity to item
        instance.item.curr_quantity += instance.quantity
    else:
        # Updated purchase: Adjust the quantity difference
        quantity_difference = instance.quantity - instance._old_quantity
        instance.item.curr_quantity += quantity_difference
    instance.item.save()


# Signal to update item quantity when an item is used or updated
@receiver(post_save, sender=Usage)
def update_item_quantity_on_usage(sender, instance, created, **kwargs):
    if created:
        # New usage: Subtract used quantity from item
        if instance.item.curr_quantity >= instance.used_quantity:
            instance.item.curr_quantity -= instance.used_quantity
        else:
            raise ValueError(f"Insufficient quantity of {instance.item.name} to use")
    else:
        # Updated usage: Adjust the quantity difference
        quantity_difference = instance.used_quantity - instance._old_quantity
        if instance.item.curr_quantity >= quantity_difference:
            instance.item.curr_quantity -= quantity_difference
        else:
            raise ValueError(f"Insufficient quantity of {instance.item.name} to use the updated amount")

    instance.item.save()


# Handle purchase deletions
@receiver(post_delete, sender=Purchase)
def restore_item_quantity_on_purchase_delete(sender, instance, **kwargs):
    instance.item.curr_quantity -= instance.quantity
    instance.item.save()


# Handle usage deletions
@receiver(post_delete, sender=Usage)
def restore_item_quantity_on_usage_delete(sender, instance, **kwargs):
    instance.item.curr_quantity += instance.used_quantity
    instance.item.save()
    