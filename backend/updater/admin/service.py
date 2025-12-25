from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html, urlencode
from simple_history.admin import SimpleHistoryAdmin

from updater.models import (
    Service, ServiceServiceDependency
)
from .deps import DependencyInline


class ServiceServiceDependencyInline(DependencyInline):
    model = ServiceServiceDependency


@admin.register(Service)
class ServiceAdmin(SimpleHistoryAdmin):
    model = Service
    inlines = [
        ServiceServiceDependencyInline
    ]
    list_display = [
        'id',
        'name',
        'view_service_deps_link',
        'view_dependant_services_link',
        'view_package_link',
        'view_devices_link',
    ]
    list_display_links = [
        'id',
    ]
    autocomplete_fields = [
        'package',
    ]
    search_fields = [
        'name',
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['name', 'package']
        return []

    def view_service_deps_link(self, obj):
        count = obj.service_deps.count()
        url = reverse('admin:updater_service_changelist') + '?' + urlencode({'dependant_services__id': obj.id})
        return format_html(
            f'<a href="{{}}"> {{}} сервис{"" if count == 1 else "а" if 2 <= count <= 4 else "ов"} </a>',
            url, count)
    view_service_deps_link.short_description = 'Сервисы, от которых зависит'

    def view_dependant_services_link(self, obj):
        count = obj.dependant_services.count()
        url = reverse('admin:updater_service_changelist') + '?' + urlencode({'service_deps__id': obj.id})
        return format_html(
            f'<a href="{{}}"> {{}} сервис{"" if count == 1 else "а" if 2 <= count <= 4 else "ов"} </a>',
            url, count)
    view_dependant_services_link.short_description = 'Зависимые сервисы'

    def view_package_link(self, obj):
        url = reverse("admin:updater_package_change", args=[obj.package_id])
        return format_html('<a href="{}">{}</a>', url, obj.package)
    view_package_link.short_description = 'Пакет'

    def view_devices_link(self, obj):
        count = obj.devices.count()
        url = reverse('admin:updater_device_changelist') + '?' + urlencode({'services__id': obj.id})
        return format_html(f'<a href="{{}}"> {{}} устройств{"о" if count == 1 else "а" if 2 <= count <= 4 else ""} </a>', url, count)
    view_devices_link.short_description = 'Устройства'
