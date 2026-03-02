from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def home(request):
    return HttpResponse("We're Cooked! - Homepage")

def login_signup(request):
    return HttpResponse("We're Cooked! - login/signup")

def user_profile(request):
    return HttpResponse("We're Cooked! - User Profile")