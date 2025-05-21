from django.urls import path
from . import views


app_name = 'order'

urlpatterns = [
    path('', views.order_view, name='order'),
    path('submit/', views.order_submit, name='order_submit'),
    path('submit/verify/', views.verify_order, name='verify_order'),
    path('status/<order_id>/', views.order_status, name='order_status'),
    path('pay/', views.pay_order, name='pay-order'),
    path('zarinpal/request/', views.zarinpal_request, name='zarinpal_request'),
    path('zarinpal/verify/', views.zarinpal_verify, name='zarinpal_verify'),
]