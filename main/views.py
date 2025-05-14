from django.db.models import Count, Min, Max, Q, ExpressionWrapper, Case, When, F, IntegerField
from django.shortcuts import render, redirect
from blog.models import Post
from shop.models import Product, Brand
from .models import Setting
from order.models import CreditCart
from uuid import uuid4


def home_view(request):
    all_products = Product.objects.filter(is_visible=True).annotate(
        verified_comments_count=Count('comments', filter=Q(comments__is_verified=True))
    )
    all_brands = Brand.objects.prefetch_related('products').all()
    context = {
        'posts': Post.objects.select_related('user').filter(is_visible=True).order_by('-created_at')[:6],
        'title_product': all_products.filter(discount__gt=-1).order_by('-views')[0],
        'top_brands': all_brands.filter(products__is_visible=True).annotate(
            max_discount=Max('products__discount'),
            min_price=Min('products__price'),
            min_discount=Min('products__discount'),
            min_volume=Min('products__available_volumes__volume'),
            least_price=ExpressionWrapper(
                Case(
                    When(max_discount=-1, then=F('min_price')),
                    default=F('min_discount'),
                    output_field=IntegerField()
                ) * F('min_volume'),
                output_field=IntegerField()
            )
        ).order_by('-products__site_score')[:4],
        'top_products': all_products.order_by('-site_score')[:6],
        'all_brand': all_brands
    }
    settings = Setting.objects.first()
    if settings.show_offer:
        context.update({
            'offer_title': settings.title,
            'offer_event': settings.event,
            'offer_link': settings.get_offer_link(),
            'offer_banner': settings.banner.url,
        })
    return render(request, 'index.html', context)


def credit_card_view(request):
    if not request.user.is_authenticated:
        return render(request, 'credit-card-empty.html')
    credit_card = None

    try:
        credit_card = CreditCart.objects.get(created_by=request.user)
        return render(request, 'credit-card.html', {'credit_card': credit_card})
    except CreditCart.DoesNotExist:
        return render(request, 'credit-card-empty.html')


def credit_card_create_view(request):
    if not request.user.is_authenticated or CreditCart.objects.filter(created_by=request.user).exists():
        return redirect('main:credit_card')

    CreditCart.objects.create(
        token=str(uuid4())[:10],
        credit=0,
        created_by=request.user,
    )

    return redirect('main:credit_card')


def credit_card_charge_view(request, charge):
    if not request.user.is_authenticated:
        return redirect('main:credit_card')
    credit_card = None
    try:
        credit_card = CreditCart.objects.get(created_by=request.user)
        if charge in ('100000', '250000', '500000', '750000', '1000000', '5000000', '10000000', '15000000', '20000000'):
            print('*' * 30)
            print('REDIRECTED TO GATEWAY PAGE')
            print('*' * 30)
            credit_card.credit += int(charge)
            credit_card.save()
    except CreditCart.DoesNotExist:
        return redirect(request, 'credit-card-empty.html')

    return redirect('main:credit_card')
