from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.contrib.auth import login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST, require_GET
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.db.models import Count, F, Q
from django.db import IntegrityError, transaction
from django.utils import timezone

from cooked.forms import SignUpForm, ProfileForm, RecipeForm, ReviewForm, UserForm
from cooked.models import Recipe, Review, Country, Follow, Ingredient, RecipeStatus
from .filter_options import DEFAULT_CUISINES, DEFAULT_OCCASIONS, english_only, merge_defaults, has_cjk
from cooked.uploads import delete_recipe_photo, save_recipe_photo

# Becca views

def home(request):
    new_recipes = Recipe.objects.select_related('author').order_by('-created_at')[:8]
    popular_recipes = Recipe.objects.select_related('author').annotate(
        review_count=Count('reviews')
    ).order_by('-review_count', '-created_at')[:8]
    popular_reviews = Review.objects.select_related('user', 'recipe').order_by('-created_at')[:6]
    
    return render(request, 'cooked/home.html', {
        'new_recipes': new_recipes,
        'popular_recipes': popular_recipes,
        'popular_reviews': popular_reviews})

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('cooked:user_profile')
    else:
        form = AuthenticationForm()
    return render(request, 'cooked/login.html', {'form': form})

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
    cooked_recipes = list(Recipe.objects.filter(
        statuses__user=request.user,
        statuses__status=RecipeStatus.STATUS_COOKED).select_related('author'))

    wishlist_recipes = Recipe.objects.filter(
        statuses__user = request.user,
        statuses__status = RecipeStatus.STATUS_WISHLIST
    ).select_related('author', 'origin_country').order_by('-statuses__created_at')

    recent_reviews = Review.objects.filter(
        user = request.user
    ).select_related('recipe').order_by('-created_at')[:4]

    following_count = Follow.objects.filter(follower=request.user).count()
    follower_count = Follow.objects.filter(following=request.user).count()
    return render(request, 'cooked/user_profile.html', {
        'profile': profile, 'cooked_recipes':cooked_recipes, 'wishlist_recipes':wishlist_recipes, 'cooked_count': len(cooked_recipes),
        'wishlist_count': wishlist_recipes.count(), 'recent_reviews': recent_reviews, 'review_count':Review.objects.filter(user=request.user).count(),
        'following_count': following_count,'follower_count':follower_count, 'is_following':False})

@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserForm(request.POST, instance=request.user)
        if form.is_valid() and user_form.is_valid():
            form.save()
            user_form.save()
            return redirect('cooked:user_profile')
    else:
        form = ProfileForm(instance=profile)
        user_form = UserForm(instance=request.user)
    return render(request, 'cooked/edit_profile.html', {'form': form, 'user_form': user_form,'profile': profile})

def search_users(request):
    q = request.GET.get("q", "")
    users = User.objects.filter(username__icontains=q) if q else []
    return render(request, "cooked/search.html", {"query": q, "users": users})

def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile = profile_user.profile

    cooked_recipes = list(Recipe.objects.filter(
        statuses__user=profile_user,
        statuses__status=RecipeStatus.STATUS_COOKED
    ).select_related('author'))

    following_count = Follow.objects.filter(follower=profile_user).count()
    followers_count = Follow.objects.filter(following=profile_user).count()

    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(
            follower=request.user, following=profile_user
        ).exists()

    return render(request, 'cooked/user_profile.html', {
        'profile': profile,
        'cooked_recipes': cooked_recipes,
        'cooked_count': len(cooked_recipes),
        'wishlist_count': 0,
        'review_count': Review.objects.filter(user=profile_user).count(),
        'recent_reviews': Review.objects.filter(user=profile_user).select_related('recipe').order_by('-created_at')[:4],
        'following_count': following_count,
        'followers_count': followers_count,
        'is_following': is_following,
    })

# Yanyan views 

