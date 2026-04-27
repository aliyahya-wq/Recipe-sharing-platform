from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('profile_edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/relations/', views.user_relations, name='user_relations'),
    path('follow/<str:username>/', views.toggle_follow, name='toggle_follow'),
    path('chefs/', views.chef_list, name='chef_list'),
]
