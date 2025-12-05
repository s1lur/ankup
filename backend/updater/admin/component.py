from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html, urlencode

from updater.models import (
    Component
)

@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    model = Component
    list_display = [
        'id',
        'human_name',
        'package_name',
        'view_devices_link',
        'view_all_versions_link'
    ]
    list_display_links = [
        'id'
    ]
    search_fields = [
        'id',
        'name'
    ]

    def view_devices_link(self, obj):
        count = obj.devices.count()
        url = reverse('admin:updater_device_changelist') + '?' + urlencode({'components__id': obj.id})
        return format_html(f'<a href="{{}}"> {{}} устройств{"о" if count == 1 else "а" if 2 <= count <= 4 else ""} </a>', url, count)
    view_devices_link.short_description = 'Устройства'

    def view_all_versions_link(self, obj):
        count = obj.versions.count()
        url = reverse('admin:updater_version_changelist') + '?' + urlencode({'component_id': obj.id})
        return format_html(
            f'<a href="{{}}"> {{}} верси{"я" if count == 1 else "и" if 2 <= count <= 4 else "й"} </a>', url, count)
    view_all_versions_link.short_description = 'Доступные версии'
