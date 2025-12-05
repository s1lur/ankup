from django.db import models


class Device(models.Model):
    class Meta:
        verbose_name = 'Устройство'
        verbose_name_plural = 'Устройства'
        db_table = 'device'

    name = models.CharField(max_length=250, unique=True, verbose_name='Название')
    components = models.ManyToManyField('updater.Component', related_name='devices', db_table='device_components', verbose_name='Компоненты')

    def __str__(self):
        return f'{self.name}'
