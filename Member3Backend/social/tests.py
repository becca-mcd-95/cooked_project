from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from recipes.models import Recipe

from .models import Country, Follow, Ingredient, RecipeStatus


class SocialModuleTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.u1 = User.objects.create_user(username="u1", password="pass12345")
        self.u2 = User.objects.create_user(username="u2", password="pass12345")

        self.egg = Ingredient.objects.create(name="Egg", category="Dairy")
        self.rice = Ingredient.objects.create(name="Rice", category="Staple")

        self.r1 = Recipe.objects.create(title="Egg only", author=self.u1, instructions="x", cooking_time_minutes=1)
        self.r1.ingredients.add(self.egg)
        self.r2 = Recipe.objects.create(title="Egg + rice", author=self.u1, instructions="x", cooking_time_minutes=1)
        self.r2.ingredients.add(self.egg, self.rice)

    def test_filter_strict(self):
        url = reverse("ingredient_filter")
        resp = self.client.get(url, {"ingredients": str(self.egg.id), "mode": "strict"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["count"], 1)

    def test_filter_loose(self):
        url = reverse("ingredient_filter")
        resp = self.client.get(url, {"ingredients": str(self.egg.id), "mode": "loose"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["count"], 2)

    def test_follow_toggle(self):
        self.client.login(username="u1", password="pass12345")
        url = reverse("follow_toggle", kwargs={"username": "u2"})
        r1 = self.client.post(url)
        self.assertEqual(r1.status_code, 200)
        self.assertTrue(Follow.objects.filter(follower=self.u1, following=self.u2).exists())

        r2 = self.client.post(url)
        self.assertEqual(r2.status_code, 200)
        self.assertFalse(Follow.objects.filter(follower=self.u1, following=self.u2).exists())

    def test_wishlist_toggle(self):
        self.client.login(username="u2", password="pass12345")
        url = reverse("status_toggle", kwargs={"recipe_id": self.r1.id})
        r1 = self.client.post(url, {"status": "wishlist"})
        self.assertEqual(r1.status_code, 200)
        self.assertTrue(
            RecipeStatus.objects.filter(user=self.u2, recipe=self.r1, status=RecipeStatus.STATUS_WISHLIST).exists()
        )
        r2 = self.client.post(url, {"status": "wishlist"})
        self.assertEqual(r2.status_code, 200)
        self.assertFalse(
            RecipeStatus.objects.filter(user=self.u2, recipe=self.r1, status=RecipeStatus.STATUS_WISHLIST).exists()
        )

    def test_world_map_requires_login(self):
        resp = self.client.get(reverse("world_map"))
        self.assertEqual(resp.status_code, 302)

    def test_world_map_highlights_cooked_countries(self):
        us = Country.objects.create(iso2="US", name="United States")
        self.r1.origin_country = us
        self.r1.save(update_fields=["origin_country"])

        RecipeStatus.objects.create(user=self.u2, recipe=self.r1, status=RecipeStatus.STATUS_COOKED)

        self.client.login(username="u2", password="pass12345")
        resp = self.client.get(reverse("world_map"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "World map")
        self.assertContains(resp, "\"US\": 1")
