from django.db.models.signals import pre_save
from django.dispatch import receiver

from main.templatetags.tags import to_jalali_verbose
from .models import Order
from main.utilities import send_sms, ORDER_SUBMITTED, ORDER_PAID, ORDER_CONFIRMED, ORDER_IN_PROGRESS, ORDER_SHIPPED, ORDER_FINISHED, ORDER_REJECTED


@receiver(pre_save, sender=Order)
def status_signal(sender, instance, *args, **kwargs):
    if not instance.pk:
        send_sms(instance.phone, ORDER_SUBMITTED, instance.order_id)
        return

    old_status = Order.objects.get(pk=instance.pk).status
    status = instance.status
    if status != old_status:

        if status == Order.StatusChoices.PENDING:
            send_sms(instance.user.phone, ORDER_PAID, instance.order_id)
            return

        if status == Order.StatusChoices.CONFIRMED:
            send_sms(instance.user.phone, ORDER_CONFIRMED, to_jalali_verbose(instance.receive_time), instance.order_id)
            return

        if status == Order.StatusChoices.IN_PROGRESS:
            send_sms(instance.user.phone, ORDER_IN_PROGRESS, instance.order_id)
            return

        if status == Order.StatusChoices.SHIPPED:
            send_sms(instance.user.phone, ORDER_SHIPPED, instance.order_id)
            return

        if status == Order.StatusChoices.FINISHED:
            send_sms(instance.user.phone, ORDER_FINISHED, instance.order_id)
            return

        if status == Order.StatusChoices.REJECTED:
            send_sms(instance.user.phone, ORDER_REJECTED, instance.order_id)