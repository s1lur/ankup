from django.db import models
from django.db.models import constraints
from simple_history.models import HistoricalRecords


class Package(models.Model):
    class Meta:
        verbose_name = 'Пакет'
        verbose_name_plural = 'Пакеты'
        db_table = 'package'

    name = models.CharField(max_length=250, unique=True, verbose_name='Название пакета')
    package_deps = models.ManyToManyField('updater.Package', through='updater.PackagePackageDependency', through_fields=('dependant', 'dependency'), related_name='dependant_packages', blank=True, verbose_name='Зависимости')
    history = HistoricalRecords(
        verbose_name='История изменений пакета',
        verbose_name_plural='Истории изменений пакетов'
    )

    def __str__(self):
        return f'{self.name}'


class PackagePackageDependency(models.Model):
    class Meta:
        verbose_name = 'Зависимость пакета от пакета'
        verbose_name_plural = 'Зависимости пакетов от пакетов'
        db_table = 'package_package_deps'
        constraints = [
            constraints.UniqueConstraint(fields=['dependant', 'dependency'], name='unique_package_package_pair')
        ]

    dependant = models.ForeignKey('updater.Package', on_delete=models.CASCADE, related_name='package_deps_through', verbose_name='Зависимый пакет')
    dependency = models.ForeignKey('updater.Package', on_delete=models.CASCADE, related_name='dependant_packages_through', verbose_name='Пакет-зависимость')
    versions = models.ManyToManyField('updater.Version', related_name='package_package_deps', blank=True, verbose_name='Версии')
