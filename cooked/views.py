from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import SignUpForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required

def home(request):
    context_dict = {'boldmessage': 'Under construction'}
    return render(request, 'cooked/home.html', context=context_dict)

def login(request):
    return render(request, 'cooked/login.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('cooked:user_profile')
    else:
        form = SignUpForm()
    return render(request, 'cooked/signup.html', {'form': form})

@login_required
def user_profile(request):
    profile = request.user.profile
    return render(request, 'cooked/user_profile.html', {'profile': profile})

@login_required
def edit_profile(request):
    return render(request, 'cooked/edit_profile.html')