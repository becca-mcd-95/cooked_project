from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from recipes.models import Recipe, Review
from social.models import Country, Follow, Ingredient, RecipeStatus


class Command(BaseCommand):
    help = "Seed demo data for Member2/Member3 modules (users, ingredients, recipes, reviews, follow, wishlist/cooked)."

    def handle(self, *args, **options):
        User = get_user_model()

        demo_password = "demo1234"
        users = {}
        for username, bio in [
            ("alice", "Home cook who loves documenting food."),
            ("bob", "Beginner cook. Big fan of simple recipes."),
            ("chef_lee", "Pro chef sharing practical, restaurant-style recipes."),
            ("admin1", "Test account for features (wishlist, notifications)."),
        ]:
            u, created = User.objects.get_or_create(username=username, defaults={"email": f"{username}@demo.local"})
            if created or not u.has_usable_password():
                u.set_password(demo_password)
                u.save(update_fields=["password"])
            users[username] = u

        for name, category in [
            ("Egg", "Dairy"),
            ("Rice", "Staple"),
            ("Salt", "Seasoning"),
            ("Black pepper", "Seasoning"),
            ("Olive oil", "Seasoning"),
            ("Tomato", "Vegetable"),
            ("Onion", "Vegetable"),
            ("Garlic", "Vegetable"),
            ("Pasta", "Staple"),
            ("Beef", "Meat"),
            ("Chicken thigh", "Meat"),
            ("Soy sauce", "Seasoning"),
            ("Honey", "Seasoning"),
            ("Lemon", "Fruit"),
        ]:
            Ingredient.objects.get_or_create(name=name, defaults={"category": category})

        countries = {}
        for iso2, name in [
            ("IT", "Italy"),
            ("US", "United States"),
            ("CN", "China"),
            ("JP", "Japan"),
            ("FR", "France"),
            ("GB", "United Kingdom"),
        ]:
            c, _ = Country.objects.get_or_create(iso2=iso2, defaults={"name": name})
            countries[iso2] = c

        def ing(*names: str):
            return list(Ingredient.objects.filter(name__in=names))

        r1, created1 = Recipe.objects.get_or_create(
            title="Tomato braised beef pasta",
            author=users["chef_lee"],
            defaults={
                "cooking_time_minutes": 60,
                "instructions": "1) Brown beef; saute onion/garlic.\n2) Add tomato and simmer.\n3) Cook pasta and mix with sauce.",
            },
        )
        if created1:
            r1.ingredients.set(ing("Beef", "Tomato", "Onion", "Garlic", "Pasta", "Salt", "Black pepper", "Olive oil"))
        if created1 or not r1.origin_country_id:
            r1.origin_country = countries["IT"]
            r1.save(update_fields=["origin_country"])

        r2, created2 = Recipe.objects.get_or_create(
            title="Honey lemon roasted chicken thighs",
            author=users["alice"],
            defaults={
                "cooking_time_minutes": 45,
                "instructions": "1) Marinate chicken with honey/lemon/soy sauce.\n2) Roast at 200C for 25-30 min.\n3) Rest and serve.",
            },
        )
        if created2:
            r2.ingredients.set(ing("Chicken thigh", "Honey", "Lemon", "Soy sauce", "Salt", "Black pepper", "Olive oil"))
        if created2 or not r2.origin_country_id:
            r2.origin_country = countries["US"]
            r2.save(update_fields=["origin_country"])

        r3, created3 = Recipe.objects.get_or_create(
            title="Simple egg fried rice",
            author=users["bob"],
            defaults={
                "cooking_time_minutes": 15,
                "instructions": "1) Scramble eggs.\n2) Fry rice until loose.\n3) Add eggs + seasoning and serve.",
            },
        )
        if created3:
            r3.ingredients.set(ing("Egg", "Rice", "Salt", "Black pepper", "Olive oil"))
        if created3 or not r3.origin_country_id:
            r3.origin_country = countries["CN"]
            r3.save(update_fields=["origin_country"])

        r4, created4 = Recipe.objects.get_or_create(
            title="Boiled egg (minimal)",
            author=users["admin1"],
            defaults={
                "cooking_time_minutes": 12,
                "instructions": "1) Boil water.\n2) Simmer egg 8-10 minutes.\n3) Chill, peel, enjoy.",
            },
        )
        if created4:
            r4.ingredients.set(ing("Egg"))
        if created4 or not r4.origin_country_id:
            r4.origin_country = countries["GB"]
            r4.save(update_fields=["origin_country"])

        def upsert_review(user, recipe, rating, comment):
            rv, _ = Review.objects.update_or_create(
                user=user,
                recipe=recipe,
                defaults={"rating": rating, "comment": comment},
            )
            return rv

        upsert_review(users["alice"], r1, 5, "Rich sauce and tender beef. Great with pasta.")
        upsert_review(users["bob"], r1, 4, "Tasty. I used beef slices and it still worked.")
        upsert_review(users["chef_lee"], r2, 5, "Nice balance of sweet and bright acidity.")
        upsert_review(users["alice"], r4, 5, "Simple but very useful. Timing is key.")

        Follow.objects.get_or_create(follower=users["alice"], following=users["chef_lee"])

        for user, recipe, status in [
            (users["alice"], r1, RecipeStatus.STATUS_COOKED),
            (users["alice"], r3, RecipeStatus.STATUS_WISHLIST),
            (users["bob"], r3, RecipeStatus.STATUS_COOKED),
            (users["bob"], r2, RecipeStatus.STATUS_WISHLIST),
            (users["admin1"], r1, RecipeStatus.STATUS_WISHLIST),
            (users["admin1"], r2, RecipeStatus.STATUS_WISHLIST),
            (users["admin1"], r4, RecipeStatus.STATUS_COOKED),
        ]:
            RecipeStatus.objects.get_or_create(user=user, recipe=recipe, status=status)

        self.stdout.write(self.style.SUCCESS("Demo data seeded. Users: alice/bob/chef_lee/admin1 (password: demo1234)."))
