from __future__ import annotations

from django.conf import settings
from django.db import models


class Ingredient(models.Model):
    name = models.CharField(max_length=80, unique=True, db_index=True)
    category = models.CharField(max_length=80, default="General")

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Country(models.Model):
    iso2 = models.CharField(max_length=2, unique=True, db_index=True, help_text="ISO 3166-1 alpha-2 code (e.g. US).")
    name = models.CharField(max_length=100, unique=True, db_index=True)
    map_code = models.CharField(max_length=8, blank=True, default="", help_text="Optional map library code override.")

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.iso2})"

    def code(self) -> str:
        return (self.map_code or self.iso2).upper()


class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following_set")
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followers_set")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["follower", "following"], name="uq_follow_pair"),
            models.CheckConstraint(condition=~models.Q(follower=models.F("following")), name="ck_no_self_follow"),
        ]

    def __str__(self) -> str:
        return f"{self.follower_id}->{self.following_id}"


class RecipeStatus(models.Model):
    STATUS_WISHLIST = "wishlist"
    STATUS_COOKED = "cooked"
    STATUS_CHOICES = [(STATUS_WISHLIST, "Wishlist"), (STATUS_COOKED, "Cooked")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recipe_statuses")
    recipe = models.ForeignKey("recipes.Recipe", on_delete=models.CASCADE, related_name="statuses")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "recipe", "status"], name="uq_recipe_status"),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.recipe_id}:{self.status}"
