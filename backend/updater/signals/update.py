from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.db import transaction

from updater.models import Update, DistUpgrade
from updater.celery import component_update, dist_upgrade


@receiver(post_save, sender=Update, dispatch_uid='schedule_update')
def schedule_update(sender, instance, created, **kwargs):
    if not created:
        return

    def on_commit():
        result = component_update.delay(instance.id)
        instance.task_id = result.id
        instance.save()

    transaction.on_commit(on_commit)

@receiver(post_save, sender=DistUpgrade, dispatch_uid='schedule_dist_upgrade')
def schedule_dist_upgrade(sender, instance, created, **kwargs):
    if not created:
        return

    def on_commit():
        result = dist_upgrade.delay(instance.id)
        instance.task_id = result.id
        instance.save()

    transaction.on_commit(on_commit)


@receiver(pre_save, sender=Update, dispatch_uid='validate_update')
def validate_update(sender, instance, **kwargs):
    assert instance.version.component.devices.filter(id=instance.device_id).exists(), \
        f'Устросйтво {instance.device} не связано с компонентом {instance.version.component}'
