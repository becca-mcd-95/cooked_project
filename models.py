from __future__ import annotations

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg


class Recipe(models.Model):
    title = models.CharField(max_length=160, db_index=True)
    instructions = models.TextField(blank=True)
    cooking_time_minutes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    photo_path = models.CharField(max_length=255, blank=True, default="")
    origin_country = models.ForeignKey(
        "social.Country",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recipes",
    )

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recipes")
    ingredients = models.ManyToManyField("social.Ingredient", blank=True, related_name="recipes")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    def avg_rating(self) -> float:
        val = self.reviews.aggregate(v=Avg("rating")).get("v") or 0
        return round(float(val), 1)


class Review(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["recipe", "user"], name="uq_review_recipe_user"),
        ]

    def __str__(self) -> str:
        return f"{self.recipe_id}:{self.user_id} ({self.rating})"
