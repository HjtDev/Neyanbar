from django.urls import path
from . import views


app_name = 'order'

urlpatterns = [
    path('', views.order_view, name='order'),
    path('submit/', views.order_submit, name='order_submit'),
    path('submit/verify/', views.verify_order, name='verify_order'),
]