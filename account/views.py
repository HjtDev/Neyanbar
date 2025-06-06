from datetime import timedelta

from django.contrib.auth import login, logout
from copy import deepcopy
from blog.models import Post
from order.models import Order, Transaction
from django.db.models import Sum, Max, Count
from django.shortcuts import render, redirect
from django.http.response import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.core.cache import cache
from .forms import validate_phone, validate_email
from .models import User
from random import randint
from main.utilities import send_sms, LOGIN_VERIFY
from django.http import QueryDict
from shop.models import Product, Volume
from django.utils import timezone


@require_POST
def login_view(request):
    phone = request.POST.get('phone')
    try:
        if phone and validate_phone(phone):
            user = User.objects.get(phone=phone)
            if cache.get(f'login-user-{user.id}'):
                return JsonResponse({'message': 'لطفا حداقل ۳۰ ثانیه برای دریافت کد جدید صبر کنید.'}, status=403)
            token = randint(1000, 9999)
            cache.set(f'login-user-{user.id}', token, timeout=30)
            send_sms(phone, LOGIN_VERIFY, token)
            return JsonResponse({'token_sent': True}, status=200)
        else:
            return JsonResponse({'message': 'شماره تلفن اشتباه است.'}, status=400)
    except User.DoesNotExist:
        return JsonResponse({'message': 'این شماره تلفن وجود ندارد.'}, status=404)


@require_POST
def login_complete_view(request):
    phone = request.POST.get('phone')
    token = request.POST.get('token')
    try:
        if phone and token:
            user = User.objects.get(phone=phone)
            code = cache.get(f'login-user-{user.id}')
            if not code:
                return JsonResponse({'message': 'کد تایید منقضی شده است.'}, status=406)
            elif code == int(token):
                cart = deepcopy(request.session.get('cart', {}))
                discount = deepcopy(request.session.get('discount', None))
                login(request, user)
                request.session['cart'] = cart
                if discount:
                    request.session['discount'] = discount
                cache.delete(f'login-user-{user.id}')
                return JsonResponse({'logged_in': True}, status=200)
            else:
                return JsonResponse({'message': 'کد تایید اشتباه است.'}, status=403)
        else:
            return JsonResponse({'message': 'کد تایید یا شماره تلفن اشتباه می باشد.'}, status=400)
    except User.DoesNotExist:
        return JsonResponse({'message': 'این شماره تلفن وجود ندارد.'}, status=404)


@require_POST
def register_view(request):
    name = request.POST.get('name')
    phone = request.POST.get('phone')
    email = request.POST.get('email')
    if not name or len(name) < 3:
        return JsonResponse({'message': 'لطفا یک نام معتبر وارد کنید.'}, status=400)
    if not validate_email(email):
        return JsonResponse({'message': 'لطفا یک ایمیل معتبر وارد کنید.'}, status=400)

    if phone and validate_phone(phone):
        user = User.objects.filter(phone=phone).exists()
        if user:
            return JsonResponse({'message': 'این شماره تلفن قبلا استفاده شده است.'}, status=403)
        if cache.get(f'register-user-{phone}'):
            return JsonResponse({'message': 'لطفا حداقل ۳۰ ثانیه برای دریافت کد جدید صبر کنید.'}, status=403)
        token = randint(1000, 9999)
        cache.set(f'register-user-{phone}', token, timeout=30)
        send_sms(phone, LOGIN_VERIFY, token)
        return JsonResponse({'token_sent': True}, status=200)
    else:
        return JsonResponse({'message': 'شماره تلفن اشتباه است.'}, status=400)


@require_POST
def register_complete_view(request):
    name = request.POST.get('name')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    token = request.POST.get('token')

    if name and email and phone and token:
        code = cache.get(f'register-user-{phone}')
        if not code:
            return JsonResponse({'message': 'کد تایید منقضی شده است.'}, status=406)
        elif code == int(token):
            user = User.objects.create_user(phone=phone, name=name, email=email)
            cart = deepcopy(request.session.get('cart', {}))
            discount = deepcopy(request.session.get('discount', None))
            login(request, user)
            request.session['cart'] = cart
            if discount:
                request.session['discount'] = discount
            cache.delete(f'register-user-{phone}')
            return JsonResponse({'logged_in': True}, status=200)
        else:
            return JsonResponse({'message': 'کد تایید اشتباه است.'}, status=403)
    else:
        return JsonResponse({'message': 'کد تایید یا شماره تلفن اشتباه می باشد.'}, status=400)


def logout_view(request):
    if request.user.is_authenticated:
        cart = deepcopy(request.session.get('cart', {}))
        discount = deepcopy(request.session.get('discount', None))
        logout(request)
        request.session['cart'] = cart
        if discount:
            request.session['discount'] = discount
    return redirect('main:index')


