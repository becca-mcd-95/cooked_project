from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def home(request):
    context_dict = {'boldmessage': 'Under construction'}
    return render(request, 'cooked/home.html', context=context_dict)

def login_signup(request):
    return render(request, 'cooked/login_signup.html')

def user_profile(request):
    return render(request, 'cooked/user_profile.html')