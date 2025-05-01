from random import choice
from time import sleep

from django.shortcuts import render, redirect
from datetime import datetime
import os
from django.conf import settings
from django.http import JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt
import jdatetime
from django.views.decorators.http import require_http_methods, require_POST
from .models import Post, Category, Tag, Comment
from main.templatetags.tags import to_jalali_verbose


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

        most_viewed = Post.objects.all().exclude(id=post.id).order_by('-views')
        suggestion = Post.objects.filter(category=post.category, is_visible=True).order_by('-created_at')
        l_suggestion = list(suggestion)
        next_post = suggestion[l_suggestion.index(post) - 1] if l_suggestion.index(post) - 1 >= 0 else suggestion[1]
        other_post = choice(suggestion.exclude(id=next_post.id).exclude(id=post.id) or most_viewed[:6])

        context = {
            'post': Post.objects.get(slug=slug),
            'suggestion': suggestion.exclude(id=post.id)[:6],
            'other_post': other_post,
            'next_post': next_post,
            'most_viewed': most_viewed[:3],
            'categories': Category.objects.all(),
            'tags': Tag.objects.all(),
            'verified_comment_count': post.comments.filter(is_verified=True).count()
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
        if not request.user.comments.filter(id=post.id).count():
            comment = Comment.objects.create(content=content, post=post, user=request.user)
            return JsonResponse({'name': str(request.user), 'profile': request.user.profile.url,
                                 'created_at': to_jalali_verbose(comment.created_at)}, status=200)
        return JsonResponse({}, status=406)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)
