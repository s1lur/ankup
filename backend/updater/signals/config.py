from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from hashlib import sha256

from updater.models import DevicePackage, ConfigTemplate

@receiver(post_save, sender=ConfigTemplate, dispatch_uid='check_config_template_change')
def check_config_template_change(sender, instance, **kwargs):
    if not hasattr(instance, '_old_file_hash') and not hasattr(instance, '_old_params'):
        return
    objs = DevicePackage.objects.filter(package__configs__id=instance.pk).select_for_update()

    if instance._old_params != instance.parameters:
        for obj in objs:
            obj.applied = False
            obj.save(update_fields=('applied',))
        return

    hash = sha256()
    with open(instance.file.path, 'rb') as f:
        hash.update(f.read())
    if hash.hexdigest() != instance._old_file_hash:
        for obj in objs:
            obj.applied = False
            obj.save(update_fields=('applied',))


@receiver(pre_save, sender=ConfigTemplate, dispatch_uid='save_config_template_old_fields')
def save_config_template_old_fields(sender, instance, **kwargs):
    if not instance.pk:
        return
    old_instance = sender.objects.get(pk=instance.pk)
    instance._old_params = old_instance.parameters
    hash = sha256()
    try:
        hash.update(old_instance.file.open().read())
        instance._old_file_hash = hash.hexdigest()
    finally:
        instance.file.close()

@receiver(pre_save, sender=DevicePackage, dispatch_uid='save_device_package_old_fields')
def save_device_package_old_fields(sender, instance, **kwargs):
    if not instance.pk:
        return

    old_instance = sender.objects.get(pk=instance.pk)
    instance._old_params = old_instance.parameters


@receiver(pre_save, sender=DevicePackage, dispatch_uid='check_device_package_change')
def check_device_package_change(sender, instance, **kwargs):
    if not hasattr(instance, '_old_params'):
        return
    if instance._old_params != instance.parameters:
        instance.applied = False
        instance.save(update_fields=('applied',))
