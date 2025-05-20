from django.conf import settings


sms = settings.SMS
env = settings.ENV
LOGIN_VERIFY = env('LOGIN_VERIFY')
PRODUCT_NOTIFY_ME = env('PRODUCT_NOTIFY_ME')
ORDER_SUBMITTED = env('ORDER_SUBMITTED')
ORDER_PAID = env('ORDER_PAID')
ORDER_CONFIRMED = env('ORDER_CONFIRMED')
ORDER_IN_PROGRESS = env('ORDER_IN_PROGRESS')
ORDER_FINISHED = env('ORDER_FINISHED')
ORDER_SHIPPED = env('ORDER_SHIPPED')
ORDER_REJECTED = env('ORDER_REJECTED')


def send_sms(phone, bodyID, *args):
    sms.send_by_base_number(';'.join(str(arg) for arg in args), phone, bodyID)
