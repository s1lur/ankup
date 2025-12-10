from django.db.models.signals import post_save
from django.core.exceptions import ValidationError

from updater.models import (
    PackagePackageDependency, ServiceServiceDependency
)


def check_cycle(model, current_id, target_id, visited=None):
    if visited is None: visited = set()

    if current_id == target_id:
        return True

    if current_id in visited:
        return False

    visited.add(current_id)

    next_ids = model.objects.filter(
        dependant_id=current_id
    ).values_list('dependency_id', flat=True)

    for nid in next_ids:
        if check_cycle(nid, target_id, visited):
            return True

    return False


def prevent_cycles(sender, instance, created, **kwargs):
    if instance.dependant_id == instance.dependency_id:
        raise ValidationError("Объект не может зависеть сам от себя.")

    if check_cycle(sender, instance.dependency_id, target_id=instance.dependant_id):
        raise ValidationError(
            f"Обнаружена циклическая зависимость! "
            f"Добавление связи '{instance.dependant.name} -> {instance.dependency.name}' замыкает круг."
        )

    
post_save.connect(prevent_cycles, sender=PackagePackageDependency, dispatch_uid='prevent_package_package_cycles')
post_save.connect(prevent_cycles, sender=ServiceServiceDependency, dispatch_uid='prevent_service_service_cycles')
