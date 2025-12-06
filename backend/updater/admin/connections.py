from django.db import models
from django import forms
from django.forms.models import BaseInlineFormSet
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html, urlencode
from django_json_widget.widgets import JSONEditorWidget
from simple_history.admin import SimpleHistoryAdmin

from updater.models import (
    DevicePackage, DeviceService, Version, Package, Service,
    HistoricalDevicePackage, HistoricalDeviceService,
)


class DevicePackageFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors): return

        existing_ids = set()
        if self.instance.pk:
            existing_ids = set(
                DevicePackage.objects.filter(device=self.instance)
                .values_list('package_id', flat=True)
            )

        added_ids = set()
        removed_ids = set()

        for form in self.forms:
            if not form.cleaned_data: continue
            pkg = form.cleaned_data.get('package')
            ver = form.cleaned_data.get('version')

            if not pkg: continue

            if ver and ver.package_id != pkg.id:
                form.add_error(
                    'version',
                    f"Эта версия принадлежит пакету '{ver.package.name}', а выбран '{pkg.name}'."
                )

            is_delete = form.cleaned_data.get('DELETE')

            if is_delete:
                if form.instance.pk: removed_ids.add(pkg.id)
            else:
                added_ids.add(pkg.id)

        final_package_ids = (existing_ids - removed_ids) | added_ids

        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE'): continue

            pkg = form.cleaned_data.get('package')
            if not pkg: continue

            required_ids = set(pkg.dependencies.values_list('id', flat=True))
            missing = required_ids - final_package_ids

            if missing:
                names = Package.objects.filter(id__in=missing).values_list('name', flat=True)
                form.add_error('package', f"Отсутствуют зависимости: {', '.join(names)}")


class DeviceServiceFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors): return

        existing_svc_ids = set()
        if self.instance.pk:
            existing_svc_ids = set(
                DeviceService.objects.filter(device=self.instance).values_list('service_id', flat=True))

        added_svc_ids = set()
        removed_svc_ids = set()

        for form in self.forms:
            if not form.cleaned_data: continue
            svc = form.cleaned_data.get('service')
            if form.cleaned_data.get('DELETE'):
                if form.instance.pk and svc: removed_svc_ids.add(svc.id)
            elif svc:
                added_svc_ids.add(svc.id)

        final_service_ids = (existing_svc_ids - removed_svc_ids) | added_svc_ids

        installed_package_ids = set()
        if self.instance.pk:
            installed_package_ids = set(
                DevicePackage.objects.filter(device=self.instance).values_list('package_id', flat=True))

        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE'): continue
            svc = form.cleaned_data.get('service')
            if not svc: continue

            req_pkg = set(svc.package_deps.values_list('id', flat=True))
            missing_pkg = req_pkg - installed_package_ids
            if missing_pkg:
                names = Package.objects.filter(id__in=missing_pkg).values_list('name', flat=True)
                form.add_error('service',
                               f"Требуются пакеты: {', '.join(names)}. (Сохраните пакеты перед добавлением сервиса)")

            req_svc = set(svc.service_deps.values_list('id', flat=True))
            missing_svc = req_svc - final_service_ids
            if missing_svc:
                names = Service.objects.filter(id__in=missing_svc).values_list('name', flat=True)
                form.add_error('service', f"Требуются сервисы: {', '.join(names)}")


@admin.register(DevicePackage)
class DevicePackageAdmin(SimpleHistoryAdmin):
    model = DevicePackage
    list_display = [
        'id',
        'applied',
        'view_device_link',
        'view_package_link',
        'view_version_link',
        'parameters',
    ]
    list_display_links = [
        'id',
    ]
    list_filter = [
        'applied'
    ]
    search_fields = [
        'device__name',
        'package__name',
        'version__name',
    ]
    autocomplete_fields = [
        'device',
        'package',
        'version',
    ]
    readonly_fields = [
        'applied'
    ]
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

    def get_readonly_fields(self, request, obj=None):
        fields = ['applied']
        if obj:
            fields += ['device', 'package']
        return fields

    def view_device_link(self, obj):
        url = reverse("admin:updater_device_change", args=[obj.device_id])
        return format_html('<a href="{}">{}</a>', url, obj.device)
    view_device_link.short_description = 'Устройство'

    def view_package_link(self, obj):
        url = reverse("admin:updater_package_change", args=[obj.package_id])
        return format_html('<a href="{}">{}</a>', url, obj.package)
    view_package_link.short_description = 'Пакет'

    def view_version_link(self, obj):
        url = reverse("admin:updater_version_change", args=[obj.version_id])
        return format_html('<a href="{}">{}</a>', url, obj.version)
    view_version_link.short_description = 'Версия'


@admin.register(DeviceService)
class DeviceServiceAdmin(SimpleHistoryAdmin):
    model = DeviceService
    list_display = [
        'id',
        'enabled',
        'applied',
        'view_device_link',
        'view_service_link',
    ]
    list_filter = [
        'applied',
        'enabled'
    ]
    autocomplete_fields = [
        'device',
        'service',
    ]
    search_fields = [
        'device__name',
        'service__name',
    ]
    readonly_fields = [
        'applied'
    ]

    def get_readonly_fields(self, request, obj=None):
        fields = ['applied']
        if obj:
            fields += ['device', 'service']
        return fields

    def view_device_link(self, obj):
        url = reverse("admin:updater_device_change", args=[obj.device_id])
        return format_html('<a href="{}">{}</a>', url, obj.device)
    view_device_link.short_description = 'Устройство'

    def view_service_link(self, obj):
        url = reverse("admin:updater_service_change", args=[obj.service_id])
        return format_html('<a href="{}">{}</a>', url, obj.service)
    view_service_link.short_description = 'Сервис'

