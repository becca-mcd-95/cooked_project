from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from social.filter_options import DEFAULT_CUISINES, DEFAULT_OCCASIONS, english_only, merge_defaults
from .forms import RecipeForm, ReviewForm
from .models import Recipe, Review
from .uploads import delete_recipe_photo, save_recipe_photo


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
            from social.models import Country

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
                from social.models import RecipeStatus

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
    template_name = "recipes/recipe_detail.html"
    context_object_name = "recipe"

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
            from social.models import RecipeStatus

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
    template_name = "recipes/create_recipe.html"

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
        return reverse_lazy("recipe_detail", kwargs={"pk": self.object.pk})


@method_decorator(login_required, name="dispatch")
class RecipeUpdateView(UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "recipes/create_recipe.html"

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
        return reverse_lazy("recipe_detail", kwargs={"pk": self.object.pk})


@method_decorator(login_required, name="dispatch")
class RecipeDeleteView(DeleteView):
    model = Recipe
    template_name = "recipes/confirm_delete.html"
    success_url = reverse_lazy("recipe_list")

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
            from social.models import RecipeStatus

            RecipeStatus.objects.get_or_create(user=request.user, recipe=recipe, status=RecipeStatus.STATUS_COOKED)

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
