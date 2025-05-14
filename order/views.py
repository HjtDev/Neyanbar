from copy import deepcopy
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.urls import reverse

from account.forms import validate_phone, validate_email
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from account.models import User
from cart.models import Cart
from .models import Order, OrderItem, Discount, Transaction, CreditCart
from django.core.cache import cache
from main.models import Setting
from datetime import datetime as dt
from shop.models import Product, Volume
from uuid import uuid4
from main.utilities import send_sms
from random import randint


def order_view(request):
    cart = Cart(request)
    if not len(cart):
        return render(request, 'cart-empty.html')


    setting = Setting.objects.first()
    context = {
        'post_fee': setting.post_fee,
        'tax_fee': setting.tax_fee,
    }
    if request.session.get('discount'):
        try:
            discount = Discount.objects.get(id=request.session['discount'])
            context.update({
                'applied_discount': discount.value,
                'final_price': sum(discount.get_price(item['product'], int(item['volume'])) * int(item['quantity']) for item in cart) * (1 + setting.tax_fee / 100) + setting.post_fee,
            })
        except Discount.DoesNotExist:
            del request.session['discount']
            context.update({
                'applied_discount': 0,
                'final_price': cart.get_total_cost() * (1 + setting.tax_fee / 100) + setting.post_fee,
            })
    else:
        context.update({
            'final_price': cart.get_total_cost() * (1 + setting.tax_fee / 100) + setting.post_fee,
        })
    minimum_days = setting.order_waiting_days
    available_days = []
    now = timezone.now().date()
    orders = Order.objects.exclude(status__in=[Order.StatusChoices.SHIPPED, Order.StatusChoices.FINISHED, Order.StatusChoices.REJECTED]).all()
    while len(available_days) < setting.order_days_limit:
        target_day = now + timedelta(days=minimum_days)
        if orders.filter(receive_time=target_day).count() < setting.orders_per_day:
            available_days.append(target_day)
        minimum_days += 1

    context.update({'dates': available_days})

    return render(request, 'checkout.html', context)


@require_POST
def order_submit(request):
    name = request.POST.get('name')
    phone = request.POST.get('phone')
    email = request.POST.get('email')
    province = request.POST.get('province')
    city = request.POST.get('city')
    address = request.POST.get('address')
    postal_code = request.POST.get('postal_code')
    different_address = request.POST.get('different_address')
    payment_method = request.POST.get('payment_method')
    credit_token = request.POST.get('credit_token')
    payment_date = request.POST.get('payment_date')

    if not name:
        return JsonResponse({'message': 'لطفا نام خود را وارد کنید'}, status=400)

    if not phone or not validate_phone(phone):
        return JsonResponse({'message': 'لطفا یک شماره تلفن معتبر وارد کنید'}, status=400)

    if email and not validate_email(email):
        return JsonResponse({'message': 'لطفا یک ایمیل معتبر وارد کنید'}, status=400)

    if not province:
        return JsonResponse({'message': 'لطفا یک استان معتبر انتخاب کنید'}, status=400)

    if not city:
        return JsonResponse({'message': 'لطفا یک شهر معتبر انتخاب کنید'}, status=400)

    if not address:
        return JsonResponse({'message': 'لطفا یک آدرس معتبر وارد کنید'}, status=400)

    if not postal_code or len(postal_code) != 10:
        return JsonResponse({'message': 'لطفا یک کد پستی معتبر وارد کنید'}, status=400)

    if not payment_method in ('GATEWAY', 'CREDIT'):
        return JsonResponse({'message': 'لطفا نوع پرداخت خود را انتخاب کنید'}, status=400)

    if payment_method == 'CREDIT' and not credit_token:
        return JsonResponse({'message': 'لطفا توکن کارت اعتباری خود را وارد کنید'}, status=400)

    if not payment_date:
        return JsonResponse({'message': 'لطفا یک تاریخ معتبر انتخاب کنید'}, status=400)
    payment_date = dt.strptime(payment_date, '%d %m %Y').date()

    cart = Cart(request)
    order = Order.objects.create(
        order_id=str(uuid4())[:10],
        name=name,
        phone=phone,
        email=email,
        province=province,
        city=city,
        address=address,
        postal_code=postal_code,
        not_for_me=True if different_address == 'true' else False,
        receive_time=payment_date,
    )
    setting = Setting.objects.first()
    total_cost = 0
    if request.session.get('discount'):
        try:
            discount = Discount.objects.get(id=request.session['discount'])
            for item in cart:
                price = discount.get_price(item['product'], int(item['volume'])) * int(item['quantity'])
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    volume=Volume.objects.get(volume=item['volume']),
                    price=price
                )
                total_cost += price
        except Discount.DoesNotExist:
            print('deleting discount')
            del request.session['discount']
    else:
        print('adding items to order manually')
        for item in cart:
            price = item['product'].get_volume_price(int(item['volume'])) * int(item['quantity'])
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                volume=Volume.objects.get(volume=item['volume']),
                price=price
            )
            total_cost += price
    total_cost = total_cost * (1 + setting.tax_fee / 100) + setting.post_fee
    print(f'{total_cost=}')
    cart.clear()
    if request.user.is_authenticated:
        if request.session.get('discount'):
            Discount.objects.get(id=request.session['discount']).users.add(request.user)
            del request.session['discount']
        if payment_method == 'CREDIT':
            try:
                credit_card = CreditCart.objects.get(token=credit_token)
                if credit_card.buy(total_cost):
                    order.user = request.user
                    order.status = Order.StatusChoices.PENDING
                    order.save()
                    Transaction.objects.create(
                        user=request.user,
                        order=order,
                        payment_type=Transaction.PaymentChoices.CREDIT,
                        paid_amount=total_cost,
                    )
                    return JsonResponse({'redirect': reverse('order:order_status', kwargs={'order_id': order.order_id})})
                else:
                    messages.error(request, 'کارت اعتباری شما شارژ کافی برای انجام این تراکنش را ندارد')
                    return JsonResponse({'redirect': reverse('order:order_status', kwargs={'order_id': order.order_id})})
            except CreditCart.DoesNotExist:
                messages.error(request, 'کارت اعتباری نامعتبر است')
                return JsonResponse({'redirect': reverse('order:order_status', kwargs={'order_id': order.order_id})})
        else:
            order.user = request.user
            order.save()
            if request.session.get('discount'):
                Discount.objects.get(id=request.session['discount']).users.add(request.user)
                del request.session['discount']
            print('*' * 30)
            print('REDIRECTED TO PAYMENT PAGE')
            print('*' * 30)
            return JsonResponse({'redirect': reverse('order:order_status', kwargs={'order_id': order.order_id})})

    else:
        request.session['order'] = {'id': order.id, 'payment_method': payment_method, 'credit_token': credit_token, 'total_cost': total_cost}
        token = randint(1000, 9999)
        cache.set(f'order-{token}', phone, timeout=30)
        send_sms(phone, token)
        return JsonResponse({'success': True})


