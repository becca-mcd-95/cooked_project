# to populate website for video
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from cooked.models import Recipe, Review, Ingredient, Country, RecipeStatus, UserProfile
 
class Command(BaseCommand):
    help = 'Seed the database with demo data'
 
    def handle(self, *args, **kwargs):
 
        # ── Countries ──
        countries_data = [
            ('IT', 'Italy'), ('JP', 'Japan'), ('MX', 'Mexico'),
            ('IN', 'India'), ('FR', 'France'), ('TH', 'Thailand'),
            ('GB', 'United Kingdom'), ('GR', 'Greece'),
        ]
        countries = {}
        for iso, name in countries_data:
            c, _ = Country.objects.get_or_create(iso2=iso, defaults={'name': name})
            countries[iso] = c
        self.stdout.write('✓ Countries created')
 
        # ── Ingredients ──
        ingredients_data = [
            ('Chicken', 'Meat'), ('Pasta', 'Carbs'), ('Tomato', 'Vegetable'),
            ('Garlic', 'Vegetable'), ('Onion', 'Vegetable'), ('Egg', 'Dairy'),
            ('Cheese', 'Dairy'), ('Rice', 'Carbs'), ('Beef', 'Meat'),
            ('Salmon', 'Fish'), ('Lemon', 'Fruit'), ('Olive Oil', 'Oil'),
            ('Basil', 'Herb'), ('Chilli', 'Spice'), ('Coconut Milk', 'Dairy'),
            ('Noodles', 'Carbs'), ('Tofu', 'Protein'), ('Ginger', 'Spice'),
        ]
        ingredients = {}
        for name, category in ingredients_data:
            ing, _ = Ingredient.objects.get_or_create(name=name, defaults={'category': category})
            ingredients[name] = ing
        self.stdout.write('✓ Ingredients created')
 
        # ── Users ──
        users_data = [
            ('pasta_queen', 'pasta@example.com', 'From Glasgow, love cooking Italian food 🍝', 'Glasgow'),
            ('spice_master', 'spice@example.com', 'Obsessed with Asian cuisine and bold flavours 🌶️', 'Edinburgh'),
            ('home_chef', 'home@example.com', 'Just a home cook trying new recipes every week!', 'London'),
            ('foodie_becca', 'becca@example.com', 'Food blogger and recipe enthusiast 📸', 'Manchester'),
        ]
        users = {}
        for username, email, bio, city in users_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email}
            )
            if created:
                user.set_password('password123')
                user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.bio = bio
            profile.city = city
            profile.save()
            users[username] = user
        self.stdout.write('✓ Users created')
 
        # ── Recipes ──
        recipes_data = [
            {
                'title': 'Spaghetti Carbonara',
                'instructions': 'Cook pasta. Fry pancetta. Mix eggs and cheese. Combine off heat. Season well.',
                'cooking_time_minutes': 25,
                'country': 'IT',
                'author': 'pasta_queen',
                'ingredients': ['Pasta', 'Egg', 'Cheese', 'Garlic'],
            },
            {
                'title': 'Chicken Tikka Masala',
                'instructions': 'Marinate chicken in yoghurt and spices. Grill then simmer in tomato sauce.',
                'cooking_time_minutes': 45,
                'country': 'IN',
                'author': 'spice_master',
                'ingredients': ['Chicken', 'Tomato', 'Onion', 'Garlic', 'Ginger', 'Chilli'],
            },
            {
                'title': 'Beef Bourguignon',
                'instructions': 'Brown beef. Cook with red wine, carrots, and herbs for 2 hours.',
                'cooking_time_minutes': 140,
                'country': 'FR',
                'author': 'home_chef',
                'ingredients': ['Beef', 'Onion', 'Garlic', 'Olive Oil'],
            },
            {
                'title': 'Pad Thai',
                'instructions': 'Stir fry noodles with egg, tofu, bean sprouts and tamarind sauce.',
                'cooking_time_minutes': 20,
                'country': 'TH',
                'author': 'spice_master',
                'ingredients': ['Noodles', 'Egg', 'Tofu', 'Chilli', 'Garlic'],
            },
            {
                'title': 'Shakshuka',
                'instructions': 'Simmer tomatoes and peppers with spices. Poach eggs directly in the sauce.',
                'cooking_time_minutes': 30,
                'country': 'GB',
                'author': 'foodie_becca',
                'ingredients': ['Egg', 'Tomato', 'Onion', 'Garlic', 'Chilli'],
            },
            {
                'title': 'Salmon Teriyaki',
                'instructions': 'Marinate salmon in soy, mirin and sake. Grill and glaze with sauce.',
                'cooking_time_minutes': 20,
                'country': 'JP',
                'author': 'home_chef',
                'ingredients': ['Salmon', 'Ginger', 'Garlic', 'Lemon'],
            },
            {
                'title': 'Margherita Pizza',
                'instructions': 'Make dough, top with tomato sauce, mozzarella and basil. Bake at 250°C.',
                'cooking_time_minutes': 40,
                'country': 'IT',
                'author': 'pasta_queen',
                'ingredients': ['Tomato', 'Cheese', 'Basil', 'Olive Oil'],
            },
            {
                'title': 'Greek Salad',
                'instructions': 'Chop tomatoes, cucumber, olives and feta. Dress with olive oil and oregano.',
                'cooking_time_minutes': 10,
                'country': 'GR',
                'author': 'foodie_becca',
                'ingredients': ['Tomato', 'Cheese', 'Lemon', 'Olive Oil'],
            },
            {
                'title': 'Chicken Fried Rice',
                'instructions': 'Fry day-old rice with chicken, egg, soy sauce and spring onions.',
                'cooking_time_minutes': 15,
                'country': 'TH',
                'author': 'spice_master',
                'ingredients': ['Chicken', 'Rice', 'Egg', 'Garlic', 'Ginger'],
            },
            {
                'title': 'Tacos al Pastor',
                'instructions': 'Marinate pork in chilli and pineapple. Cook on high heat and serve in tortillas.',
                'cooking_time_minutes': 35,
                'country': 'MX',
                'author': 'home_chef',
                'ingredients': ['Onion', 'Chilli', 'Garlic', 'Lemon'],
            },
            {
                'title': 'Thai Green Curry',
                'instructions': 'Fry curry paste. Add coconut milk, vegetables and protein. Simmer 20 mins.',
                'cooking_time_minutes': 30,
                'country': 'TH',
                'author': 'spice_master',
                'ingredients': ['Coconut Milk', 'Chicken', 'Chilli', 'Ginger', 'Garlic'],
            },
            {
                'title': 'Ramen',
                'instructions': 'Make broth from bones. Cook noodles separately. Top with egg, nori and pork.',
                'cooking_time_minutes': 180,
                'country': 'JP',
                'author': 'pasta_queen',
                'ingredients': ['Noodles', 'Egg', 'Ginger', 'Garlic'],
            },
        ]
 
        recipes = {}
        for data in recipes_data:
            recipe, created = Recipe.objects.get_or_create(
                title=data['title'],
                defaults={
                    'instructions': data['instructions'],
                    'cooking_time_minutes': data['cooking_time_minutes'],
                    'origin_country': countries[data['country']],
                    'author': users[data['author']],
                }
            )
            if created:
                for ing_name in data['ingredients']:
                    if ing_name in ingredients:
                        recipe.ingredients.add(ingredients[ing_name])
            recipes[data['title']] = recipe
        self.stdout.write('✓ Recipes created')
 
        # ── Reviews ──
        reviews_data = [
            ('spice_master', 'Spaghetti Carbonara', 5, 'Absolutely incredible — the creamiest carbonara I have ever made. Will be making this every week!'),
            ('home_chef', 'Spaghetti Carbonara', 4, 'Really good recipe, just make sure you take it off the heat before adding the eggs or you will get scrambled eggs!'),
            ('foodie_becca', 'Chicken Tikka Masala', 5, 'This is the best tikka masala recipe I have tried at home. Rich, fragrant and delicious.'),
            ('pasta_queen', 'Pad Thai', 4, 'Loved this! Used extra chilli and it was perfect. Quick weeknight dinner.'),
            ('home_chef', 'Shakshuka', 5, 'Made this for brunch and everyone was impressed. So easy and so good.'),
            ('spice_master', 'Salmon Teriyaki', 5, 'The glaze is just perfect. Served with steamed rice and it was restaurant quality.'),
            ('foodie_becca', 'Margherita Pizza', 4, 'Simple but perfect. Used a pizza stone and it made a huge difference.'),
            ('pasta_queen', 'Thai Green Curry', 5, 'This is my new go-to curry recipe. The coconut milk makes it so creamy.'),
        ]
 
        for username, recipe_title, rating, comment in reviews_data:
            if username in users and recipe_title in recipes:
                Review.objects.get_or_create(
                    user=users[username],
                    recipe=recipes[recipe_title],
                    defaults={'rating': rating, 'comment': comment}
                )
        self.stdout.write('✓ Reviews created')
 
        # ── Recipe Statuses (cooked + wishlist) ──
        cooked_data = [
            ('pasta_queen', 'Chicken Tikka Masala'),
            ('pasta_queen', 'Pad Thai'),
            ('pasta_queen', 'Shakshuka'),
            ('spice_master', 'Spaghetti Carbonara'),
            ('spice_master', 'Margherita Pizza'),
            ('home_chef', 'Chicken Tikka Masala'),
            ('home_chef', 'Salmon Teriyaki'),
            ('foodie_becca', 'Ramen'),
            ('foodie_becca', 'Tacos al Pastor'),
        ]
        for username, recipe_title in cooked_data:
            if username in users and recipe_title in recipes:
                RecipeStatus.objects.get_or_create(
                    user=users[username],
                    recipe=recipes[recipe_title],
                    status=RecipeStatus.STATUS_COOKED
                )
 
        wishlist_data = [
            ('pasta_queen', 'Beef Bourguignon'),
            ('pasta_queen', 'Ramen'),
            ('spice_master', 'Beef Bourguignon'),
            ('home_chef', 'Tacos al Pastor'),
            ('foodie_becca', 'Thai Green Curry'),
        ]
        for username, recipe_title in wishlist_data:
            if username in users and recipe_title in recipes:
                RecipeStatus.objects.get_or_create(
                    user=users[username],
                    recipe=recipes[recipe_title],
                    status=RecipeStatus.STATUS_WISHLIST
                )
        self.stdout.write('✓ Recipe statuses created')
 
        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully!'))
        self.stdout.write('Users created (all with password: password123):')
        for username in users:
            self.stdout.write(f'  - {username}')