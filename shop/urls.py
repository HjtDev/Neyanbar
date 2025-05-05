from django.urls import path
from . import views


app_name = 'shop'

urlpatterns = [
    path('view_handler/', views.view_handler, name='view_handler'),
    path('like_handler/', views.like_handler, name='like_handler'),
    path('comment_handler/', views.comment_handler, name='comment_handler'),
    path('comment_like/', views.comment_like, name='comment_like'),
    path('products/detail/<slug>/', views.product_view, name='product-detail'),
]