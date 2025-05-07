from django.db.models import Min
from django.http import JsonResponse, QueryDict
from .models import Cart
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from shop.models import Product, Volume
from django.template.loader import render_to_string


@require_http_methods(['PATCH'])
def delete_view(request):
    data = QueryDict(request.body)
    pid = data.get('id')
    volume = data.get('volume')
    cart = Cart(request)
    cart.delete(str(pid), str(volume))
    return JsonResponse({'length': len(cart), 'total': cart.get_total_cost()}, status=200)


@require_http_methods(['PATCH'])
def add_view(request):
    data = QueryDict(request.body)
    pid = data.get('id')
    quantity = int(data.get('quantity')) or 1
    size = int(data.get('volume'))

    try:
        product = Product.objects.get(id=int(pid))
        volume = size if product.available_volumes.filter(volume=size).exists() else product.available_volumes.aggregate(Min('volume'))['volume__min']
        cart = Cart(request)
        added = cart.add(str(product.id), volume, quantity, product.inventory)
        return JsonResponse({
            'added': added,
            'url': product.get_absolute_url(),
            'image': product.images.first().image.url,
            'name': product.name,
            'price': product.get_volume_price(volume),
            'quantity': quantity,
            'length': len(cart),
            'total': cart.get_total_cost(),
            'partial': render_to_string(request=request, template_name='partials/cart_list.html', context={'cart': cart}),
        }, status=200)
    except (Product.DoesNotExist, Volume.DoesNotExist) as e:
        print(e)
        return JsonResponse({'message': 'Invalid payload'}, status=400)
