from django.db import models
from django.forms.models import BaseInlineFormSet
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html, urlencode
from django_json_widget.widgets import JSONEditorWidget
from simple_history.admin import SimpleHistoryAdmin

from updater.models import (
    DevicePackage, DeviceService, Package, Service,
)


class DevicePackageFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors): return

        if self.instance.pk:
            installed_map = dict(
                DevicePackage.objects.filter(device=self.instance)
                .values_list('package_id', 'version_id')
            )
        else:
            installed_map = {}

        for form in self.forms:
            if not form.cleaned_data: continue

            pkg = form.cleaned_data.get('package')
            ver = form.cleaned_data.get('version')
            is_delete = form.cleaned_data.get('DELETE')

            if pkg:
                if is_delete:
                    installed_map.pop(pkg.id, None)
                else:
                    installed_map[pkg.id] = ver.id if ver else None

        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE'): continue

            current_pkg = form.cleaned_data.get('package')
            if not current_pkg: continue

            dependencies = current_pkg.package_deps_through.all().prefetch_related('versions')

            for dep_link in dependencies:
                required_pkg = dep_link.dependency
                allowed_versions = dep_link.versions.all()
                allowed_ver_ids = set(v.id for v in allowed_versions)

                if required_pkg.id not in installed_map:
                    form.add_error(
                        'package',
                        f"Отсутствует зависимость: пакет '{required_pkg.name}'."
                    )
                    continue

                if allowed_ver_ids:
                    installed_ver_id = installed_map[required_pkg.id]

                    if installed_ver_id is None:
                        allowed_strs = ", ".join([str(v.number) for v in allowed_versions])
                        form.add_error(
                            'package',
                            f"Для '{required_pkg.name}' требуется одна из версий: [{allowed_strs}], "
                            f"но версия не выбрана."
                        )
                    elif installed_ver_id not in allowed_ver_ids:
                        allowed_strs = ", ".join([str(v.number) for v in allowed_versions])

                        form.add_error(
                            'package',
                            f"Неверная версия зависимости '{required_pkg.name}'. "
                            f"Требуется: [{allowed_strs}]."
                        )


class DeviceServiceFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors): return

        device = self.instance

        if not device.pk:
            installed_pkg_map = {}
        else:
            installed_pkg_map = dict(
                DevicePackage.objects.filter(device=device)
                .values_list('package_id', 'version_id')
            )

        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE'): continue

            service = form.cleaned_data.get('service')
            if not service: continue

            dependencies = service.package_deps_through.all().prefetch_related('versions')

            for dep_link in dependencies:
                required_pkg = dep_link.dependency
                allowed_versions = dep_link.versions.all()
                allowed_ver_ids = set(v.id for v in allowed_versions)

                if required_pkg.id not in installed_pkg_map:
                    form.add_error(
                        'service',
                        f"Сервис требует пакет '{required_pkg.name}', который не установлен."
                    )
                    continue

                if allowed_ver_ids:
                    installed_ver_id = installed_pkg_map[required_pkg.id]

                    if installed_ver_id not in allowed_ver_ids:
                        allowed_strs = ", ".join([str(v.number) for v in allowed_versions])
                        form.add_error(
                            'service',
                            f"Сервис требует пакет '{required_pkg.name}' одной из версий: [{allowed_strs}]. "
                            f"Проверьте установленную версию."
                        )


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

