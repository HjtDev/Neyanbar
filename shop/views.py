from django.http import QueryDict, JsonResponse
from django.shortcuts import render, redirect
from django.db.models import Q, Avg, Count, FloatField, F, ExpressionWrapper
from django.views.decorators.http import require_http_methods, require_POST
from shop.models import Product, Comment, Brand, Volume, ProductSmell
from main.templatetags.tags import to_jalali_verbose
from django.core.paginator import Paginator


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
    ).annotate(
        verified_comments_count=Count('comments', filter=Q(comments__is_verified=True)),
        order=ExpressionWrapper(
            F('views') * .25 + F('site_score') * .75,
            output_field=FloatField()
        )
    ).distinct().order_by('-order')[:6]

    most_viewed_col1 = all_products.order_by('-views')[:3]
    most_viewed_col2 = all_products.order_by('-views')[3:7]

    average_rating = int(product.comments.filter(is_verified=True).aggregate(Avg('score'))['score__avg'] or 3)

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
    score = int(request.POST.get('score'))
    content = request.POST.get('content')

    if not content:
        return JsonResponse({'error': 'Content is required'}, status=400)

    try:
        product = Product.objects.get(id=product_id)
        comment = Comment.objects.create(content=content, product=product, user=request.user, score=score)
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


@require_http_methods(['PATCH'])
def notify_me(request):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'You are not logged in'}, status=403)

    product_id = QueryDict(request.body).get('id')

    try:
        if product_id:
            product = Product.objects.get(id=product_id)
            if not request.user in product.remind_to.all():
                product.remind_to.add(request.user)
                return JsonResponse({'added': True}, status=200)
            else:
                product.remind_to.remove(request.user)
                return JsonResponse({'added': False}, status=200)
        else:
            return JsonResponse({'message': 'Product id required'}, status=400)
    except Product.DoesNotExist:
        return JsonResponse({'message': 'Product not found'}, status=404)


def product_list_view(request):
    all_products = Product.objects.filter(is_visible=True).annotate(
        verified_comments_count=Count('comments', filter=Q(comments__is_verified=True)),
        order=ExpressionWrapper(
            F('views') * .35 + F('site_score') * .65,
            output_field=FloatField()
        )
    ).order_by('-order')


    for key in request.GET:
        if request.GET.get('brand'):  # index top brands
            all_products = all_products.filter(brand__name=request.GET.get('brand'))
        elif 'brand' in key:
            all_products = all_products.filter(brand__slug__in=request.GET.getlist(key))

        if 'volumes' in key:
            all_products = all_products.filter(available_volumes__in=Volume.objects.filter(volume__in=[int(v) for v in request.GET.getlist(key)])).distinct()

        if 'smells' in key:
            all_products = all_products.filter(smell__in=ProductSmell.objects.filter(value__in=request.GET.getlist(key))).distinct()

        if 'seasons' in key:
            all_products = all_products.filter(season__in=request.GET.getlist(key))

        if 'tastes' in key:
            all_products = all_products.filter(taste__in=request.GET.getlist(key))

        if 'nature' in key:
            all_products = all_products.filter(nature__in=request.GET.getlist(key))

        if 'durability' in key:
            all_products = all_products.filter(durability__in=request.GET.getlist(key))

        if 'gender' in key:
            all_products = all_products.filter(gender__in=request.GET.getlist(key))

        if 'type' in key:
            all_products = all_products.filter(perfume_type__in=request.GET.getlist(key))

    page = int(request.GET.get('page', 1))
    all_products = Paginator(all_products.distinct(), 3)

    context = {
        'products': all_products.page(page),
        'brands': Brand.objects.all(),
        'volumes': Volume.objects.all(),
        'smells': ProductSmell.objects.all(),
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'filter.html', {'products': all_products.object_list})

    return render(request, 'product_list.html', context)
