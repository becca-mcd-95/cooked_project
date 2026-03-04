from django.apps import AppConfig
from models import create_user_profile

class CookedConfig(AppConfig):
    name = 'cooked'

def ready(self):
    import cooked.models