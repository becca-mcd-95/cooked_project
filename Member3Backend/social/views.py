from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models import Count, F
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET, require_POST

from recipes.models import Recipe, Review

from .models import Country, Follow, Ingredient, RecipeStatus


@require_GET
def profile(request: HttpRequest, username: str):
    profile_user = get_object_or_404(User, username=username)
    recipes = (
        Recipe.objects.filter(author=profile_user)
        .select_related("author", "origin_country")
        .prefetch_related("ingredients", "reviews")
        .order_by("-created_at")[:24]
    )
    followers = Follow.objects.filter(following=profile_user).count()
    following = Follow.objects.filter(follower=profile_user).count()
    is_following = False
    if request.user.is_authenticated and request.user.id != profile_user.id:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()

    return render(
        request,
        "social/profile.html",
        {
            "profile_user": profile_user,
            "recipes": recipes,
            "followers": followers,
            "following": following,
            "is_following": is_following,
        },
    )


@require_GET
def ingredient_search(request: HttpRequest):
    ingredients = Ingredient.objects.all().order_by("name")
    return render(
        request,
        "social/search.html",
        {
            "ingredients": ingredients,
            "mode": request.GET.get("mode", "strict"),
        },
    )


@require_GET
def ingredient_filter(request: HttpRequest):
    raw_ids = (request.GET.get("ingredients") or "").split(",")
    ids = [int(x) for x in raw_ids if x.isdigit()]
    mode = request.GET.get("mode") or "strict"

    qs = Recipe.objects.select_related("author", "origin_country").prefetch_related("ingredients", "reviews")

    if ids:
        if mode == "loose":
            qs = qs.filter(ingredients__id__in=ids).distinct()
        else:
            qs = (
                qs.annotate(
                    total_count=Count("ingredients", distinct=True),
                    match_count=Count("ingredients", filter=Q(ingredients__id__in=ids), distinct=True),
                )
                .filter(total_count__gt=0)
                .filter(match_count=F("total_count"))
                .distinct()
            )
    else:
        qs = qs.none()

    html = render_to_string("social/_filter_results.html", {"recipes": qs[:60]}, request=request)
    return JsonResponse({"ok": True, "html": html, "count": qs.count()})


@require_POST
@login_required
def follow_toggle(request: HttpRequest, username: str):
    target = get_object_or_404(User, username=username)
    if target.id == request.user.id:
        return JsonResponse({"ok": False, "error": "You cannot follow yourself."}, status=400)

    existing = Follow.objects.filter(follower=request.user, following=target).first()
    if existing:
        existing.delete()
        following = False
    else:
        Follow.objects.create(follower=request.user, following=target)
        following = True

    followers = Follow.objects.filter(following=target).count()
    return JsonResponse({"ok": True, "following": following, "followers": followers})


@require_POST
@login_required
def status_toggle(request: HttpRequest, recipe_id: int):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    status = request.POST.get("status") or ""
    if status not in {RecipeStatus.STATUS_WISHLIST, RecipeStatus.STATUS_COOKED}:
        return JsonResponse({"ok": False, "error": "Invalid status."}, status=400)

    existing = RecipeStatus.objects.filter(user=request.user, recipe=recipe, status=status).first()
    if existing:
        existing.delete()
        active = False
    else:
        RecipeStatus.objects.create(user=request.user, recipe=recipe, status=status)
        active = True

    wishlist_active = RecipeStatus.objects.filter(
        user=request.user, recipe=recipe, status=RecipeStatus.STATUS_WISHLIST
    ).exists()
    cooked_active = RecipeStatus.objects.filter(
        user=request.user, recipe=recipe, status=RecipeStatus.STATUS_COOKED
    ).exists()
    return JsonResponse({"ok": True, "active": active, "wishlist": wishlist_active, "cooked": cooked_active})


@login_required
def wishlist(request: HttpRequest):
    recipes = (
        Recipe.objects.filter(statuses__user=request.user, statuses__status=RecipeStatus.STATUS_WISHLIST)
        .select_related("author", "origin_country")
        .prefetch_related("ingredients", "reviews")
        .order_by("-statuses__created_at")
    )
    return render(request, "social/wishlist.html", {"recipes": recipes})


@login_required
def notifications(request: HttpRequest):
    reviews = (
        Review.objects.select_related("user", "recipe", "recipe__author")
        .filter(recipe__author=request.user)
        .exclude(user=request.user)
        .order_by("-created_at")[:60]
    )
    return render(request, "social/notifications.html", {"reviews": reviews})


@require_GET
@login_required
def world_map(request: HttpRequest):
    rows = (
        RecipeStatus.objects.filter(
            user=request.user,
            status=RecipeStatus.STATUS_COOKED,
            recipe__origin_country__isnull=False,
        )
        .values(
            "recipe__origin_country__id",
            "recipe__origin_country__name",
            "recipe__origin_country__iso2",
            "recipe__origin_country__map_code",
        )
        .annotate(count=Count("id"))
        .order_by("recipe__origin_country__name")
    )

    region_values: dict[str, int] = {}
    code_to_name: dict[str, str] = {}
    completed = []
    for r in rows:
        iso2 = (r.get("recipe__origin_country__iso2") or "").upper()
        map_code = (r.get("recipe__origin_country__map_code") or "").upper()
        code = map_code or iso2
        if not code:
            continue
        count = int(r["count"])
        region_values[code] = region_values.get(code, 0) + count
        code_to_name[code] = r.get("recipe__origin_country__name") or code
        completed.append({"code": code, "name": code_to_name[code], "count": count})

    total_countries = Country.objects.count()
    completed_countries = len({r["recipe__origin_country__id"] for r in rows})

    return render(
        request,
        "social/world_map.html",
        {
            "region_values": region_values,
            "code_to_name": code_to_name,
            "completed": completed,
            "completed_countries": completed_countries,
            "total_countries": total_countries,
        },
    )
