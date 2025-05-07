from django.db.models import Count, Min, Max, Q, ExpressionWrapper, Case, When, F, IntegerField
from django.shortcuts import render
from blog.models import Post
from shop.models import Product, Brand


def home_view(request):
    all_products = Product.objects.filter(is_visible=True).annotate(
        verified_comments_count=Count('comments', filter=Q(comments__is_verified=True))
    )
    context = {
        'posts': Post.objects.select_related('user').filter(is_visible=True).order_by('-created_at')[:6],
        'title_product': all_products.filter(discount__gt=-1).order_by('-views')[0],
        'top_brands': Brand.objects.prefetch_related('products').filter(products__is_visible=True).annotate(
            max_discount=Max('products__discount'),
            min_price=Min('products__price'),
            min_discount=Min('products__discount'),
            min_volume=Min('products__available_volumes__volume'),
        ).annotate(
            least_price=ExpressionWrapper(
                Case(
                    When(max_discount=-1, then=F('min_price')),
                    default=F('min_discount'),
                    output_field=IntegerField()
                ) * F('min_volume'),
                output_field=IntegerField()
            )
        ).order_by('-products__site_score')[:4],
        'top_products': all_products.order_by('-site_score')[:6]
    }
    return render(request, 'index.html', context)
