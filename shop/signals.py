from django.dispatch.dispatcher import receiver
from django.db.models.signals import pre_save
from main.utilities import send_sms, PRODUCT_NOTIFY_ME
from shop.models import Product


@receiver(pre_save, sender=Product)
def notify_me(sender, instance: Product, *args, **kwargs):
    if not instance.pk:
        return

    old_inventory = Product.objects.get(pk=instance.pk).inventory

    if not old_inventory and instance.inventory and instance.remind_to.exists():
        remind_list = instance.remind_to.all()
        for user in remind_list:
            send_sms(user.phone, PRODUCT_NOTIFY_ME, user.name, instance.name)