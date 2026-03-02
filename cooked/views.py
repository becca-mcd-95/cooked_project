from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def home(request):
    context_dict = {'boldmessage': 'Under construction'}
    return render(request, 'cooked/home.html', context=context_dict)

# def login_signup(request):
#     return HttpResponse("We're Cooked! - login/signup")

# def user_profile(request):
#     return HttpResponse("We're Cooked! - User Profile")