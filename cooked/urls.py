from django.urls import path
from cooked import views

app_name = 'cooked'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('user_profile', views.user_profile, name='user_profile'),
]