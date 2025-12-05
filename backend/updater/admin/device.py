from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html, urlencode
from django.shortcuts import redirect

from updater.models import (
    Device, Version, DistUpgrade
)
from updater.celery import (
    dist_upgrade
)


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    model = Device
    list_display = [
        'id',
        'name',
        'view_components_link',
        'view_all_versions_link',
        'view_current_state_link',
        'view_target_state_link',
        'view_updates_link',
    ]
    list_display_links = [
        'id'
    ]
    search_fields = [
        'id',
        'name'
    ]
    actions = ['run_dist_upgrade']

    def view_components_link(self, obj):
        count = obj.components.count()
        url = reverse('admin:updater_component_changelist') + '?' + urlencode({'devices__id': obj.id})
        return format_html(f'<a href="{{}}"> {{}} компонент{"" if count == 1 else "а" if 2 <= count <= 4 else "ов"} </a>', url, count)
    view_components_link.short_description = 'Компоненты'

    def view_all_versions_link(self, obj):
        count = Version.objects.filter(component__devices__id=obj.id).count()
        url = reverse('admin:updater_version_changelist') + '?' + urlencode({'component__devices__id': obj.id})
        return format_html(
            f'<a href="{{}}"> {{}} верси{"я" if count == 1 else "и" if 2 <= count <= 4 else "й"} </a>', url, count)
    view_all_versions_link.short_description = 'Доступные версии'

    def view_current_state_link(self, obj):
        url = reverse('admin:updater_currentstate_changelist') + '?' + urlencode({'device_id': obj.id})
        return format_html(
            '<a href="{}"> Посмотреть </a>', url)
    view_current_state_link.short_description = 'Текущее состояние'

    def view_target_state_link(self, obj):
        url = reverse('admin:updater_targetstate_changelist') + '?' + urlencode({'device_id': obj.id})
        return format_html(
            '<a href="{}"> Посмотреть </a>', url)
    view_target_state_link.short_description = 'Целевое состояние'

    def view_updates_link(self, obj):
        count = obj.updates.count()
        url = reverse('admin:updater_update_changelist') + '?' + urlencode({'device_id': obj.id})
        return format_html(
            f'<a href="{{}}"> {{}} обновлени{"е" if count == 1 else "я" if 2 <= count <= 4 else "й"} </a>', url, count)
    view_updates_link.short_description = 'Обновления'

    @admin.action(description="Выполнить dist-upgrade для выбранных устройств")
    def run_dist_upgrade(self, request, queryset):
        objs = DistUpgrade.objects.bulk_create([
            DistUpgrade(device=d, author=request.author)
            for d in queryset
        ])
        return redirect('admin:updater_distupgrade_changelist', id__in=objs.values_list('pk', flat=True))
