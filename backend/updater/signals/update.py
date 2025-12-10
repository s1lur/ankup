from functools import partial

from django.db import transaction
from django.db.models.signals import post_save

from updater.models import PackageUpdate, DistUpgrade, ServiceUpdate, AntivirusUpdate
from updater.celery import execute_update


def schedule_update(sender, instance, created, **kwargs):
    if not created:
        return

    def on_commit():
        result = execute_update.delay(sender.__name__, instance.id, kwargs.get('timeout', 600))
        instance.task_id = result.id
        instance.save(update_fields=('task_id',))

    transaction.on_commit(on_commit)

post_save.connect(partial(schedule_update, timeout=1800), sender=PackageUpdate, dispatch_uid='schedule_package_update')
post_save.connect(schedule_update, sender=DistUpgrade, dispatch_uid='schedule_dist_upgrade')
post_save.connect(schedule_update, sender=ServiceUpdate, dispatch_uid='schedule_service_update')
post_save.connect(schedule_update, sender=AntivirusUpdate, dispatch_uid='schedule_antivirus_update')
