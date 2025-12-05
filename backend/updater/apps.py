from django.apps import AppConfig


class UpdaterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'updater'

    def ready(self):
        from .signals import schedule_update, schedule_dist_upgrade, validate_update
