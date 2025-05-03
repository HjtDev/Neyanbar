from django.shortcuts import render, redirect
from django.db.models import Q
from shop.models import Product


def product_view(request, slug):
    try:
        product = Product.objects.get(slug=slug)
    except Product.DoesNotExist:
        return redirect('main:index')

    all_products = Product.objects.filter(is_visible=True).exclude(id=product.id)

    if not product.is_visible and request.user.is_authenticated:
        return redirect('main:index')

    suggestion = all_products.filter(
        Q(taste=product.taste) |
        Q(nature=product.nature) |
        Q(smell__in=product.smell.all())
    ).distinct().order_by('-created_at')[:6]

    most_viewed_col1 = all_products.order_by('-views')[:3]
    most_viewed_col2 = all_products.order_by('-views')[3:7]

    context = {
        'product': product,
        'suggestion': suggestion,
        'most_viewed_col1': most_viewed_col1,
        'most_viewed_col2': most_viewed_col2,
    }
    return render(request, 'product.html', context)