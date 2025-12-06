from django.db import models
from simple_history.models import HistoricalRecords


class Package(models.Model):
    class Meta:
        verbose_name = 'Пакет'
        verbose_name_plural = 'Пакеты'
        db_table = 'package'

    name = models.CharField(max_length=250, verbose_name='Название пакета')
    dependencies = models.ManyToManyField('updater.Package', db_table='package_package_deps', related_name='dependant_packages', blank=True, verbose_name='Зависимости')

    def __str__(self):
        return f'{self.name}'


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


class Service(models.Model):
    class Meta:
        verbose_name = 'Сервис'
        verbose_name_plural = 'Сервисы'
        db_table = 'service'

    name = models.CharField(max_length=250, unique=True, help_text='Название сервиса в systemd (без .service)', verbose_name='Название')
    service_deps = models.ManyToManyField('updater.Service', db_table='service_service_deps', related_name='dependant_services', blank=True, verbose_name='Сервисы-зависимости')
    package_deps = models.ManyToManyField('updater.Package', db_table='service_package_deps', related_name='services', blank=True, verbose_name='Пакеты-зависимости')

    def __str__(self):
        return f"{self.name}.service"
