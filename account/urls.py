from django.urls import path
from . import views


app_name = 'account'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('login/complete/', views.login_complete_view, name='login-complete'),
    path('register/', views.register_view, name='register'),
    path('register/complete/', views.register_complete_view, name='register-complete'),
    path('logout/', views.logout_view, name='logout'),
]
