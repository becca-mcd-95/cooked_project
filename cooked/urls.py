from django.urls import path, include
from cooked import views
from django.contrib.auth import views as auth_views

app_name = 'cooked'

urlpatterns = [
    # Becca
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('search/', views.search_users, name='search_users'),

    # Yanyan
    path('recipes/', views.RecipeListView.as_view(), name='recipe_list'),
    path('recipes/new/', views.RecipeCreateView.as_view(), name='recipe_create'),
    path('recipes/<int:pk>/', views.RecipeDetailView.as_view(), name='recipe_detail'),
    path('recipes/<int:pk>/edit/', views.RecipeUpdateView.as_view(), name='recipe_edit'),
    path('recipes/<int:pk>/delete/', views.RecipeDeleteView.as_view(), name='recipe_delete'),
    path('cooked/<int:recipe_id>/review/', views.review_upsert, name='review_upsert'),
    path('reviews/<int:review_id>/delete/', views.review_delete, name='review_delete'),

    # Tuoyu
    path('u/<str:username>/', views.profile, name='profile'),
    path('ingredient_search/', views.ingredient_search, name='ingredient_search'),
    path('ingredients/filter/', views.ingredient_filter, name='ingredient_filter'),
    path('follow/<str:username>/toggle/', views.follow_toggle, name='follow_toggle'),
    path('cooked/<int:recipe_id>/status/', views.status_toggle, name='status_toggle'),
    path('wishlist/', views.wishlist, name='wishlist'),
]
