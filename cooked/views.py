from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    context_dict = {'boldmessage': 'Under construction'}
    return render(request, 'cooked/home.html', context=context_dict)

def login(request):
    return render(request, 'cooked/login.html')

def signup(request):
    return render(request, 'cooked/signup.html')

def user_profile(request):
    return render(request, 'cooked/user_profile.html')