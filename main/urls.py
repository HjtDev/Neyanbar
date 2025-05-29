from django.urls import path
from . import views


app_name = 'main'

urlpatterns = [
    path('', views.home_view, name='index'),
    path('credit-card/', views.credit_card_view, name='credit_card'),
    path('credit-card/create/', views.credit_card_create_view, name='credit_card_create'),
    path('credit-card/charge/<charge>/', views.credit_card_charge_view, name='credit_card_charge'),
    path('request/perfume/', views.perfume_request_view, name='perfume-request'),
    path('about-us/', views.about_us_view, name='about_us'),
    path('terms/', views.terms_view, name='terms'),
    # path('faq/', views.faq_view, name='faq'),
]