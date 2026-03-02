from django.urls import path
from cooked import views

app_name = 'cooked'

urlpatterns = [
    path('', views.home, name='home'),
]