class RecipeListView(ListView):
    model = Recipe
    template_name = "cooked/recipe_list.html"
    context_object_name = "recipes"
    paginate_by = 12

    def get_queryset(self):
        qs = (
            Recipe.objects.select_related("author", "origin_country")
            .prefetch_related("ingredients")
            .prefetch_related("reviews")
        )
        q = (self.request.GET.get("q") or "").strip()
        if q:
            qs = qs.filter(title__icontains=q)

        country_ids = [int(x) for x in self.request.GET.getlist("country") if (x or "").isdigit()]
        cuisines = [x.strip() for x in self.request.GET.getlist("cuisine") if (x or "").strip()]
        difficulties = [int(x) for x in self.request.GET.getlist("difficulty") if (x or "").isdigit()]
        occasions = [x.strip() for x in self.request.GET.getlist("occasion") if (x or "").strip()]

        if country_ids:
            qs = qs.filter(origin_country_id__in=country_ids)
        if cuisines:
            qs = qs.filter(cuisine__in=cuisines)
        if difficulties:
            qs = qs.filter(difficulty__in=difficulties)
        if occasions:
            qs = qs.filter(occasion__in=occasions)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = (self.request.GET.get("q") or "").strip()
        ctx["q"] = q
        ctx["q_terms"] = [x for x in q.replace(",", " ").split() if x][:8]

        if q:
            from cooked.models import Country

            ctx["countries"] = list(Country.objects.all().order_by("name")[:80])
            cuisines_qs = (
                Recipe.objects.exclude(cuisine="")
                .values_list("cuisine", flat=True)
                .distinct()
                .order_by("cuisine")[:200]
            )
            occasions_qs = (
                Recipe.objects.exclude(occasion="")
                .values_list("occasion", flat=True)
                .distinct()
                .order_by("occasion")[:200]
            )
            ctx["cuisines"] = merge_defaults(values=english_only(cuisines_qs), defaults=DEFAULT_CUISINES, limit=60)
            ctx["occasions"] = merge_defaults(values=english_only(occasions_qs), defaults=DEFAULT_OCCASIONS, limit=60)

            ctx["selected_country_ids"] = {int(x) for x in self.request.GET.getlist("country") if (x or "").isdigit()}
            ctx["selected_cuisines"] = {x for x in self.request.GET.getlist("cuisine") if (x or "").strip()}
            ctx["selected_difficulties"] = {int(x) for x in self.request.GET.getlist("difficulty") if (x or "").isdigit()}
            ctx["selected_occasions"] = {x for x in self.request.GET.getlist("occasion") if (x or "").strip()}
            qd = self.request.GET.copy()
            qd.pop("page", None)
            ctx["search_querystring"] = qd.urlencode()

        browse = (self.request.GET.get("browse") or "country").strip().lower()
        if browse not in {"country", "cuisine", "difficulty", "occasion"}:
            browse = "country"
        ctx["browse"] = browse

        if not q:
            base = (
                Recipe.objects.select_related("author", "origin_country")
                .prefetch_related("ingredients", "reviews")
                .prefetch_related("statuses")
            )
            if browse == "country":
                base = base.filter(origin_country__isnull=False)
            elif browse == "cuisine":
                base = base.exclude(cuisine="")
            elif browse == "difficulty":
                base = base.filter(difficulty__isnull=False)
            elif browse == "occasion":
                base = base.exclude(occasion="")

            week_ago = timezone.now() - timezone.timedelta(days=7)
            base = base.annotate(
                reviews_count=Count("reviews", distinct=True),
                wishlist_count=Count(
                    "statuses",
                    filter=Q(statuses__status="wishlist"),
                    distinct=True,
                ),
                cooked_count=Count(
                    "statuses",
                    filter=Q(statuses__status="cooked"),
                    distinct=True,
                ),
                reviews_week=Count(
                    "reviews",
                    filter=Q(reviews__created_at__gte=week_ago),
                    distinct=True,
                ),
            )

            ctx["new_uploads"] = list(base.order_by("-created_at")[:6])
            ctx["popular_week"] = list(base.order_by("-reviews_week", "-reviews_count", "-created_at")[:6])

            ctx["to_cook"] = []
            ctx["my_wishlist_ids"] = []
            ctx["my_cooked_ids"] = []
            if self.request.user.is_authenticated:
                from cooked.models import RecipeStatus

                to_cook_qs = (
                    Recipe.objects.select_related("author", "origin_country")
                    .prefetch_related("ingredients", "reviews")
                    .prefetch_related("statuses")
                    .filter(statuses__user=self.request.user, statuses__status=RecipeStatus.STATUS_WISHLIST)
                    .annotate(
                        reviews_count=Count("reviews", distinct=True),
                        wishlist_count=Count(
                            "statuses",
                            filter=Q(statuses__status="wishlist"),
                            distinct=True,
                        ),
                        cooked_count=Count(
                            "statuses",
                            filter=Q(statuses__status="cooked"),
                            distinct=True,
                        ),
                    )
                    .order_by("-statuses__created_at")
                )
                if browse == "country":
                    to_cook_qs = to_cook_qs.filter(origin_country__isnull=False)
                elif browse == "cuisine":
                    to_cook_qs = to_cook_qs.exclude(cuisine="")
                elif browse == "difficulty":
                    to_cook_qs = to_cook_qs.filter(difficulty__isnull=False)
                elif browse == "occasion":
                    to_cook_qs = to_cook_qs.exclude(occasion="")
                ctx["to_cook"] = list(to_cook_qs[:6])

                ids = {r.id for r in ctx["new_uploads"]} | {r.id for r in ctx["popular_week"]} | {r.id for r in ctx["to_cook"]}
                statuses = RecipeStatus.objects.filter(user=self.request.user, recipe_id__in=list(ids)).values_list(
                    "recipe_id",
                    "status",
                )
                wish = []
                cooked = []
                for rid, st in statuses:
                    if st == RecipeStatus.STATUS_WISHLIST:
                        wish.append(rid)
                    elif st == RecipeStatus.STATUS_COOKED:
                        cooked.append(rid)
                ctx["my_wishlist_ids"] = wish
                ctx["my_cooked_ids"] = cooked

        return ctx


