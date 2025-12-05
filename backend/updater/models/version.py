from django.db import models


class Version(models.Model):
    class Meta:
        verbose_name = 'Версия'
        verbose_name_plural = 'Версии'
        db_table = 'version'

    component = models.ForeignKey('updater.Component', related_name='versions', on_delete=models.CASCADE, verbose_name='Компонент')
    number = models.CharField(max_length=250, verbose_name='Номер версии')

    def __str__(self):
        return f'{self.component}-{self.number}'
