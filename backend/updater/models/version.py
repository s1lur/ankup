from django.db import models
from simple_history.models import HistoricalRecords


class Version(models.Model):
    class Meta:
        verbose_name = 'Версия'
        verbose_name_plural = 'Версии'
        db_table = 'version'

    package = models.ForeignKey('updater.Package', related_name='versions', on_delete=models.CASCADE, verbose_name='Пакет')
    number = models.CharField(max_length=250, verbose_name='Номер версии')
    history = HistoricalRecords(
        verbose_name='История изменений версии',
        verbose_name_plural='Истории изменений версий'
    )

    def __str__(self):
        return f'{self.package}-{self.number}'
