from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models import Count
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET, require_POST

from recipes.models import Recipe, Review

from .filter_options import DEFAULT_CUISINES, DEFAULT_OCCASIONS, english_only, has_cjk, merge_defaults
from .forms import ProfileEditForm
from .models import Country, Follow, Ingredient, Profile, RecipeStatus
from .uploads import delete_avatar, delete_cover, save_avatar, save_cover


@require_GET
def profile(request: HttpRequest, username: str):
    profile_user = get_object_or_404(User, username=username)
    profile_obj, _ = Profile.objects.get_or_create(user=profile_user)
    recipes = (
        Recipe.objects.filter(author=profile_user)
        .select_related("author", "origin_country")
        .prefetch_related("ingredients", "reviews")
        .order_by("-created_at")[:24]
    )
    followers = Follow.objects.filter(following=profile_user).count()
    following = Follow.objects.filter(follower=profile_user).count()
    cooked_count = RecipeStatus.objects.filter(user=profile_user, status=RecipeStatus.STATUS_COOKED).count()
    to_try_count = RecipeStatus.objects.filter(user=profile_user, status=RecipeStatus.STATUS_WISHLIST).count()
    reviews_count = Review.objects.filter(user=profile_user).count()
    recent_posts = (
        Review.objects.select_related("recipe")
        .filter(user=profile_user)
        .filter(Q(pinned=True) | ~Q(comment=""))
        .order_by("-pinned", "-created_at")[:4]
    )

    chef_level = 1
    if cooked_count >= 40:
        chef_level = 5
    elif cooked_count >= 25:
        chef_level = 4
    elif cooked_count >= 15:
        chef_level = 3
    elif cooked_count >= 5:
        chef_level = 2
    chef_slots = [i <= chef_level for i in range(1, 6)]

    is_following = False
    if request.user.is_authenticated and request.user.id != profile_user.id:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()

    edit_form = None
    if request.user.is_authenticated and request.user.id == profile_user.id:
        edit_form = ProfileEditForm(user=request.user, profile=profile_obj)

    return render(
        request,
        "social/profile.html",
        {
            "profile_user": profile_user,
            "profile": profile_obj,
            "recipes": recipes,
            "followers": followers,
            "following": following,
            "is_following": is_following,
            "cooked_count": cooked_count,
            "to_try_count": to_try_count,
            "reviews_count": reviews_count,
            "recent_posts": recent_posts,
            "chef_slots": chef_slots,
            "edit_form": edit_form,
        },
    )


@require_POST
@login_required
def profile_edit(request: HttpRequest):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    form = ProfileEditForm(user=request.user, profile=profile_obj, data=request.POST, files=request.FILES)
    if not form.is_valid():
        followers = Follow.objects.filter(following=request.user).count()
        following = Follow.objects.filter(follower=request.user).count()
        cooked_count = RecipeStatus.objects.filter(user=request.user, status=RecipeStatus.STATUS_COOKED).count()
        to_try_count = RecipeStatus.objects.filter(user=request.user, status=RecipeStatus.STATUS_WISHLIST).count()
        reviews_count = Review.objects.filter(user=request.user).count()
        recent_posts = (
            Review.objects.select_related("recipe")
            .filter(user=request.user)
            .filter(Q(pinned=True) | ~Q(comment=""))
            .order_by("-pinned", "-created_at")[:4]
        )
        chef_level = 1
        if cooked_count >= 40:
            chef_level = 5
        elif cooked_count >= 25:
            chef_level = 4
        elif cooked_count >= 15:
            chef_level = 3
        elif cooked_count >= 5:
            chef_level = 2
        chef_slots = [i <= chef_level for i in range(1, 6)]

        recipes = (
            Recipe.objects.filter(author=request.user)
            .select_related("author", "origin_country")
            .prefetch_related("ingredients", "reviews")
            .order_by("-created_at")[:24]
        )
        return render(
            request,
            "social/profile.html",
            {
                "profile_user": request.user,
                "profile": profile_obj,
                "recipes": recipes,
                "followers": followers,
                "following": following,
                "is_following": False,
                "cooked_count": cooked_count,
                "to_try_count": to_try_count,
                "reviews_count": reviews_count,
                "recent_posts": recent_posts,
                "chef_slots": chef_slots,
                "edit_form": form,
                "open_edit_modal": True,
            },
            status=400,
        )

    new_username = form.cleaned_data["username"]
    profile_obj.display_name = (form.cleaned_data.get("display_name") or "").strip()
    profile_obj.bio = (form.cleaned_data.get("bio") or "").strip()

    avatar = form.cleaned_data.get("avatar")
    if avatar:
        try:
            old = profile_obj.avatar_path
            profile_obj.avatar_path = save_avatar(avatar)
            if old and old != profile_obj.avatar_path:
                delete_avatar(old)
        except ValueError as e:
            form.add_error("avatar", str(e))

    cover = form.cleaned_data.get("cover")
    if cover:
        try:
            old = profile_obj.cover_path
            profile_obj.cover_path = save_cover(cover)
            if old and old != profile_obj.cover_path:
                delete_cover(old)
        except ValueError as e:
            form.add_error("cover", str(e))

    if form.errors:
        followers = Follow.objects.filter(following=request.user).count()
        following = Follow.objects.filter(follower=request.user).count()
        cooked_count = RecipeStatus.objects.filter(user=request.user, status=RecipeStatus.STATUS_COOKED).count()
        to_try_count = RecipeStatus.objects.filter(user=request.user, status=RecipeStatus.STATUS_WISHLIST).count()
        reviews_count = Review.objects.filter(user=request.user).count()
        recent_posts = (
            Review.objects.select_related("recipe")
            .filter(user=request.user)
            .filter(Q(pinned=True) | ~Q(comment=""))
            .order_by("-pinned", "-created_at")[:4]
        )
        chef_level = 1
        if cooked_count >= 40:
            chef_level = 5
        elif cooked_count >= 25:
            chef_level = 4
        elif cooked_count >= 15:
            chef_level = 3
        elif cooked_count >= 5:
            chef_level = 2
        chef_slots = [i <= chef_level for i in range(1, 6)]

        recipes = (
            Recipe.objects.filter(author=request.user)
            .select_related("author", "origin_country")
            .prefetch_related("ingredients", "reviews")
            .order_by("-created_at")[:24]
        )
        return render(
            request,
            "social/profile.html",
            {
                "profile_user": request.user,
                "profile": profile_obj,
                "recipes": recipes,
                "followers": followers,
                "following": following,
                "is_following": False,
                "cooked_count": cooked_count,
                "to_try_count": to_try_count,
                "reviews_count": reviews_count,
                "recent_posts": recent_posts,
                "chef_slots": chef_slots,
                "edit_form": form,
                "open_edit_modal": True,
            },
            status=400,
        )

    request.user.username = new_username
    request.user.save(update_fields=["username"])
    profile_obj.save(update_fields=["display_name", "bio", "avatar_path", "cover_path", "updated_at"])

    return redirect("profile", username=new_username)


