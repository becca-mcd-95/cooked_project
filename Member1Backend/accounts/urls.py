from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", views.signup, name="signup"),
    path("profile/", views.profile, name="account_profile"),
    path("profile/edit/", views.profile_edit, name="account_profile_edit"),
    path("", include("django.contrib.auth.urls")),
]