@require_http_methods(['POST', 'GET'])
def verify_order(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        phone = cache.get(f'order-{token}')
        order = Order.objects.get(id=request.session['order'].get('id'))
        if not phone:
            messages.error(request, 'کد تایید نامعتبر بود')
            return redirect('order:order_status', order_id=order.order_id)

        try:  # user already exists and login is successful
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:  # user does not exist registration required
            user = User.objects.create(
                name=order.name,
                email=order.email,
                phone=phone,
            )

        cart, discount, order_session = {}, deepcopy(request.session.get('discount', None)), deepcopy(request.session.get('order', None))
        login(request, user)
        request.session['cart'] = cart
        if discount:
            Discount.objects.get(id=discount).users.add(user)
            del request.session['discount']
        request.session['order'] = order_session

        payment_method = request.session['order'].get('payment_method')
        credit_token = request.session['order'].get('credit_token')
        total_cost = int(request.session['order'].get('total_cost'))
        del request.session['order']

        if payment_method == 'CREDIT':
            try:
                credit_card = CreditCart.objects.get(token=credit_token)
                if credit_card.buy(total_cost):
                    order.status = Order.StatusChoices.PENDING
                    order.user = user
                    order.save()
                    Transaction.objects.create(
                        user=request.user,
                        order=order,
                        payment_type=Transaction.PaymentChoices.CREDIT,
                        paid_amount=total_cost,
                    )
                    return redirect('order:order_status', order_id=order.order_id)
                else:
                    messages.error(request, 'کارت اعتباری شما شارژ کافی برای انجام این تراکنش را ندارد')
                    return redirect('order:order_status', order_id=order.order_id)
            except CreditCart.DoesNotExist:
                messages.error(request, 'کارت اعتباری نامعتبر است')
                return redirect('order:order_status', order_id=order.order_id)
        else:
            order.user = user
            order.save()
            print('*' * 30)
            print('REDIRECTED TO GATEWAY PAGE')
            print('*' * 30)
        return JsonResponse({'redirect': reverse('order:order_status', kwargs={'order_id': order.order_id})})
    else:
        return render(request, 'verify.html')


def order_status(request, order_id):
    try:
        order = Order.objects.prefetch_related('transactions').get(order_id=order_id)
        context = {
            'order': order,
            'total_before_tax': sum(item.price for item in order.items.all()),
        }
        return render(request, 'order-status.html', context)
    except Order.DoesNotExist:
        return redirect('main:index')


@require_POST
def pay_order(request):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'شما باید ابتدا یک حساب کاربری بسازید'}, status=401)

    order_id = request.POST.get('order_id')
    payment_method = request.POST.get('payment_type')
    credit_token = request.POST.get('credit_token')
    order = None
    discount = None

    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        return JsonResponse({'message': 'این سفارش وجود ندارد'}, status=404)

    if order.status == Order.StatusChoices.NOT_PAID:

        total_cost = order.get_total_cost()
        print(f'{total_cost=}')

        if payment_method == 'GATEWAY':
            print('*' * 30)
            print('REDIRECTED TO GATEWAY PAGE')
            print('*' * 30)
            order.user = request.user
            order.save()
            return JsonResponse({'message': f'successful payment from gateway {total_cost}'}, status=400)
        elif payment_method == 'CREDIT':
            try:
                credit_card = CreditCart.objects.get(token=credit_token)
                if credit_card.buy(total_cost):
                    order.status = Order.StatusChoices.PENDING
                    order.user = request.user
                    order.save()
                    Transaction.objects.create(
                        user=request.user,
                        order=order,
                        payment_type=Transaction.PaymentChoices.CREDIT,
                        paid_amount=total_cost,
                    )
                    return JsonResponse({})
                else:
                    return JsonResponse({'message': 'کارت اعتباری شما شارژ کافی برای این تراکنش را ندارد'}, status=403)
            except CreditCart.DoesNotExist:
                return JsonResponse({'message': 'کارت اعتباری شما نا معتبر است'}, status=404)
        else:
            return JsonResponse({'message': 'لطفا نوع پرداخت را انتخاب کنید'}, status=400)
    else:
        return JsonResponse({'message': 'این سفارش قبلا پرداخت شده است'}, status=403)

