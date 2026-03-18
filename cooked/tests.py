from django.test import TestCase, Client
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from .models import Country, Follow, Ingredient, UserProfile, RecipeStatus
from cooked.models import Recipe, Review, Ingredient, Country, Follow, RecipeStatus



# Yanyan tests

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

    def test_homepage_authenticated_does_not_error(self):
        self.client.login(username="u1", password="pass12345")
        uk = Country.objects.create(iso2="GB", name="United Kingdom")
        recipe = Recipe.objects.create(
            title="R",
            author=self.user,
            instructions="x",
            cooking_time_minutes=1,
            origin_country=uk,
        )
        RecipeStatus.objects.create(user=self.user, recipe=recipe, status=RecipeStatus.STATUS_WISHLIST)
        resp = self.client.get(reverse("recipe_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Recipes")

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

# Tuoyu tests 

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
        self.assertEqual(data["count"], 2)

    def test_filter_loose(self):
        url = reverse("ingredient_filter")
        resp = self.client.get(url, {"ingredients": str(self.egg.id), "mode": "loose"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["count"], 2)

    def test_filter_strict_requires_all_selected_ingredients(self):
        url = reverse("ingredient_filter")
        resp = self.client.get(url, {"ingredients": f"{self.egg.id},{self.rice.id}", "mode": "strict"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["count"], 1)

    def test_filter_can_filter_by_metadata(self):
        it = Country.objects.create(iso2="IT", name="Italy")
        us = Country.objects.create(iso2="US", name="United States")

        self.r1.origin_country = it
        self.r1.cuisine = "Italian"
        self.r1.difficulty = 2
        self.r1.occasion = "Weeknight dinner"
        self.r1.save(update_fields=["origin_country", "cuisine", "difficulty", "occasion"])

        self.r2.origin_country = us
        self.r2.cuisine = "American"
        self.r2.difficulty = 4
        self.r2.occasion = "Hosting"
        self.r2.save(update_fields=["origin_country", "cuisine", "difficulty", "occasion"])

        url = reverse("ingredient_filter")
        resp = self.client.get(
            url,
            {
                "ingredients": str(self.egg.id),
                "mode": "loose",
                "country": [str(it.id)],
                "cuisine": ["Italian"],
                "difficulty": ["2"],
                "occasion": ["Weeknight dinner"],
            },
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["count"], 1)

    def test_signup_creates_user_and_logs_in(self):
        resp = self.client.post(
            reverse("signup"),
            {
                "email": "new@example.com",
                "username": "newuser",
                "password1": "pass12345z",
                "password2": "pass12345z",
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(get_user_model().objects.filter(username="newuser").exists())
        self.assertTrue(self.client.session.get("_auth_user_id"))

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
        data1 = r1.json()
        self.assertIn("wishlist_count", data1)
        self.assertIn("cooked_count", data1)
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

    def test_profile_page_renders(self):
        resp = self.client.get(reverse("profile", kwargs={"username": "u1"}))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Chef level")
        self.assertTrue(UserProfile.objects.filter(user=self.u1).exists())

    def test_profile_edit_updates_username_and_bio(self):
        self.client.login(username="u1", password="pass12345")
        resp = self.client.post(
            reverse("profile_edit"),
            {
                "display_name": "User One",
                "username": "u1_new",
                "bio": "hello",
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.u1.refresh_from_db()
        self.assertEqual(self.u1.username, "u1_new")
        p = UserProfile.objects.get(user=self.u1)
        self.assertEqual(p.display_name, "User One")
        self.assertEqual(p.bio, "hello")

class AccountsModuleTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username="u1", email="u1@example.com", password="pass12345")

    def test_signup_creates_user_and_logs_in(self):
        url = reverse("signup")
        resp = self.client.post(
            url,
            {"email": "new@example.com", "username": "newuser", "password1": "pass12345x", "password2": "pass12345x"},
        )
        self.assertEqual(resp.status_code, 302)
        User = get_user_model()
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertTrue(self.client.session.get("_auth_user_id"))

    def test_profile_requires_login(self):
        resp = self.client.get(reverse("account_profile"))
        self.assertEqual(resp.status_code, 302)

    def test_profile_renders_activity(self):
        self.client.login(username="u1", password="pass12345")
        r1 = Recipe.objects.create(title="R1", author=self.user, instructions="x", cooking_time_minutes=1)
        RecipeStatus.objects.create(user=self.user, recipe=r1, status=RecipeStatus.STATUS_COOKED)
        resp = self.client.get(reverse("account_profile"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "R1")

    def test_profile_edit_updates_username(self):
        self.client.login(username="u1", password="pass12345")
        resp = self.client.post(
            reverse("account_profile_edit"),
            {"display_name": "Chef", "username": "u1_new", "bio": "Hello"},
        )
        self.assertEqual(resp.status_code, 302)
        User = get_user_model()
        self.assertTrue(User.objects.filter(username="u1_new").exists())