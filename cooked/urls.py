from django.urls import path
from cooked import views
from django.contrib.auth import views as auth_views

app_name = 'cooked'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('user_profile', views.user_profile, name='user_profile'),
    path('logout/', views.logout_view, name='logout'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
]