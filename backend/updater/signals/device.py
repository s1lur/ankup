from croniter import croniter

from django.dispatch import receiver
from django.db.models.signals import post_save,pre_save
from django.utils import timezone

from updater.models import Device
from updater.celery import update_devices_availability


@receiver(post_save, sender=Device, dispatch_uid="device_post_save")
def device_post_save(sender, instance, created, **kwargs):
    update_devices_availability.delay()


@receiver(pre_save, sender=Device)
def update_device_antivirus_schedule(sender, instance, **kwargs):
    if not instance.antivirus_schedule :
        instance.next_run_at = None
        return

    try:
        old_instance = Device.objects.get(pk=instance.pk)
        old_schedule = old_instance.antivirus_schedule
    except Device.DoesNotExist:
        old_schedule = None

    if instance.antivirus_schedule != old_schedule or not instance.next_run_at:
        try:
            iter = croniter(instance.antivirus_schedule, timezone.now())
            instance.next_run_at = iter.get_next(timezone.datetime)
        except Exception:
            instance.next_run_at = None

