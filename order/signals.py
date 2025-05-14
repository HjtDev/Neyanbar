from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Order
from main.utilities import send_sms


@receiver(pre_save, sender=Order)
def status_signal(sender, instance, *args, **kwargs):
    if not instance.pk:
        send_sms(instance.phone, f'Your order with the id: {instance.order_id} has been submitted')
        return

    old_status = Order.objects.get(pk=instance.pk).status
    status = instance.status
    if status != old_status:

        if status == Order.StatusChoices.PENDING:
            send_sms(instance.user.phone, 'Thanks for your payment we will ready your order soon!')
            return

        if status == Order.StatusChoices.CONFIRMED:
            send_sms(instance.user.phone, 'Your order has been confirmed. and will be sent to you on the due date')
            return

        if status == Order.StatusChoices.IN_PROGRESS:
            send_sms(instance.user.phone, 'Your order is in progress. and will be sent to you on the due date')
            return

        if status == Order.StatusChoices.READY_TO_SHIP:
            send_sms(instance.user.phone, 'Your order is ready to ship')
            return

        if status == Order.StatusChoices.SHIPPED:
            send_sms(instance.user.phone, 'Your order has been shipped.')
            return

        if status == Order.StatusChoices.FINISHED:
            send_sms(instance.user.phone, 'Thanks for your purchase enjoy your product')
            return

        if status == Order.StatusChoices.REJECTED:
            send_sms(instance.user.phone, 'Your order has been rejected if there is an issue please contact support')