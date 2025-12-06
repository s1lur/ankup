from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from updater.models import Package, Service


def check_circular_dependency(model_class, pk_set, instance_pk, relation_field):
    if instance_pk in pk_set:
        return True

    for target_id in pk_set:
        obj = model_class.objects.get(pk=target_id)
        next_level_ids = set(getattr(obj, relation_field).values_list('id', flat=True))

        if next_level_ids:
            if check_circular_dependency(model_class, next_level_ids, instance_pk, relation_field):
                return True
    return False


@receiver(m2m_changed, sender=Package.dependencies.through, dispatch_uid='validate_package_cycles')
def validate_package_cycles(sender, instance, action, pk_set, **kwargs):
    if action == "pre_add":
        if check_circular_dependency(Package, pk_set, instance.pk, 'dependencies'):
            raise ValidationError("Обнаружена циклическая зависимость пакетов!")


@receiver(m2m_changed, sender=Service.service_deps.through, dispatch_uid='validate_service_cycles')
def validate_service_cycles(sender, instance, action, pk_set, **kwargs):
    if action == "pre_add":
        if check_circular_dependency(Service, pk_set, instance.pk, 'service_deps'):
            raise ValidationError("Обнаружена циклическая зависимость сервисов!")
