from django.urls import path
from . import views


app_name = 'blog'

urlpatterns = [
    path('view_handler/', views.view_handler, name='view_handler'),
    path('editor/upload/', views.editor_upload_handler, name='editor-upload'),
    path('posts/detail/<slug>/', views.post_detail_view, name='post-detail'),
]