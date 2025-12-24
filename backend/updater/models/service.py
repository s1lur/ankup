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
    package = models.ForeignKey('updater.Package', on_delete=models.CASCADE, related_name='services', verbose_name='Пакет')
    history = HistoricalRecords(
        verbose_name='История изменений сервиса',
        verbose_name_plural='Истории изменений сервисов'
    )

    def __str__(self):
        return f"{self.name}.service"


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
