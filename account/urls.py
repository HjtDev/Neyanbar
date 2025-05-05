from django.urls import path
from . import views


app_name = 'account'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('login/complete/', views.login_complete_view, name='login-complete'),
    path('register/', views.register_view, name='register'),
    path('register/complete/', views.register_complete_view, name='register-complete'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/edit/', views.edit_profile_view, name='profile-edit'),
    path('dashboard/compare/', views.compare_list_view, name='compare-list'),
    path('dashboard/compare/action/', views.compare_list_handler, name='compare-handler'),
]
