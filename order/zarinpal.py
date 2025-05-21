from django.shortcuts import redirect, reverse
from .models import Order, CreditCart
from django.http import HttpResponse


def start_payment(request, order_id, r_reverse=False, charge=''):
    if charge:
        request.session['start_credit_payment'] = charge
    else:
        request.session['start_payment'] = order_id
    request.session.modified = True
    return reverse('order:zarinpal_request') if r_reverse else redirect('order:zarinpal_request')


def get_payment_obj(request) -> Order | CreditCart | HttpResponse:
    try:
        if request.session.get('start_payment'):
            return Order.objects.get(order_id=request.session['start_payment'])
        elif request.session.get('start_credit_payment'):
            return CreditCart.objects.get(created_by=request.user)
        else:
            return HttpResponse('هیچ پرداختی برای شما ثبت نشده است')

    except Order.DoesNotExist:
        return HttpResponse('مشکلی در پیدا کردن سفارش شما پیدا شده است لطفا مجددا تلاش کنید و صورت تداوم مشکل با پشتیبانی تماس بگیرید')
    except CreditCart.DoesNotExist:
        return HttpResponse('مشکلی در پیدا کردن کارت اعتباری شما پیدا شده است لطفا مجددا تلاش کنید و در صورت تداوم مشکل با پشتیبانی تماس بگیرید')
    except KeyError:
        return HttpResponse('سفارش شما معتبر نمی باشد')


def delete_payment(request):
    if request.session.get('start_payment'):
        del request.session['start_payment']
    if request.session.get('start_credit_payment'):
        del request.session['start_credit_payment']
