from django.db.models.signals import pre_save
from django.dispatch import receiver
from postex import postex
from django.utils import timezone
from datetime import datetime, time, timedelta, timezone as dt_timezone


from main.templatetags.tags import to_jalali_verbose
from .models import Order
from main.utilities import (
    send_sms, ORDER_SUBMITTED, ORDER_PAID,
    ORDER_CONFIRMED, ORDER_IN_PROGRESS, ORDER_SHIPPED,
    ORDER_FINISHED, ORDER_REJECTED, ORDER_SUBMITTED_ADMIN, ADMIN_PHONE)


@receiver(pre_save, sender=Order)
def status_signal(sender, instance: Order, *args, **kwargs):
    if not instance.pk:
        send_sms(instance.phone, ORDER_SUBMITTED, instance.order_id)
        send_sms(ADMIN_PHONE, ORDER_SUBMITTED_ADMIN, instance.name, instance.phone, instance.order_id)
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

        if status == Order.StatusChoices.READY_TO_SHIP:
            now = timezone.localtime(timezone.now())
            tomorrow_10am_local = timezone.make_aware(datetime.combine(now.date() + timedelta(days=1), time(10, 0)), timezone.get_current_timezone())
            pickup_date_time = tomorrow_10am_local.isoformat()
            pickup_on_utc = tomorrow_10am_local.astimezone(dt_timezone.utc).isoformat()
            postex.submit_parcel(' '.join(instance.name.split(' ')[:-1]), instance.name.split(' ')[-1], instance.phone, instance.email, instance.national_code,
                                 instance.postal_code, 'ایران', instance.city, instance.address,
                                 instance.get_parcel_items() * 10, 15, 10, 20, 500, True, True, instance.get_total_cost() * 10, 5,
                                 instance.description, instance.id, pickup_date_time, pickup_on_utc, instance.receive_time.isoformat())

        if status == Order.StatusChoices.SHIPPED:
            send_sms(instance.user.phone, ORDER_SHIPPED, instance.order_id)
            return

        if status == Order.StatusChoices.FINISHED:
            send_sms(instance.user.phone, ORDER_FINISHED, instance.order_id)
            return

        if status == Order.StatusChoices.REJECTED:
            send_sms(instance.user.phone, ORDER_REJECTED, instance.order_id)