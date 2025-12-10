from croniter import croniter

from django.db import models
from django.core.exceptions import ValidationError
from simple_history.models import HistoricalRecords


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
    antivirus_schedule = models.CharField(
        max_length=100, blank=True, null=True, verbose_name='Расписание обновления баз сигнатур антивируса',
        help_text='Формат: * * * * * (м ч д м дн). Оставьте пустым, чтобы отключить.'
    )
    next_run_at = models.DateTimeField(blank=True, null=True, db_index=True, verbose_name='Время следующего запуска обновления антивируса')
    history = HistoricalRecords(
        verbose_name='История изменений устройства',
        verbose_name_plural='Истории изменений устройств'
    )

    def __str__(self):
        return f'{self.name}'

    def clean(self):
        if self.antivirus_schedule:
            try:
                if not croniter.is_valid(self.antivirus_schedule):
                    raise ValidationError({'antivirus_schedule': 'Некорректный формат crontab'})
            except Exception:
                raise ValidationError({'antivirus_schedule': 'Ошибка парсинга crontab'})