from django.contrib import admin
from cooked.models import Recipe, Review,  Country, Follow, Ingredient, RecipeStatus

# Yanyan 

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

# Tuoyu

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category")
    search_fields = ("name", "category")


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "iso2", "map_code")
    search_fields = ("name", "iso2", "map_code")


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("id", "follower", "following", "created_at")
    search_fields = ("follower__username", "following__username")


@admin.register(RecipeStatus)
class RecipeStatusAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "recipe__title")
