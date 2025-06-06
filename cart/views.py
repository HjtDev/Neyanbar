from django.db.models import Min
from django.http import JsonResponse, QueryDict
from .models import Cart
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from shop.models import Product, Volume
from django.template.loader import render_to_string
from json import loads
from order.models import Discount


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


@require_http_methods(['PATCH'])
def update_view(request):
    data = loads(request.body)
    results = []
    cart = Cart(request)
    try:
        for pid, options in data.items():
            for volume, quantity in options.items():
                results.append(cart.update(pid, int(volume), quantity, Product.objects.get(id=int(pid)).inventory))
        if all(results):
            cart.save()
            return JsonResponse({'message': 'Success'}, status=200)
        return JsonResponse({'message': 'Invalid payload'}, status=400)
    except Product.DoesNotExist:
        return JsonResponse({'message': 'Product Does Not Exist'}, status=400)



def cart_view(request):
    if not len(Cart(request)):
        return render(request, 'cart-empty.html')
    return render(request, 'cart.html')


@require_http_methods(['GET'])
def apply_discount(request):
    token = request.GET.get('token')
    try:
        discount = Discount.objects.get(token=token)
        valid, message = discount.is_valid(request.user)
        if valid:
            cart = Cart(request)
            for item in cart:
                if item['product'] in message:
                    request.session['discount'] = discount.id
                    return JsonResponse({})
            return JsonResponse({'btn': 'هیچ یک از محصولات لیست شما شامل این تخفیف نمی شود'}, status=404)
        return JsonResponse({'btn': message}, status=403)
    except Discount.DoesNotExist:
        return JsonResponse({'btn': 'این کد تخفیف نا معتبر است'}, status=404)
