from django.db import models
from django.db.models import constraints
from simple_history.models import HistoricalRecords


class Service(models.Model):
    class Meta:
        verbose_name = 'Сервис'
        verbose_name_plural = 'Сервисы'
        db_table = 'service'

    name = models.CharField(max_length=250, unique=True, help_text='Название сервиса в systemd (без .service)', verbose_name='Название')
    service_deps = models.ManyToManyField('updater.Service', through='updater.ServiceServiceDependency', through_fields=('dependant', 'dependency'), related_name='dependant_services', blank=True, verbose_name='Сервисы-зависимости')
    package_deps = models.ManyToManyField('updater.Package', through='updater.ServicePackageDependency', through_fields=('dependant', 'dependency'), related_name='dependant_services', blank=True, verbose_name='Пакеты-зависимости')
    history = HistoricalRecords(
        verbose_name='История изменений сервиса',
        verbose_name_plural='Истории изменений сервисов'
    )

    def __str__(self):
        return f"{self.name}.service"


class ServicePackageDependency(models.Model):
    class Meta:
        verbose_name = 'Зависимость сервиса от пакета'
        verbose_name_plural = 'Зависимости сервисов от пакетов'
        db_table = 'service_package_deps'
        constraints = [
            constraints.UniqueConstraint(fields=['dependant', 'dependency'], name='unique_service_package_pair')
        ]

    dependant = models.ForeignKey('updater.Service', on_delete=models.CASCADE, related_name='package_deps_through', verbose_name='Зависимый сервис')
    dependency = models.ForeignKey('updater.Package', on_delete=models.CASCADE, related_name='dependant_services_through', verbose_name='Пакет-зависимость')
    versions = models.ManyToManyField('updater.Version', related_name='services_package_deps', db_table='version_service_package_deps', blank=True, verbose_name='Версии')


class ServiceServiceDependency(models.Model):
    class Meta:
        verbose_name = 'Зависимость сервиса от сервиса'
        verbose_name_plural = 'Зависимости сервисов от сервисов'
        db_table = 'service_service_deps'
        constraints = [
            constraints.UniqueConstraint(fields=['dependant', 'dependency'], name='unique_service_service_pair')
        ]

    dependant = models.ForeignKey('updater.Service', on_delete=models.CASCADE, related_name='service_deps_through', verbose_name='Зависимый сервис')
    dependency = models.ForeignKey('updater.Service', on_delete=models.CASCADE, related_name='dependant_services_through', verbose_name='Сервис-зависимость')
