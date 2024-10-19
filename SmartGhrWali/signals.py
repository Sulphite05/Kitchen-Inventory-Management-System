from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Purchase, Usage


# Signal to update current quantity when a purchase is made
@receiver(post_save, sender=Purchase)
def update_item_quantity_on_purchase(sender, instance, created, **kwargs):
    if created:
        instance.item.curr_quantity += instance.quantity
        instance.item.save()

# Signal to update current quantity when an item is used
@receiver(post_save, sender=Usage)
def update_item_quantity_on_usage(sender, instance, created, **kwargs):
    if created:
        if instance.item.curr_quantity >= instance.used_quantity:
            instance.item.curr_quantity -= instance.used_quantity
            instance.item.save()
        else:
            raise ValueError(f"Insufficient quantity of {instance.item.name} to use")

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
    