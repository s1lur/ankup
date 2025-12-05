from django.db import models
from updater.choices import TaskStatus


class Task(models.Model):
    class Meta:
        abstract = True

    device = models.ForeignKey('updater.Device', related_name='%(class)ss', on_delete=models.CASCADE,
                               verbose_name='Устройство')
    status = models.CharField(max_length=50, choices=TaskStatus.choices, default=TaskStatus.REQUESTED, verbose_name='Состояние')
    task_id = models.UUIDField(null=True, verbose_name='ID задачи')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    author = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, verbose_name='Автор')


class Update(Task):
    class Meta:
        verbose_name = 'Обновление'
        verbose_name_plural = 'Обновления'
        db_table = 'update'

    version = models.ForeignKey('updater.Version', related_name='updates', on_delete=models.CASCADE, verbose_name='Версия')


class DistUpgrade(Task):
    class Meta:
        verbose_name = 'Задача выполнения dist-upgrade'
        verbose_name_plural = 'Задачи выполнения dist-upgrade'
        db_table = 'dist_upgrade'
