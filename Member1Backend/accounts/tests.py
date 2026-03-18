from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from recipes.models import Recipe
from social.models import RecipeStatus


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

