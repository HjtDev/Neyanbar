from django.http import QueryDict, JsonResponse
from django.shortcuts import render, redirect
from django.db.models import Q, Avg
from django.views.decorators.http import require_http_methods, require_POST
from shop.models import Product, Comment
from main.templatetags.tags import to_jalali_verbose


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
        product = Product.objects.prefetch_related('comments').get(slug=slug)
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

    average_rating = int(product.comments.filter(is_verified=True).aggregate(Avg('score'))['score__avg'])

    context = {
        'product': product,
        'suggestion': suggestion,
        'most_viewed_col1': most_viewed_col1,
        'most_viewed_col2': most_viewed_col2,
        'rating': average_rating,
        'verified_comment_count': product.comments.filter(is_verified=True).count(),
    }
    return render(request, 'product.html', context)


@require_POST
def comment_handler(request):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'You are not logged in'}, status=403)

    product_id = request.POST.get('id')
    content = request.POST.get('content')

    if not content:
        return JsonResponse({'error': 'Content is required'}, status=400)

    try:
        product = Product.objects.get(id=product_id)
        comment = Comment.objects.create(content=content, product=product, user=request.user)
        return JsonResponse({'name': str(request.user), 'profile': request.user.profile.url,
                             'created_at': to_jalali_verbose(comment.created_at), 'id': comment.id}, status=200)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)


@require_http_methods(['PATCH'])
def comment_like(request):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'You are not logged in'}, status=403)

    comment_id = QueryDict(request.body).get('id')
    try:
        if comment_id:
            comment = Comment.objects.get(id=comment_id)
            if request.user in comment.liked_by.all():
                comment.liked_by.remove(request.user)
                return JsonResponse({'like': False}, status=200)
            else:
                comment.liked_by.add(request.user)
                return JsonResponse({'like': True}, status=200)
        else:
            return JsonResponse({'error': 'Comment id required'}, status=400)

    except Comment.DoesNotExist:
        return JsonResponse({'error': 'Comment not found'}, status=404)