class RecipeDetailView(DetailView):
    model = Recipe
    template_name = "cooked/recipe_detail.html"
    context_object_name = "recipe"
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        return Recipe.objects.select_related("author", "origin_country").prefetch_related("ingredients", "reviews__user")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["review_form"] = ReviewForm()
        avg = self.object.avg_rating()
        level = max(0, min(5, int(avg)))
        ctx["avg_level_slots"] = [i <= level for i in range(1, 6)]
        if self.request.user.is_authenticated:
            ctx["my_review"] = Review.objects.filter(recipe=self.object, user=self.request.user).first()
            from cooked.models import RecipeStatus

            ctx["wishlist_active"] = RecipeStatus.objects.filter(
                user=self.request.user, recipe=self.object, status=RecipeStatus.STATUS_WISHLIST
            ).exists()
            ctx["cooked_active"] = RecipeStatus.objects.filter(
                user=self.request.user, recipe=self.object, status=RecipeStatus.STATUS_COOKED
            ).exists()
            cooked_row = RecipeStatus.objects.filter(
                user=self.request.user,
                recipe=self.object,
                status=RecipeStatus.STATUS_COOKED,
            ).only("created_at").first()
            ctx["cooked_on"] = cooked_row.created_at if cooked_row else None
        else:
            ctx["my_review"] = None
            ctx["wishlist_active"] = False
            ctx["cooked_active"] = False
            ctx["cooked_on"] = None
        return ctx


