from django.contrib import admin

from .models import Country, Follow, Ingredient, Profile, RecipeStatus


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


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "display_name", "updated_at")
    search_fields = ("user__username", "display_name", "bio")
