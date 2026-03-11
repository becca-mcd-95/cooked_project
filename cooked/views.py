from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import SignUpForm, ProfileForm
from django.contrib.auth import login as auth_login, logout
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'cooked/home.html')

def login(request):
    return render(request, 'cooked/login.html')

def logout_view(request):
    logout(request)
    return redirect('cooked:home')

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
    profile = request.user.profile
    if request.method == 'POST':  
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('cooked:user_profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'cooked/edit_profile.html', {'form': form})