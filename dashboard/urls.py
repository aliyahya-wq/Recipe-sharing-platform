from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('users/add-staff/', views.add_staff_user, name='add_staff_user'),
    path('users/edit/<int:pk>/', views.edit_user, name='edit_user'),
    path('users/delete/<int:pk>/', views.delete_user, name='delete_user'),
    path('users/toggle-status/<int:pk>/', views.toggle_user_status, name='toggle_user_status'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/delete/<int:pk>/', views.delete_category, name='delete_category'),
    path('recipes/', views.recipe_list, name='recipe_list'),
    path('recipes/delete/<int:pk>/', views.delete_recipe, name='delete_recipe'),
    path('recipes/edit/<int:pk>/', views.edit_recipe, name='edit_recipe'),
    path('comments/', views.comment_list, name='comment_list'),
    path('comments/delete/<int:pk>/', views.delete_comment, name='delete_comment'),
    path('reports/', views.reports, name='reports'),
    path('recycle-bin/', views.recycle_bin, name='recycle_bin'),
    path('recycle-bin/restore/<str:item_type>/<int:pk>/', views.restore_item, name='restore_item'),
    path('recycle-bin/purge/<str:item_type>/<int:pk>/', views.purge_item, name='purge_item'),
    path('activity-log/', views.activity_log, name='activity_log'),
]
