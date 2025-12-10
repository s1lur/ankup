from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from hashlib import sha256

from updater.models import DevicePackage, ConfigTemplate

@receiver(post_save, sender=ConfigTemplate, dispatch_uid='check_config_template_change')
def check_config_template_change(sender, instance, created, **kwargs):
    objs = DevicePackage.objects.filter(package__configs__id=instance.pk).select_for_update()

    def unapply(objs):
        for obj in objs:
            obj.applied = False
            obj.save(update_fields=('applied',))

    if created:
        unapply(objs)
        return

    if not hasattr(instance, '_old_file_hash') and not hasattr(instance, '_old_params'):
        return

    if instance._old_params != instance.parameters:
        unapply(objs)
        return

    hash = sha256()
    with open(instance.file.path, 'rb') as f:
        hash.update(f.read())
    if hash.hexdigest() != instance._old_file_hash:
        unapply(objs)


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


