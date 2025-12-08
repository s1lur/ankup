from django.contrib import admin
from django.db import models, transaction
from django import forms
from django.urls import reverse
from django.utils.html import format_html, urlencode
from django.shortcuts import redirect
from django_json_widget.widgets import JSONEditorWidget

from updater.models import (
    Device, Version, DistUpgrade, DeviceService, DevicePackage, PackageUpdate, ServiceUpdate,
)
from .connections import DevicePackageFormSet, DeviceServiceFormSet



class DevicePackageInline(admin.TabularInline):
    model = DevicePackage
    formset = DevicePackageFormSet
    autocomplete_fields = [
        'package',
        'version',
    ]
    extra = 1
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

    def get_readonly_fields(self, request, obj=None):
        fields = ['applied']
        if obj:
            fields += ['package']
        return fields


class DeviceServiceInline(admin.TabularInline):
    model = DeviceService
    formset = DeviceServiceFormSet
    autocomplete_fields = [
        'service',
    ]
    extra = 1

    def get_readonly_fields(self, request, obj=None):
        fields = ['applied']
        if obj:
            fields += ['service']
        return fields


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    model = Device
    list_display = [
        'id',
        'name',
        'is_available',
        'last_seen',
        'view_packages_link',
        'view_services_link',
        'view_device_packages_link',
        'view_device_services_link',
        'view_all_versions_link',
    ]
    list_display_links = [
        'id',
    ]
    search_fields = [
        'id',
        'name',
    ]
    readonly_fields = [
        'is_available',
        'last_seen',
    ]
    actions = ['run_package_update', 'run_dist_upgrade', 'run_service_update']
    inlines = [
        DevicePackageInline,
        DeviceServiceInline,
    ]

    def view_packages_link(self, obj):
        count = obj.packages.count()
        url = reverse('admin:updater_package_changelist') + '?' + urlencode({'devices__id': obj.id})
        return format_html(f'<a href="{{}}"> {{}} пакет{"" if count == 1 else "а" if 2 <= count <= 4 else "ов"} </a>', url, count)
    view_packages_link.short_description = 'Пакеты'

    def view_services_link(self, obj):
        count = obj.services.count()
        url = reverse('admin:updater_service_changelist') + '?' + urlencode({'devices__id': obj.id})
        return format_html(f'<a href="{{}}"> {{}} сервис{"" if count == 1 else "а" if 2 <= count <= 4 else "ов"} </a>', url, count)
    view_services_link.short_description = 'Сервисы'

    def view_device_packages_link(self, obj):
        count = obj.device_packages.count()
        url = reverse('admin:updater_devicepackage_changelist') + '?' + urlencode({'device_id': obj.id})
        return format_html(f'<a href="{{}}"> {{}} связ{"ь" if count == 1 else "и" if 2 <= count <= 4 else "ей"} пакет-устройство </a>', url, count)
    view_device_packages_link.short_description = 'Связи с пакетами'

    def view_device_services_link(self, obj):
        count = obj.device_services.count()
        url = reverse('admin:updater_deviceservice_changelist') + '?' + urlencode({'device_id': obj.id})
        return format_html(f'<a href="{{}}"> {{}} связ{"ь" if count == 1 else "и" if 2 <= count <= 4 else "ей"} сервис-устройство </a>', url, count)
    view_device_services_link.short_description = 'Связи с сервисами'

    def view_services_link(self, obj):
        count = obj.services.count()
        url = reverse('admin:updater_service_changelist') + '?' + urlencode({'devices__id': obj.id})
        return format_html(f'<a href="{{}}"> {{}} сервис{"" if count == 1 else "а" if 2 <= count <= 4 else "ов"} </a>', url, count)
    view_services_link.short_description = 'Сервисы'

    def view_all_versions_link(self, obj):
        count = Version.objects.filter(package__devices__id=obj.id).count()
        url = reverse('admin:updater_version_changelist') + '?' + urlencode({'package__devices__id': obj.id})
        return format_html(
            f'<a href="{{}}"> {{}} верси{"я" if count == 1 else "и" if 2 <= count <= 4 else "й"} </a>', url, count)
    view_all_versions_link.short_description = 'Доступные версии'

    @admin.action(description="Обновить пакеты и конфиги на выбранных устройствах")
    def run_package_update(self, request, queryset):
        ids = list()
        with transaction.atomic():
            for d in queryset:
                pu = PackageUpdate(device=d, author=request.user)
                pu.save()
                ids.append(pu.id)
        return redirect(reverse('admin:updater_packageupdate_changelist') + '?' + urlencode({'id__in': ids}))

    @admin.action(description="Выполнить dist-upgrade для выбранных устройств")
    def run_dist_upgrade(self, request, queryset):
        ids = list()
        with transaction.atomic():
            for d in queryset:
                du = DistUpgrade(device=d, author=request.user)
                du.save()
                ids.append(du.id)
        return redirect(reverse('admin:updater_distupgrade_changelist') + '?' + urlencode({'id__in': ids}))

    @admin.action(description="Обновить сервисы на выбранных устройствах")
    def run_service_update(self, request, queryset):
        ids = list()
        with transaction.atomic():
            for d in queryset:
                su = ServiceUpdate(device=d, author=request.user)
                su.save()
                ids.append(su.id)
        return redirect(reverse('admin:updater_serviceupdate_changelist') + '?' + urlencode({'id__in': ids}))
