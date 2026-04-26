from django.urls import path
from . import views



urlpatterns = [
    path('', views.recipe_list, name='recipes'),
    path('detail/<str:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('add/', views.recipe_add, name='recipe_add'),
    path('result/', views.recipe_result, name='recipe_result'),
    path('comment/<str:recipe_id>/', views.add_comment, name='add_comment'),
    path('reply/<str:recipe_id>/<int:comment_id>/', views.add_reply, name='add_reply'),
    path('rate/<str:recipe_id>/', views.rate_recipe, name='rate_recipe'),
    path('favorite/<str:recipe_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('like/<str:recipe_id>/', views.toggle_like, name='toggle_like'),
    path('favorites/', views.favorites_list, name='favorites'),
    path('liked/', views.user_liked_recipes, name='user_liked_recipes'),
    path('edit/<str:recipe_id>/', views.edit_recipe, name='edit_recipe'),
    path('delete/<str:recipe_id>/', views.delete_recipe, name='delete_recipe'),
]

