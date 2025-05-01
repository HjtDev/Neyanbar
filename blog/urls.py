from django.urls import path
from . import views


app_name = 'blog'

urlpatterns = [
    path('view_handler/', views.view_handler, name='view_handler'),
    path('comment/', views.comment_view, name='comment_view'),
    path('editor/upload/', views.editor_upload_handler, name='editor-upload'),
    path('posts/list/', views.post_list_view, name='post-list'),
    path('posts/detail/<slug>/', views.post_detail_view, name='post-detail'),
]