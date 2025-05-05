from idlelib.rpc import request_queue
from time import sleep

from django.http import QueryDict, JsonResponse
from django.shortcuts import render, redirect
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from shop.models import Product


@require_http_methods(['PATCH'])
def view_handler(request):
    product_id = QueryDict(request.body).get('id')
    try:
        if product_id:
            product = Product.objects.get(id=product_id)
            product.views += 1
            product.save()
            return JsonResponse({'message': 'success'})
        else:
            return JsonResponse({'message': 'Post id required'}, status=400)
    except Product.DoesNotExist:
        return JsonResponse({'message': 'Post not found'}, status=404)


@require_http_methods(['PATCH'])
def like_handler(request):
    if not request.user.is_authenticated:
        return JsonResponse({}, status=401)
    product_id = QueryDict(request.body).get('id')
    try:
        if product_id:
            product = Product.objects.get(id=product_id)
            if request.user in product.liked_by.all():
                product.liked_by.remove(request.user)
                return JsonResponse({'like': False})
            else:
                product.liked_by.add(request.user)
                return JsonResponse({'like': True})
        else:
            return JsonResponse({'message': 'Product id required'}, status=400)
    except Product.DoesNotExist:
        return JsonResponse({'message': 'Product not found'}, status=404)


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