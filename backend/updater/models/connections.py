from django.db import models
from django.core.exceptions import ValidationError
from simple_history.models import HistoricalRecords

from .device import Device
from .components import Package, Service


class DevicePackage(models.Model):
    class Meta:
        verbose_name = 'Связь устройства с пакетом'
        verbose_name_plural = 'Связи устройств с пакетами'
        db_table = 'device_package'
        constraints = [
            models.UniqueConstraint(fields=('device_id', 'package_id',), name='unique_device_package')
        ]

    device = models.ForeignKey('updater.Device', on_delete=models.CASCADE, related_name='device_packages', verbose_name='Устройство')
    package = models.ForeignKey('updater.Package', on_delete=models.CASCADE, related_name='device_packages', verbose_name='Пакет')
    version = models.ForeignKey('updater.Version', on_delete=models.CASCADE, null=True, blank=True, default=None, related_name='device_packages', verbose_name='Версия')
    applied = models.BooleanField(default=False, verbose_name='Применено ли')
    parameters = models.JSONField(default=dict, blank=True, verbose_name='Параметры', help_text='Подставляются в шаблон (имеют приоритет над параметрами в шаблоне)')
    history = HistoricalRecords(
        verbose_name='История изменений связей устройства с пакетом',
        verbose_name_plural='Истории изменений связей устройств с пакетами'
    )

    def __str__(self):
        return f'{self.device}:{self.package.name}-{self.version.number}'

    def clean(self):
        if self.package_id and self.version_id:
            if self.version.package_id != self.package_id:
                raise ValidationError({
                    'version': f"Выбранная версия '{self.version.number}' не относится к пакету '{self.package.name}'"
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class DeviceService(models.Model):
    class Meta:
        verbose_name = 'Связь устройства с сервисом'
        verbose_name_plural = 'Связи устройств с сервисами'
        db_table = 'device_service'
        constraints = [
            models.UniqueConstraint(fields=('device_id', 'service_id',), name='unique_device_service')
        ]

    device = models.ForeignKey('updater.Device', on_delete=models.CASCADE, related_name='device_services',
                               verbose_name='Устройство')
    service = models.ForeignKey('updater.Service', on_delete=models.CASCADE, related_name='device_services',
                                verbose_name='Сервис')
    applied = models.BooleanField(default=False, verbose_name='Применено ли')
    enabled = models.BooleanField(default=True, verbose_name='Включен ли')
    history = HistoricalRecords(
        verbose_name='История изменений связей устройства с сервисом',
        verbose_name_plural='Истории изменений связей устройств с сервисами'
    )

    def __str__(self):
        return f'{self.device}:{self.service}'
