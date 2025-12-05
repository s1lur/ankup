from django.db import models
from django.utils.translation import gettext_lazy as _


class TaskStatus(models.TextChoices):
    REQUESTED = 'REQUESTED', _('Запрошено')
    PROCESSING = 'PROCESSING', _('В процессе применения')
    ACTIVE = 'ACTIVE', _('Активно')
    ERROR = 'ERROR', _('Ошибка применения')
    PAST = 'PAST', _('В прошлом')
