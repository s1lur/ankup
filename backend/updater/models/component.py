from django.db import models

from .states import CurrentState, TargetState


class Component(models.Model):
    class Meta:
        verbose_name = 'Компонент'
        verbose_name_plural = 'Компоненты'
        db_table = 'component'

    human_name = models.CharField(max_length=250, verbose_name='Название')
    package_name = models.CharField(max_length=250, unique=True, verbose_name='Название пакета')

    def __str__(self):
        return f'{self.package_name}'