@require_GET
def ingredient_search(request: HttpRequest):
    ingredients = Ingredient.objects.all().order_by("name")
    countries_qs = Country.objects.all().order_by("name")
    countries = [c for c in countries_qs if not has_cjk(c.name)]
    if not countries:
        countries = list(countries_qs)

    cuisines_qs = (
        Recipe.objects.exclude(cuisine="")
        .values_list("cuisine", flat=True)
        .distinct()
        .order_by("cuisine")[:200]
    )
    cuisines = merge_defaults(values=english_only(cuisines_qs), defaults=DEFAULT_CUISINES, limit=60)

    occasions_qs = (
        Recipe.objects.exclude(occasion="")
        .values_list("occasion", flat=True)
        .distinct()
        .order_by("occasion")[:200]
    )
    occasions = merge_defaults(values=english_only(occasions_qs), defaults=DEFAULT_OCCASIONS, limit=60)

    return render(
        request,
        "social/search.html",
        {
            "ingredients": ingredients,
            "countries": countries,
            "cuisines": cuisines,
            "occasions": occasions,
            "mode": request.GET.get("mode", "strict"),
        },
    )


@require_GET
def ingredient_filter(request: HttpRequest):
    raw_ids = (request.GET.get("ingredients") or "").split(",")
    ids = [int(x) for x in raw_ids if x.isdigit()]
    mode = request.GET.get("mode") or "strict"

    country_ids = [int(x) for x in request.GET.getlist("country") if (x or "").isdigit()]
    cuisines = [x.strip() for x in request.GET.getlist("cuisine") if (x or "").strip()]
    difficulties = [int(x) for x in request.GET.getlist("difficulty") if (x or "").isdigit()]
    occasions = [x.strip() for x in request.GET.getlist("occasion") if (x or "").strip()]

    qs = Recipe.objects.select_related("author", "origin_country").prefetch_related("ingredients", "reviews")

    if ids:
        if mode == "loose":
            qs = qs.filter(ingredients__id__in=ids).distinct()
        else:
            # "Strict" means every selected ingredient is required (recipes may still have extra ingredients).
            required = len(ids)
            qs = (
                qs.filter(ingredients__id__in=ids)
                .annotate(match_count=Count("ingredients", filter=Q(ingredients__id__in=ids), distinct=True))
                .filter(match_count=required)
                .distinct()
            )
    else:
        qs = qs.none()

    if country_ids:
        qs = qs.filter(origin_country_id__in=country_ids)
    if cuisines:
        qs = qs.filter(cuisine__in=cuisines)
    if difficulties:
        qs = qs.filter(difficulty__in=difficulties)
    if occasions:
        qs = qs.filter(occasion__in=occasions)

    html = render_to_string("social/_filter_results_list.html", {"recipes": qs[:60]}, request=request)
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
    wishlist_count = RecipeStatus.objects.filter(recipe=recipe, status=RecipeStatus.STATUS_WISHLIST).count()
    cooked_count = RecipeStatus.objects.filter(recipe=recipe, status=RecipeStatus.STATUS_COOKED).count()
    return JsonResponse(
        {
            "ok": True,
            "active": active,
            "wishlist": wishlist_active,
            "cooked": cooked_active,
            "wishlist_count": wishlist_count,
            "cooked_count": cooked_count,
        }
    )


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
