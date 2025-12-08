from django.apps import AppConfig


class UpdaterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'updater'

    def ready(self):
        from .signals import (
            schedule_update, device_post_save,
            validate_service_cycles, validate_package_cycles,
            check_config_template_file_change, save_config_template_old_file_hash
        )

