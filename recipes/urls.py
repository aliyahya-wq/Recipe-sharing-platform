from django.urls import path
from . import views

urlpatterns = [
    path('', views.recipe_list, name='recipes'),
    path('home/', views.home, name='home'),
    path('detail/<str:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('add/', views.recipe_add, name='recipe_add'),
    path('result/', views.recipe_result, name='recipe_result'),
    path('comment/<str:recipe_id>/', views.add_comment, name='add_comment'),
    path('reply/<str:recipe_id>/<int:comment_index>/', views.add_reply, name='add_reply'),
    path('rate/<str:recipe_id>/', views.rate_recipe, name='rate_recipe'),
    path('favorite/<str:recipe_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorites_list, name='favorites'),
]
