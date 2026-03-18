from django.apps import AppConfig
from cooked.models import create_user_profile

class CookedConfig(AppConfig):
    name = 'cooked'

    def ready(self):
        create_user_profile()


"""
Commenting out the below because I'm not sure what it influences 

"""

# # Yanyan

# class RecipesConfig(AppConfig):
#     default_auto_field = "django.db.models.BigAutoField"
#     name = "recipes"

# # Tuoyu

# class SocialConfig(AppConfig):
#     default_auto_field = "django.db.models.BigAutoField"
#     name = "social"

