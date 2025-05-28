from django.conf import settings


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
    if bodyID is None:
        return sms.send(phone, '50004001766438', args[0])
    else:
        return sms.send_by_base_number(';'.join(str(arg) for arg in args), phone, bodyID)
