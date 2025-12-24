from django.dispatch import receiver
from simple_history.signals import post_create_historical_record

from updater.models import (
    HistoricalDevicePackage, HistoricalDeviceService
)


@receiver(post_create_historical_record, sender=HistoricalDevicePackage, dispatch_uid='check_device_package_change')
def check_device_package_change(sender, instance, history_instance, **kwargs):
    prev_record = history_instance.prev_record
    if not prev_record:
        return
    if history_instance.diff_against(prev_record, included_fields=('parameters', 'version')).changes:
        instance.skip_history_when_saving = True
        instance.applied = False
        instance.save(update_fields=('applied',))
        del instance.skip_history_when_saving


@receiver(post_create_historical_record, sender=HistoricalDeviceService, dispatch_uid='check_device_service_change')
def check_device_service_change(sender, instance, history_instance, **kwargs):
    prev_record = history_instance.prev_record
    if not prev_record:
        return
    if history_instance.diff_against(prev_record, included_fields=('enabled',)).changes:
        instance.skip_history_when_saving = True
        instance.applied = False
        instance.save(update_fields=('applied',))
        del instance.skip_history_when_saving