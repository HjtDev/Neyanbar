from django.conf import settings
from django.core.cache import cache
import logging

sms = settings.SMS
env = settings.ENV
LOGIN_VERIFY = env('LOGIN_VERIFY')
PRODUCT_NOTIFY_ME = env('PRODUCT_NOTIFY_ME')
ORDER_SUBMITTED = env('ORDER_SUBMITTED')
ORDER_SUBMITTED_ADMIN = env('ORDER_SUBMITTED_ADMIN')
ORDER_PAID = env('ORDER_PAID')
ORDER_CONFIRMED = env('ORDER_CONFIRMED')
ORDER_IN_PROGRESS = env('ORDER_IN_PROGRESS')
ORDER_FINISHED = env('ORDER_FINISHED')
ORDER_SHIPPED = env('ORDER_SHIPPED')
ORDER_REJECTED = env('ORDER_REJECTED')
ADMIN_PHONE = env('ADMIN_PHONE')


def send_sms(phone, bodyID, *args):
    remaining_sms = float(sms.get_credit().get('Value'))
    if remaining_sms <= 10.0:
        if not cache.get('sms_warning', False):
            sms.send(ADMIN_PHONE, '50004001766438', '')
            cache.set('sms_warning', True)
            logging.warning(f'Warning SMS sent : {remaining_sms=}')
    else:
        cache.set('sms_warning', False)

    if bodyID is None:
        return sms.send(phone, '50004001766438', args[0])
    else:
        return sms.send_by_base_number(';'.join(str(arg) for arg in args), phone, bodyID)