def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('main:index')
    if request.user.is_superuser:
        context = {
            'total_shop_views': Product.objects.all().aggregate(Sum('views'))['views__sum'] or 1,
            'total_blog_views': Post.objects.all().aggregate(Sum('views'))['views__sum'] or 1,
            'total_views': Product.objects.all().aggregate(Sum('views'))['views__sum'] or 1 + Post.objects.all().aggregate(Sum('views'))['views__sum'] or 1,
            'most_seen_post': Post.objects.all().order_by('-views').first(),
            'most_seen_product': Product.objects.all().order_by('-views').first(),
            'most_sold_product': Product.objects.all().annotate(sold=Count('bought_by')).order_by('-sold').first(),
            'most_sold_volume': Volume.objects.all().annotate(sold=Count('order_items')).order_by('-sold')[:3],

            'alltime_order_count': Order.objects.all().count(),
            'alltime_total': sum(order.get_total_cost() for order in Order.objects.exclude(status__in=[Order.StatusChoices.NOT_PAID, Order.StatusChoices.REJECTED])),

            'today_orders_count': Order.objects.filter(created_at__date=timezone.localdate()).count(),
            'today_total': sum(
                order.get_total_cost() for order in Order.objects.filter(
                    created_at__date=timezone.localdate()
                ).exclude(
                    status__in=[Order.StatusChoices.NOT_PAID, Order.StatusChoices.REJECTED]
                )
            ),

            'last_week_orders_count': Order.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count(),

            'last_week_total': sum(
                order.get_total_cost() for order in Order.objects.filter(
                    created_at__gte=timezone.now() - timedelta(days=7)
                ).exclude(
                    status__in=[Order.StatusChoices.NOT_PAID, Order.StatusChoices.REJECTED]
                )
            ),
            'last_month_orders_count': Order.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            ).count(),

            'last_month_total': sum(
                order.get_total_cost() for order in Order.objects.filter(
                    created_at__gte=timezone.now() - timedelta(days=30)
                ).exclude(
                    status__in=[Order.StatusChoices.NOT_PAID, Order.StatusChoices.REJECTED]
                )
            ),

            # Last 90 days (last season)
            'last_season_orders_count': Order.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=90)
            ).count(),

            'last_season_total': sum(
                order.get_total_cost() for order in Order.objects.filter(
                    created_at__gte=timezone.now() - timedelta(days=90)
                ).exclude(
                    status__in=[Order.StatusChoices.NOT_PAID, Order.StatusChoices.REJECTED]
                )
            ),

            # Last 365 days (last year)
            'last_year_orders_count': Order.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=365)
            ).count(),

            'last_year_total': sum(
                order.get_total_cost() for order in Order.objects.filter(
                    created_at__gte=timezone.now() - timedelta(days=365)
                ).exclude(
                    status__in=[Order.StatusChoices.NOT_PAID, Order.StatusChoices.REJECTED]
                )
            ),

            'biggest_transaction': Transaction.objects.all().order_by('-paid_amount').first(),
        }
        return render(request, 'account.html', context)
    return render(request, 'account.html')


@require_http_methods(['PATCH'])
def edit_profile_view(request):
    data = QueryDict(request.body)
    name = data.get('name')
    email = data.get('email')

    if not name or len(name) < 3:
        return JsonResponse({'name': 'لطفا یک نام معتبر انتخاب کنید.'}, status=400)

    if not validate_email(email):
        return JsonResponse({'email': 'لطفا یک ایمیل معتبر انتخاب کنید.'}, status=400)


    if request.user.is_authenticated:
        request.user.name, request.user.email = name, email
        request.user.save()

    return JsonResponse({}, status=200)


@require_http_methods(['PATCH'])
def compare_list_handler(request):
    if not request.user.is_authenticated:
        return JsonResponse({}, status=401)

    data = QueryDict(request.body)
    product_id = data.get('id')
    action = data.get('action')

    try:
        if product_id and action:
            product = Product.objects.get(id=product_id)
            compare_list = request.user.compare_list
            if action == 'update':
                if product in compare_list.all():
                    compare_list.remove(product)
                    return JsonResponse({'added': False}, status=200)
                else:
                    if compare_list.count() == 4:
                        return JsonResponse({'limit': True}, status=403)
                    compare_list.add(product)
                    return JsonResponse({'added': True}, status=200)
            elif action == 'remove':
                compare_list.remove(product)
                return JsonResponse({'empty': compare_list.exists()}, status=200)
            else:
                return JsonResponse({'message': 'Invalid action.'}, status=400)
        else:
            return JsonResponse({'message': 'Product id and Action are required'}, status=400)

    except Product.DoesNotExist:
        return JsonResponse({'message': 'Product not found'}, status=404)


def compare_list_view(request):
    if not request.user.is_authenticated:
        return redirect('main:index')

    compare_list = request.user.compare_list.all()

    if not compare_list.exists():
        return redirect('shop:product-list')

    return render(request, 'compare.html', {'compare_list': request.user.compare_list.all()})
