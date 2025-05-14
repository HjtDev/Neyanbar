from xml.etree.ElementInclude import include

from django.urls import path
from . import views


app_name = 'main'

urlpatterns = [
    path('', views.home_view, name='index'),
    path('credit-card/', views.credit_card_view, name='credit_card'),
    path('credit-card/create/', views.credit_card_create_view, name='credit_card_create'),
    path('credit-card/charge/<charge>/', views.credit_card_charge_view, name='credit_card_charge'),
    path('join-club/', views.join_club_view, name='join_club'),
]