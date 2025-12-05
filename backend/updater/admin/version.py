from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html, urlencode

from updater.models import (
    Version
)

@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    model = Version
    list_display = [
        'id',
        'number',
        'view_component_link',
        'view_current_state_link',
        'view_target_state_link',
        'view_updates_link',
    ]
    list_display_links = [
        'id'
    ]
    search_fields = [
        'id',
        'component__name'
    ]

    def view_component_link(self, obj):
        url = reverse("admin:updater_component_change", args=[obj.component_id])
        return format_html('<a href="{}">{}</a>', url, obj.component)
    view_component_link.short_description = 'Компонент'

    def view_current_state_link(self, obj):
        url = reverse('admin:updater_currentstate_changelist') + '?' + urlencode({'version_id': obj.id})
        return format_html(
            '<a href="{}"> Посмотреть </a>', url)
    view_current_state_link.short_description = 'Текущее состояние'

    def view_target_state_link(self, obj):
        url = reverse('admin:updater_targetstate_changelist') + '?' + urlencode({'version_id': obj.id})
        return format_html(
            '<a href="{}"> Посмотреть </a>', url)
    view_target_state_link.short_description = 'Целевое состояние'

    def view_updates_link(self, obj):
        count = obj.update_set.count()
        url = reverse('admin:updater_update_changelist') + '?' + urlencode({'version_id': obj.id})
        return format_html(
            f'<a href="{{}}"> {{}} обновлени{"е" if count == 1 else "я" if 2 <= count <= 4 else "й"} </a>', url, count)
    view_updates_link.short_description = 'Обновления'
