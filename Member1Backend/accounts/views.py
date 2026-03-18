from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from recipes.models import Recipe
from social.models import Profile, RecipeStatus

from .forms import ProfileEditForm, SignUpForm


@require_http_methods(["GET", "POST"])
def signup(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect("recipe_list")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            authed = authenticate(username=getattr(user, "username", ""), password=form.cleaned_data.get("password1"))
            if authed is not None:
                login(request, authed)
            messages.success(request, "Account created. Welcome!")
            return redirect("recipe_list")
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request: HttpRequest):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    created_recipes = (
        Recipe.objects.filter(author=request.user)
        .select_related("origin_country")
        .order_by("-created_at")[:20]
    )
    cooked_recipes = (
        Recipe.objects.filter(statuses__user=request.user, statuses__status=RecipeStatus.STATUS_COOKED)
        .select_related("origin_country", "author")
        .order_by("-statuses__created_at")[:20]
    )
    return render(
        request,
        "accounts/profile.html",
        {
            "profile_obj": profile_obj,
            "created_recipes": created_recipes,
            "cooked_recipes": cooked_recipes,
            "edit_form": ProfileEditForm(user=request.user, profile=profile_obj),
        },
    )


@require_http_methods(["GET", "POST"])
@login_required
def profile_edit(request: HttpRequest):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileEditForm(user=request.user, profile=profile_obj, data=request.POST)
        if form.is_valid():
            request.user.username = form.cleaned_data["username"]
            request.user.save(update_fields=["username"])

            profile_obj.display_name = (form.cleaned_data.get("display_name") or "").strip()
            profile_obj.bio = (form.cleaned_data.get("bio") or "").strip()
            profile_obj.save(update_fields=["display_name", "bio", "updated_at"])

            messages.success(request, "Profile updated.")
            return redirect("account_profile")
    else:
        form = ProfileEditForm(user=request.user, profile=profile_obj)

    return render(request, "accounts/edit_profile.html", {"profile_obj": profile_obj, "form": form})

