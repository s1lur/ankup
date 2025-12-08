from django.dispatch import receiver
from django.db.models.signals import post_save

from updater.models import Device
from updater.celery import update_devices_availability


@receiver(post_save, sender=Device, dispatch_uid="device_post_save")
def device_post_save(sender, instance, created, **kwargs):
    update_devices_availability.delay()



