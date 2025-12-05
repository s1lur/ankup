from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html, urlencode

from updater.models import (
    CurrentState, TargetState
)


@admin.register(CurrentState)
class CurrentStateAdmin(admin.ModelAdmin):
    model = CurrentState
    list_display = [
        'view_device_link',
        'view_component_link',
        'view_version_link',
    ]
    search_fields = [
        'device__name',
        'component__name',
        'version__name',
    ]

    def view_device_link(self, obj):
        url = reverse("admin:updater_device_change", args=[obj.device_id])
        return format_html('<a href="{}">{}</a>', url, obj.device)
    view_device_link.short_description = 'Устройство'

    def view_component_link(self, obj):
        url = reverse("admin:updater_component_change", args=[obj.component_id])
        return format_html('<a href="{}">{}</a>', url, obj.component)
    view_component_link.short_description = 'Компонент'

    def view_version_link(self, obj):
        url = reverse("admin:updater_version_change", args=[obj.version_id])
        return format_html('<a href="{}">{}</a>', url, obj.version)
    view_version_link.short_description = 'Версия'


@admin.register(TargetState)
class TargetStateAdmin(admin.ModelAdmin):
    model = CurrentState
    list_display = [
        'view_device_link',
        'view_component_link',
        'view_version_link',
    ]
    search_fields = [
        'device__name',
        'component__name',
        'version__name',
    ]

    def view_device_link(self, obj):
        url = reverse("admin:updater_device_change", args=[obj.device_id])
        return format_html('<a href="{}">{}</a>', url, obj.device)
    view_device_link.short_description = 'Устройство'

    def view_component_link(self, obj):
        url = reverse("admin:updater_component_change", args=[obj.component_id])
        return format_html('<a href="{}">{}</a>', url, obj.component)
    view_component_link.short_description = 'Компонент'

    def view_version_link(self, obj):
        url = reverse("admin:updater_version_change", args=[obj.version_id])
        return format_html('<a href="{}">{}</a>', url, obj.version)
    view_version_link.short_description = 'Версия'
