from django.db import models


class State(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, db_column='id', verbose_name='ID')
    device = models.ForeignKey('updater.Device', db_column='device_id', on_delete=models.DO_NOTHING, verbose_name='Устройство')
    component = models.ForeignKey('updater.Component', db_column='component_id', on_delete=models.DO_NOTHING, verbose_name='Компонент')
    version = models.ForeignKey('updater.Version', db_column='version_id', on_delete=models.DO_NOTHING, verbose_name='Версия')


class CurrentState(State):
    class Meta:
        db_table = 'current_state'
        managed = False
        verbose_name = 'Текущее состояние'
        verbose_name_plural = 'Текущее состояние'


class TargetState(State):
    class Meta:
        db_table = 'target_state'
        managed = False
        verbose_name = 'Целевое состояние'
        verbose_name_plural = 'Целевое состояние'
