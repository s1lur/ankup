from django.db import models


class Device(models.Model):
    class Meta:
        verbose_name = 'Устройство'
        verbose_name_plural = 'Устройства'
        db_table = 'device'

    name = models.CharField(max_length=250, unique=True, verbose_name='Название')
    packages = models.ManyToManyField('updater.Package', related_name='devices', through='updater.DevicePackage', blank=True, verbose_name='Пакеты')
    services = models.ManyToManyField('updater.Service', related_name='devices', through='updater.DeviceService', blank=True, verbose_name='Сервисы')
    is_available = models.BooleanField(default=False, blank=True, verbose_name='Доступность')
    last_seen = models.DateTimeField(null=True, blank=True, verbose_name='Время последнего успешного пинга')

    def __str__(self):
        return f'{self.name}'
