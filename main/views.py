from django.db.models import Count, Min, Max, ExpressionWrapper, Case, When, F, IntegerField
from django.shortcuts import render, redirect
from blog.models import Post
from shop.models import Product, Brand
from .models import Setting, AboutUs, Terms, PerfumeRequest
from order.models import CreditCart
from uuid import uuid4
from order.zarinpal import start_payment
from jdatetime import date as jdate


def home_view(request):
    all_products = Product.objects.select_related('brand').filter(is_visible=True).annotate(
        verified_comments_count=Count('comments')
    )
    all_brands = Brand.objects.prefetch_related('products').all()

    title_products = all_products.filter(discount__gt=-1)
    if not title_products.exists():
        title_products = all_products.order_by('-views')

    settings = Setting.objects.first()
    context = {
        'posts': Post.objects.select_related('user').filter(is_visible=True).order_by('-created_at')[:6],
        'title_product': title_products[0],
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
        'neyanbar_suggestion': all_products.order_by('-views')[:6],
        'top_discounts': title_products.exclude(id=title_products[0].id).annotate(max_discount=Max('discount')).order_by('max_discount')[:6],
        'sweet_product': all_products.filter(taste=Product.TasteChoices.SWEET).order_by('-site_score').first(),
        'sour_product': all_products.filter(taste=Product.TasteChoices.SOUR).order_by('-site_score').first(),
        'bitter_product': all_products.filter(taste=Product.TasteChoices.BITTER).order_by('-site_score').first(),
        'spicy_product': all_products.filter(taste=Product.TasteChoices.SPICY).order_by('-site_score').first(),
        'top_male_product': all_products.filter(gender__in=[Product.GenderChoices.MALE, Product.GenderChoices.UNISEX]).annotate(
            max_discount=Max('discount'),
            min_discount = Min('discount'),
            min_price=Min('price'),
            min_volume=Min('available_volumes__volume'),
            least_price=ExpressionWrapper(
                Case(
                    When(max_discount=-1, then=F('min_price')),
                    default=F('min_discount'),
                    output_field=IntegerField()
                ) * F('min_volume'),
                output_field=IntegerField()
            )
        ).order_by('least_price').first(),
        'top_female_product': all_products.filter(gender__in=[Product.GenderChoices.FEMALE, Product.GenderChoices.UNISEX]).annotate(
            max_discount=Max('discount'),
            min_discount = Min('discount'),
            min_price=Min('price'),
            min_volume=Min('available_volumes__volume'),
            least_price=ExpressionWrapper(
                Case(
                    When(max_discount=-1, then=F('min_price')),
                    default=F('min_discount'),
                    output_field=IntegerField()
                ) * F('min_volume'),
                output_field=IntegerField()
            )
        ).order_by('least_price').first(),
        'new_products': all_products.order_by('-created_at')[:7],
        'high_rated_products': all_products.order_by('-site_score')[:7],
        'most_sold_products': all_products.annotate(sold=Count('bought_by', distinct=True)).order_by('-sold')[:7],
        'most_viewed_products': all_products.order_by('-views')[:7],
        'video_text': settings.video_text,
        'footer_text': settings.footer_text,
    }
    if settings.show_offer:
        context.update({
            'offer_title': settings.title,
            'offer_event': settings.event,
            'offer_link': settings.get_offer_link(),
            'offer_banner': settings.banner.url,
        })
    if jdate.today().month <= 6:
        context.update({
            'season_title': 'عطر های بهاری و تابستانی',
            'season_products': all_products.filter(season__in=[Product.SeasonChoices.SUMMER, Product.SeasonChoices.ALL_SEASONS]).order_by('-discount')[:7]
        })
    else:
        context.update({
            'season_title': 'عطر های پاییزی و زمستانی',
            'season_products': all_products.filter(season__in=[Product.SeasonChoices.WINTER, Product.SeasonChoices.ALL_SEASONS]).order_by('-discount')[:7]
        })
    return render(request, 'index.html', context)


def credit_card_view(request):
    if not request.user.is_authenticated:
        return render(request, 'credit-card-empty.html')
    credit_cart = None

    try:
        credit_cart = CreditCart.objects.filter(created_by=request.user)
        if not credit_cart.exists():
            return render(request, 'credit-card-empty.html')
        return render(request, 'credit-card.html', {'credit_carts': credit_cart})
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
            return start_payment(request, credit_card.pk, False, charge)
    except CreditCart.DoesNotExist:
        return redirect(request, 'credit-card-empty.html')

    return redirect('main:credit_card')


def perfume_request_view(request):
    p_request = request.GET.get('request')
    if p_request:
        PerfumeRequest.objects.get_or_create(text=p_request)
    return redirect('main:index')


def about_us_view(request):
    return render(request, 'about-us.html', {'objects': AboutUs.objects.all(), 'show_info': True, 'title': 'درباره ما'})


def terms_view(request):
    return render(request, 'about-us.html', {'objects': Terms.objects.all(), 'show_info': False, 'title': 'شرایط و ضوابط'})


# def faq_view(request):
#     return render(request, 'faq.html', {'faq': FAQ.objects.filter(is_visible=True)})
