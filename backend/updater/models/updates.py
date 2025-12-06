from django.db import models
from updater.choices import TaskStatus
from updater.models import DevicePackage, DeviceService


class Task(models.Model):
    class Meta:
        abstract = True

    device = models.ForeignKey('updater.Device', related_name='%(class)ss', on_delete=models.CASCADE,
                               verbose_name='Устройство')
    status = models.CharField(max_length=50, choices=TaskStatus.choices, default=TaskStatus.REQUESTED, verbose_name='Состояние')
    task_id = models.UUIDField(null=True, verbose_name='ID задачи')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    author = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, verbose_name='Автор')


class PackageUpdate(Task):
    _salt_task_name = 'package_update'
    _connection_model = DevicePackage

    class Meta:
        verbose_name = 'Обновление пакетов'
        verbose_name_plural = 'Обновления пакетов'
        db_table = 'component_update'

    def __str__(self):
        return f'package update {self.created_at.strftime("%Y-%m-%d %H:%M:%S")}'


class DistUpgrade(Task):
    _salt_task_name = 'dist_upgrade'

    class Meta:
        verbose_name = 'Задача выполнения dist-upgrade'
        verbose_name_plural = 'Задачи выполнения dist-upgrade'
        db_table = 'dist_upgrade'

    def __str__(self):
        return f'dist-upgrade {self.created_at.strftime("%Y-%m-%d %H:%M:%S")}'


class ServiceUpdate(Task):
    _salt_task_name = 'service_update'
    _connection_model = DeviceService

    class Meta:
        verbose_name = 'Обновление сервисов на устройстве'
        verbose_name_plural = 'Обновления сервисов на устройствах'
        db_table = 'service_update'

    def __str__(self):
        return f'service update {self.created_at.strftime("%Y-%m-%d %H:%M:%S")}'