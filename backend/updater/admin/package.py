from django.contrib import admin
from django.db import models
from django.urls import reverse
from django.utils.html import format_html, urlencode
from django_json_widget.widgets import JSONEditorWidget
from simple_history.admin import SimpleHistoryAdmin

from updater.models import (
    Package, ConfigTemplate, PackagePackageDependency
)
from .deps import VersionedDependencyInline


class ConfigTemplateInline(admin.TabularInline):
    model = ConfigTemplate
    extra = 1
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }


class PackagePackageDepsInline(VersionedDependencyInline):
    model = PackagePackageDependency


@admin.register(Package)
class PackageAdmin(SimpleHistoryAdmin):
    model = Package
    inlines = [
        ConfigTemplateInline, PackagePackageDepsInline,
    ]
    list_display = [
        'id',
        'name',
        'view_devices_link',
        'view_all_versions_link',
        'view_config_templates_link',
        'view_package_deps_link',
        'view_dependant_services_link',
        'view_dependant_packages_link',
    ]
    list_display_links = [
        'id',
    ]
    search_fields = [
        'id',
        'name',
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['name']
        return []

    def view_devices_link(self, obj):
        count = obj.devices.count()
        url = reverse('admin:updater_device_changelist') + '?' + urlencode({'packages__id': obj.id})
        return format_html(f'<a href="{{}}"> {{}} устройств{"о" if count == 1 else "а" if 2 <= count <= 4 else ""} </a>', url, count)
    view_devices_link.short_description = 'Устройства'

    def view_all_versions_link(self, obj):
        count = obj.versions.count()
        url = reverse('admin:updater_version_changelist') + '?' + urlencode({'package_id': obj.id})
        return format_html(
            f'<a href="{{}}"> {{}} верси{"я" if count == 1 else "и" if 2 <= count <= 4 else "й"} </a>', url, count)
    view_all_versions_link.short_description = 'Доступные версии'

    def view_config_templates_link(self, obj):
        count = obj.configs.count()
        url = reverse('admin:updater_configtemplate_changelist') + '?' + urlencode({'package_id': obj.id})
        return format_html(f'<a href="{{}}"> {{}} шаблон{"" if count == 1 else "а" if 2 <= count <= 4 else "ов"} конфиг{"а" if count == 1 else "ов"} </a>', url, count)
    view_config_templates_link.short_description = 'Шаблоны конфигов'

    def view_package_deps_link(self, obj):
        count = obj.package_deps.count()
        url = reverse('admin:updater_package_changelist') + '?' + urlencode({'dependant_packages__id': obj.id})
        return format_html(f'<a href="{{}}"> {{}} пакет{"" if count == 1 else "а" if 2 <= count <= 4 else "ов"} </a>', url, count)
    view_package_deps_link.short_description = 'Пакеты-зависимости'

    def view_dependant_services_link(self, obj):
        count = obj.dependant_services.count()
        url = reverse('admin:updater_service_changelist') + '?' + urlencode({'package_deps__id': obj.id})
        return format_html(f'<a href="{{}}"> {{}} сервис{"" if count == 1 else "а" if 2 <= count <= 4 else "ов"} </a>', url, count)
    view_dependant_services_link.short_description = 'Зависимые сервисы'

    def view_dependant_packages_link(self, obj):
        count = obj.dependant_packages.count()
        url = reverse('admin:updater_package_changelist') + '?' + urlencode({'package_deps__id': obj.id})
        return format_html(f'<a href="{{}}"> {{}} пакет{"" if count == 1 else "а" if 2 <= count <= 4 else "ов"} </a>', url, count)
    view_dependant_packages_link.short_description = 'Зависимые пакеты'
