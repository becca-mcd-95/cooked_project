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

from cooked.forms import SignUpForm, ProfileForm, RecipeForm, ReviewForm
from cooked.models import Recipe, Review, Country, Follow, Ingredient, RecipeStatus
# from static.uploads.recipes import delete_recipe_photo, save_recipe_photo

# Becca views

def home(request):
    return render(request, 'cooked/home.html')

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
        if form.is_valid():
            form.save()
            return redirect('cooked:user_profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'cooked/edit_profile.html', {'form': form})

def search_users(request):
    q = request.GET.get("q", "")
    users = User.objects.filter(username__icontains=q) if q else []
    return render(request, "cooked/search_users.html", {"query": q, "users": users})

# temporary view for hardcoding content to user_profile, again can be removed 

def demo_profile(request):
    return render(request, 'cooked/user_profile_demo.html')

# Yanyan views 

class RecipeListView(ListView):
    model = Recipe
    template_name = "recipes/recipe_list.html"
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
        return qs


class RecipeDetailView(DetailView):
    model = Recipe
    template_name = "recipe_detail.html"
    context_object_name = "recipe"

    def get_queryset(self):
        return Recipe.objects.select_related("author", "origin_country").prefetch_related("ingredients", "reviews__user")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["review_form"] = ReviewForm()
        if self.request.user.is_authenticated:
            ctx["my_review"] = Review.objects.filter(recipe=self.object, user=self.request.user).first()
            from models import RecipeStatus

            ctx["wishlist_active"] = RecipeStatus.objects.filter(
                user=self.request.user, recipe=self.object, status=RecipeStatus.STATUS_WISHLIST
            ).exists()
            ctx["cooked_active"] = RecipeStatus.objects.filter(
                user=self.request.user, recipe=self.object, status=RecipeStatus.STATUS_COOKED
            ).exists()
        else:
            ctx["my_review"] = None
            ctx["wishlist_active"] = False
            ctx["cooked_active"] = False
        return ctx


@method_decorator(login_required, name="dispatch")
class RecipeCreateView(CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "create_recipe.html"

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
        return reverse_lazy("recipe_detail", kwargs={"id": self.object.id})


@method_decorator(login_required, name="dispatch")
class RecipeUpdateView(UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "create_recipe.html"

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
        return reverse_lazy("recipe_detail", kwargs={"id": self.object.id})


@method_decorator(login_required, name="dispatch")
class RecipeDeleteView(DeleteView):
    model = Recipe
    template_name = "confirm_delete.html"

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
    
    def get_success_url(self):
        return reverse_lazy("cooked:recipe_list")

@require_POST
@login_required
def review_upsert(request: HttpRequest, recipe_id: int):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    form = ReviewForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)

    rating = form.cleaned_data["rating"]
    comment = form.cleaned_data["comment"]

    with transaction.atomic():
        review = Review.objects.filter(recipe=recipe, user=request.user).first()
        if review:
            review.rating = rating
            review.comment = comment
            review.save(update_fields=["rating", "comment", "updated_at"])
            action = "updated"
        else:
            try:
                review = Review.objects.create(recipe=recipe, user=request.user, rating=rating, comment=comment)
            except IntegrityError:
                review = Review.objects.get(recipe=recipe, user=request.user)
                review.rating = rating
                review.comment = comment
                review.save(update_fields=["rating", "comment", "updated_at"])
            action = "created"

    html = render_to_string("recipes/_review_item.html", {"review": review, "user": request.user}, request=request)
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
    return render(
        request,
        "cooked/ingredient_search.html",
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

    html = render_to_string("cooked/_filter_results.html", {"recipes": qs[:60]}, request=request)
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
