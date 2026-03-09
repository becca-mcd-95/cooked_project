from django.contrib import admin

from .models import Recipe, Review


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "cooking_time_minutes", "created_at")
    search_fields = ("title", "author__username")
    list_filter = ("created_at",)
    filter_horizontal = ("ingredients",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe", "user", "rating", "created_at")
    search_fields = ("recipe__title", "user__username")
    list_filter = ("rating", "created_at")

