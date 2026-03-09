from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

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
        return qs


class RecipeDetailView(DetailView):
    model = Recipe
    template_name = "recipes/recipe_detail.html"
    context_object_name = "recipe"

    def get_queryset(self):
        return Recipe.objects.select_related("author", "origin_country").prefetch_related("ingredients", "reviews__user")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["review_form"] = ReviewForm()
        if self.request.user.is_authenticated:
            ctx["my_review"] = Review.objects.filter(recipe=self.object, user=self.request.user).first()
            from social.models import RecipeStatus

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
