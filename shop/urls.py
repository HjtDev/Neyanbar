from django.urls import path
from . import views


app_name = 'shop'

urlpatterns = [
    path('products/detail/<slug>/', views.product_view, name='product-detail'),
]