from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from social.models import Ingredient

from .models import Recipe, Review


class RecipeModuleTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username="u1", password="pass12345")
        self.other = User.objects.create_user(username="u2", password="pass12345")
        self.egg = Ingredient.objects.create(name="Egg", category="Dairy")

    def test_recipe_create_requires_login(self):
        url = reverse("recipe_create")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)

    def test_recipe_create(self):
        self.client.login(username="u1", password="pass12345")
        url = reverse("recipe_create")
        photo = SimpleUploadedFile("photo.jpg", b"\xff\xd8\xff\xd9", content_type="image/jpeg")
        resp = self.client.post(
            url,
            {
                "title": "Test recipe",
                "cooking_time_minutes": 10,
                "instructions": "Step 1\nStep 2",
                "ingredients": [self.egg.id],
                "photo": photo,
            },
        )
        self.assertEqual(resp.status_code, 302)
        recipe = Recipe.objects.get(title="Test recipe")
        self.assertEqual(recipe.author_id, self.user.id)
        self.assertEqual(recipe.ingredients.count(), 1)
        self.assertTrue(recipe.photo_path.startswith("uploads/recipes/"))
        abs_path = (Path(settings.BASE_DIR) / "static" / recipe.photo_path).resolve()
        self.assertTrue(abs_path.exists())
        abs_path.unlink(missing_ok=True)

    def test_review_upsert_validation(self):
        recipe = Recipe.objects.create(title="R", author=self.user, instructions="x", cooking_time_minutes=1)
        self.client.login(username="u2", password="pass12345")
        url = reverse("review_upsert", kwargs={"recipe_id": recipe.id})
        bad = self.client.post(url, {"rating": 6, "comment": "nope"})
        self.assertEqual(bad.status_code, 400)

    def test_review_upsert_create_and_update(self):
        recipe = Recipe.objects.create(title="R", author=self.user, instructions="x", cooking_time_minutes=1)
        self.client.login(username="u2", password="pass12345")
        url = reverse("review_upsert", kwargs={"recipe_id": recipe.id})

        r1 = self.client.post(url, {"rating": 5, "comment": "great"})
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(Review.objects.filter(recipe=recipe, user=self.other).count(), 1)

        r2 = self.client.post(url, {"rating": 4, "comment": "updated"})
        self.assertEqual(r2.status_code, 200)
        rv = Review.objects.get(recipe=recipe, user=self.other)
        self.assertEqual(rv.rating, 4)
        self.assertEqual(rv.comment, "updated")
