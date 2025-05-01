from django.shortcuts import render
from blog.models import Post


def home_view(request):
    context = {
        'posts': Post.objects.select_related('user').all().order_by('-created_at')[:6]
    }
    return render(request, 'index.html', context)
