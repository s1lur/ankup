from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from hashlib import sha256

from updater.models import DevicePackage, ConfigTemplate

@receiver(post_save, sender=ConfigTemplate, dispatch_uid='check_config_template_file_change')
def check_config_template_file_change(sender, instance, **kwargs):
    if not hasattr(instance, '_old_file_hash'):
        return
    objs = DevicePackage.objects.filter(package__configs__id=instance.pk).select_for_update()
    hash = sha256()
    with open(instance.file.path, 'rb') as f:
        hash.update(f.read())
    if hash.hexdigest() != instance._old_file_hash:
        for obj in objs:
            obj.applied = False
            obj.save(update_fields=('applied',))


@receiver(pre_save, sender=ConfigTemplate, dispatch_uid='save_config_template_old_file_hash')
def save_config_template_old_file_hash(sender, instance, **kwargs):
    hash = sha256()
    try:
        hash.update(instance.file.open().read())
        instance._old_file_hash = hash.hexdigest()
    except Exception:
        instance.file.close()
