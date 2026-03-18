from django.apps import AppConfig

class CookedConfig(AppConfig):
    name = 'cooked'

    def ready(self):
        import cooked.models
