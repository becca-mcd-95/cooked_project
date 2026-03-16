from django.urls import path, include
from cooked import views
from django.contrib.auth import views as auth_views

app_name = 'cooked'

urlpatterns = [
    path('', views.home, name='home'), # Becca
    path('login/', views.login, name='login'), # Becca
    path('signup/', views.signup, name='signup'), # Becca
    path('user_profile', views.user_profile, name='user_profile'), # Becca
    path('logout/', views.logout_view, name='logout'), # Becca
    path('edit_profile/', views.edit_profile, name='edit_profile'), # Becca
    path('recipes/', views.RecipeListView.as_view(), name='recipe_list'), #Yanyan
    path('new_recipe/', views.RecipeCreateView.as_view(), name='recipe_create'), #Yanyan
    path('recipe/<int:id>/', views.RecipeDetailView.as_view(), name='recipe_detail'), #Yanyan
    path('edit_recipe/<int:id>/', views.RecipeUpdateView.as_view(), name='recipe_edit'), #Yanyan
    path('delete_recipe/<int:id>/', views.RecipeDeleteView.as_view(), name='recipe_delete'), #Yanyan
    path('recipe/<int:recipe_id>/review/', views.review_upsert, name='review_upsert'), # Tuoyu
    path('review/<int:review_id>/delete/', views.review_delete, name='review_delete'), # Tuoyu
    path('recipe/<int:recipe_id>/status/', views.status_toggle, name='status_toggle'), # Tuoyu
    path('search/', views.search_users, name='search_users'),
    path('ingredient_search/', views.ingredient_search, name='ingredient_search'),


]