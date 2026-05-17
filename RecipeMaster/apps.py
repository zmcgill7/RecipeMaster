from django.apps import AppConfig


class RecipemasterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'RecipeMaster'

    def ready(self):
        from django.conf import settings

        if not settings.BACKGROUND_RECIPE_DATA_DOWNLOAD:
            return

        from .recipe_data import start_recipe_data_download

        start_recipe_data_download()
