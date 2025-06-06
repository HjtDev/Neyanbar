from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from datetime import datetime
import os
from random import choice
from django.conf import settings
from django.http import JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt
import jdatetime
from django.views.decorators.http import require_http_methods, require_POST
from .models import Post, Category, Tag, Comment
from main.templatetags.tags import to_jalali_verbose
# from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
# from django.db.models import Q


@csrf_exempt
def editor_upload_handler(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file_obj = request.FILES['file']
        now = datetime.now()
        now = jdatetime.GregorianToJalali(now.year, now.month, now.day)

        upload_path = os.path.join(
            settings.MEDIA_ROOT, 'editor',
            str(now.jyear), str(now.jmonth).zfill(2), str(now.jday).zfill(2)
        )
        os.makedirs(upload_path, exist_ok=True)
        file_path = os.path.join(upload_path, file_obj.name)
        with open(file_path, 'wb+') as f:
            for chunk in file_obj.chunks():
                f.write(chunk)
        file_url = f"{settings.MEDIA_URL}editor/{now.jyear}/{str(now.jmonth).zfill(2)}/{str(now.jday).zfill(2)}/{file_obj.name}"
        return JsonResponse({'location': file_url})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@require_http_methods(['PATCH'])
def view_handler(request):
    data = QueryDict(request.body)
    post_id = data.get('id')

    if post_id:
        try:
            post = Post.objects.get(id=post_id)
            post.views += 1
            post.save()
            return JsonResponse({}, status=200)
        except Post.DoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=404)
    return JsonResponse({'error': 'Invalid request'}, status=400)


def post_detail_view(request, slug):
    try:
        post = Post.objects.prefetch_related('tags', 'comments', 'comments__user').get(slug=slug)
        if not post.is_visible and not request.user.is_superuser:
            return redirect('main:index')

        all_posts = Post.objects.all()

        most_viewed = all_posts.exclude(id=post.id).order_by('-views')
        suggestion = all_posts.filter(category=post.category).exclude(id=post.id).order_by('-created_at')[:6]
        other_post = choice(all_posts.exclude(id=post.id) or most_viewed[:6])
        all_posts = list(all_posts.exclude(id=post.id))
        next_post = all_posts[list(all_posts).index(other_post) - 1]

        context = {
            'post': Post.objects.get(slug=slug),
            'suggestion': suggestion,
            'other_post': other_post,
            'next_post': next_post,
            'most_viewed': most_viewed[:3],
            'categories': Category.objects.all(),
            'tags': Tag.objects.all(),
        }
        return render(request, 'blog.html', context)
    except Post.DoesNotExist:
        return redirect('main:index')


@require_POST
def comment_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'You are not logged in'}, status=403)

    post_id = request.POST.get('post')
    content = request.POST.get('content')

    if not content:
        return JsonResponse({'error': 'Content is required'}, status=400)

    try:
        post = Post.objects.get(id=post_id)
        if not post.comments.filter(user=request.user).exists() or request.user.is_superuser:
            comment = Comment.objects.create(content=content, post=post, user=request.user)
            return JsonResponse({'name': str(request.user), 'profile': request.user.profile.url,
                                 'created_at': to_jalali_verbose(comment.created_at)}, status=200)
        return JsonResponse({}, status=406)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)


def post_list_view(request):
    filters = []
    all_posts = Post.objects.filter(is_visible=True)
    posts = all_posts.select_related('user', 'category').prefetch_related('comments').order_by('-created_at')
    tags = Tag.objects.all()

    if request.GET.get('category'):
        posts = posts.filter(category__slug=request.GET.get('category'))
        filters.append(f'دسته بندی {posts.first().category.name}')

    if request.GET.get('tag'):
        tag = tags.get(slug=request.GET.get('tag'))
        posts = posts.filter(tags__in=[tag])
        filters.append(tag.name)

    if request.GET.get('author'):
        posts = posts.filter(user__name=request.GET.get('author'))
        filters.append(f'نویسنده {posts.first().user.name}')

    search_query = request.GET.get('search')
    if search_query:
        posts = posts.filter(title__icontains=search_query)
        filters.append(f'جستوجو برای {search_query}')

    page = int(request.GET.get('page', 1))
    post = Paginator(posts, 2)

    most_viewed = all_posts.order_by('-views')
    # most_viewed = all_posts.exclude(id__in=[p.id for p in post.object_list]).order_by('-views')  # separates most_viewed from current page posts

    context = {
        'posts': post.page(page if page < post.num_pages else post.num_pages),
        'filters': filters,
        'most_viewed': most_viewed[:3],
        'categories': Category.objects.all(),
        'tags': tags,
    }
    return render(request, 'blog-list.html', context)
