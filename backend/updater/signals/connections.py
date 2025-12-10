from django.dispatch import receiver
from django.db.models.signals import post_save

from updater.models import (
    DevicePackage, DeviceService
)


@receiver(post_save, sender=DevicePackage, dispatch_uid='check_device_package_change')
def check_device_package_change(sender, instance, **kwargs):
    last_record = instance.history.latest()
    prev_record = last_record.prev_record
    if not prev_record:
        return
    if last_record.diff_against(prev_record, include_fields=('parameters',)):
        instance.applied = False
        instance.save(update_fields=('applied',))


@receiver(post_save, sender=DeviceService, dispatch_uid='check_device_service_change')
def check_device_service_change(sender, instance, **kwargs):
    last_record = instance.history.latest()
    prev_record = last_record.prev_record
    if not prev_record:
        return
    if last_record.diff_against(prev_record, include_fields=('enabled',)):
        instance.applied = False
        instance.save(update_fields=('applied',))