from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.db.models import Avg
from django.core.validators import MaxValueValidator, MinValueValidator

# Becca models
# this class was written with help as a placeholder 
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # do we need username and name field? does that pull from database? 
    bio = models.TextField(max_length=400, blank=True)
    city = models.TextField(max_length=40, blank=True)
    profile_picture = models.ImageField(upload_to='profile_photos', blank=True, null=True)
    header_photo = models.ImageField(upload_to='header_photos', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# Member 2 models (Yanyan)

class Recipe(models.Model):
    title = models.CharField(max_length=160, db_index=True)
    instructions = models.TextField(blank=True)
    cooking_time_minutes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    photo_path = models.CharField(max_length=255, blank=True, default="")
    origin_country = models.ForeignKey(
        "cooked.Country",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recipes",
    )

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recipes")
    ingredients = models.ManyToManyField("cooked.Ingredient", blank=True, related_name="recipes")

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
        unique_together = ("recipe", "user")

    def __str__(self) -> str:
        return f"{self.recipe_id}:{self.user_id} ({self.rating})"

# Member 3 models (Tuoyu)

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
        unique_together = ("follower", "following")

    def __str__(self) -> str:
        return f"{self.follower_id}->{self.following_id}"


class RecipeStatus(models.Model):
    STATUS_WISHLIST = "wishlist"
    STATUS_COOKED = "cooked"
    STATUS_CHOICES = [(STATUS_WISHLIST, "Wishlist"), (STATUS_COOKED, "Cooked")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recipe_statuses")
    recipe = models.ForeignKey("cooked.Recipe", on_delete=models.CASCADE, related_name="statuses")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "recipe", "status")


    def __str__(self) -> str:
        return f"{self.user_id}:{self.recipe_id}:{self.status}"
