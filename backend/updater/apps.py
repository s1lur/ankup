from django.apps import AppConfig


class UpdaterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'updater'

    def ready(self):
        from .signals import (
            schedule_update, device_post_save, update_device_antivirus_schedule,
            prevent_cycles,
            check_device_package_change, check_device_service_change,
            check_config_template_change, save_config_template_old_fields,
        )

