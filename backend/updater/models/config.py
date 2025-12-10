from django.db import models
from simple_history.models import HistoricalRecords


class ConfigTemplate(models.Model):
    class Meta:
        verbose_name = 'Шаблон конфига'
        verbose_name_plural = 'Шаблоны конфигов'
        db_table = 'config_template'

    name = models.CharField(max_length=250, verbose_name='Название')
    file = models.FileField(upload_to='config_templates', verbose_name='Файл')
    package = models.ForeignKey('updater.Package', on_delete=models.CASCADE, related_name='configs', verbose_name='Пакет')
    dest_path = models.CharField(max_length=255, verbose_name='Путь на устройстве', help_text="Пример: /etc/nginx.conf)")
    file_mode = models.CharField(max_length=4, default='0644', verbose_name='Режим доступа к файлу')
    parameters = models.JSONField(default=dict, blank=True, verbose_name='Параметры', help_text='Подставляются в шаблон')
    history = HistoricalRecords(
        verbose_name='История изменений шаблона конфига',
        verbose_name_plural='Истории изменений шаблонов конфигов'
    )

    def __str__(self):
        return self.name