@method_decorator(login_required, name="dispatch")
class RecipeCreateView(CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "cooked/create_recipe.html"

    def form_valid(self, form):
        photo = form.cleaned_data.get("photo")
        obj = form.save(commit=False)
        obj.author = self.request.user
        if photo:
            try:
                obj.photo_path = save_recipe_photo(photo)
            except ValueError as e:
                form.add_error("photo", str(e))
                return self.form_invalid(form)
        obj.save()
        form.save_m2m()
        self.object = obj
        messages.success(self.request, "Recipe created.")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy("cooked:recipe_detail", kwargs={"pk": self.object.pk})


@method_decorator(login_required, name="dispatch")
class RecipeUpdateView(UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "cooked/create_recipe.html"

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author_id != request.user.id:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        new_photo = form.cleaned_data.get("photo")
        old_photo_path = self.get_object().photo_path

        obj = form.save(commit=False)
        if new_photo:
            try:
                obj.photo_path = save_recipe_photo(new_photo)
            except ValueError as e:
                form.add_error("photo", str(e))
                return self.form_invalid(form)
        obj.save()
        form.save_m2m()
        self.object = obj

        if new_photo and old_photo_path and old_photo_path != obj.photo_path:
            delete_recipe_photo(old_photo_path)
        messages.success(self.request, "Recipe updated.")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy("cooked:recipe_detail", kwargs={"pk": self.object.pk})


@method_decorator(login_required, name="dispatch")
class RecipeDeleteView(DeleteView):
    model = Recipe
    template_name = "cooked/confirm_delete.html"
    success_url = reverse_lazy("cooked:recipe_list")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author_id != request.user.id:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.photo_path:
            delete_recipe_photo(obj.photo_path)
        messages.info(request, "Recipe deleted.")
        return super().delete(request, *args, **kwargs)


@require_POST
@login_required
def review_upsert(request: HttpRequest, recipe_id: int):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    form = ReviewForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)

    rating = form.cleaned_data["rating"]
    comment = form.cleaned_data["comment"]
    pinned = bool(form.cleaned_data.get("pinned"))
    mark_cooked = bool(form.cleaned_data.get("mark_cooked"))

    with transaction.atomic():
        review = Review.objects.filter(recipe=recipe, user=request.user).first()
        if review:
            review.rating = rating
            review.comment = comment
            review.pinned = pinned
            review.save(update_fields=["rating", "comment", "pinned", "updated_at"])
            action = "updated"
        else:
            try:
                review = Review.objects.create(recipe=recipe, user=request.user, rating=rating, comment=comment, pinned=pinned)
            except IntegrityError:
                review = Review.objects.get(recipe=recipe, user=request.user)
                review.rating = rating
                review.comment = comment
                review.pinned = pinned
                review.save(update_fields=["rating", "comment", "pinned", "updated_at"])
            action = "created"

        if mark_cooked:
            from cooked.models import RecipeStatus

            RecipeStatus.objects.get_or_create(user=request.user, recipe=recipe, status=RecipeStatus.STATUS_COOKED)

    html = render_to_string("cooked/_review_item.html", {"review": review, "user": request.user}, request=request)
    return JsonResponse(
        {
            "ok": True,
            "action": action,
            "review_id": review.id,
            "avg_rating": recipe.avg_rating(),
            "html": html,
        }
    )


@require_POST
@login_required
def review_delete(request: HttpRequest, review_id: int):
    review = get_object_or_404(Review, pk=review_id)
    if review.user_id != request.user.id and review.recipe.author_id != request.user.id:
        raise PermissionDenied
    recipe = review.recipe
    review.delete()
    return JsonResponse({"ok": True, "avg_rating": recipe.avg_rating()})

# Tuyou views 

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
        "cooked/ingredient_search.html",
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

    html = render_to_string("cooked/_filter_results_list.html", {"recipes": qs[:60]}, request=request)
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
    return render(request, "cooked/wishlist.html", {"recipes": recipes})


@login_required
def notifications(request: HttpRequest):
    reviews = (
        Review.objects.select_related("user", "recipe", "recipe__author")
        .filter(recipe__author=request.user)
        .exclude(user=request.user)
        .order_by("-created_at")[:60]
    )
    return render(request, "cooked/notifications.html", {"reviews": reviews})


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
        "cooked/world_map.html",
        {
            "region_values": region_values,
            "code_to_name": code_to_name,
            "completed": completed,
            "completed_countries": completed_countries,
            "total_countries": total_countries,
        },
    )

