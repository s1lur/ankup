from django.db import models
from django.utils.translation import gettext_lazy as _


class TaskStatus(models.TextChoices):
    REQUESTED = 'REQUESTED', _('Запрошено')
    PROCESSING = 'PROCESSING', _('В процессе применения')
    SUCCESS = 'SUCCESS', _('Успешно применено')
    ERROR = 'ERROR', _('Ошибка применения')
