from django.urls import path
from . import views


app_name = 'cart'

urlpatterns = [
    path('list/', views.cart_view, name='cart'),
    path('add/', views.add_view, name='add'),
    path('update/', views.update_view, name='update'),
    path('delete/', views.delete_view, name='delete'),
    path('discount/', views.apply_discount, name='apply_discount'),
]