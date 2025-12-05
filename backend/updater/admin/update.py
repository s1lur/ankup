from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html, urlencode

from updater.models import (
    Update, DistUpgrade
)


@admin.register(DistUpgrade)
class DistUpgradeAdmin(admin.ModelAdmin):
    model = DistUpgrade
    list_display = [
        'id',
        'view_device_link',
        'view_task_link',
        'status',
        'created_at',
        'view_author_link'
    ]
    list_display_links = [
        'id'
    ]
    search_fields = [
        'id',
    ]
    readonly_fields = [
        'created_at',
        'status',
        'task_id',
        'author',
    ]
    list_filter = [
        'status'
    ]

    def view_device_link(self, obj):
        url = reverse("admin:updater_device_change", args=[obj.device_id])
        return format_html('<a href="{}">{}</a>', url, obj.device)
    view_device_link.short_description = 'Устройство'

    def view_version_link(self, obj):
        url = reverse("admin:updater_version_change", args=[obj.version_id])
        return format_html('<a href="{}">{}</a>', url, obj.version)
    view_version_link.short_description = 'Версия'

    def view_author_link(self, obj):
        url = reverse("admin:auth_user_change", args=[obj.author_id])
        return format_html('<a href="{}">{}</a>', url, obj.author)
    view_author_link.short_description = 'Автор'

    def view_task_link(self, obj):
        url = reverse("admin:task_status", args=[obj.task_id])
        return format_html('<a href="{}"> Подробности </a>', url)
    view_task_link.short_description = 'Ссылка на задачу'

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        return super().save_model(request, obj, form, change)


@admin.register(Update)
class UpdateAdmin(admin.ModelAdmin):
    model = Update
    list_display = [
        'id',
        'view_device_link',
        'view_version_link',
        'view_task_link',
        'status',
        'created_at',
        'view_author_link'
    ]
    list_display_links = [
        'id'
    ]
    search_fields = [
        'id',
    ]
    readonly_fields = [
        'created_at',
        'status',
        'task_id',
        'author',
    ]
    list_filter = [
        'status'
    ]

    def view_device_link(self, obj):
        url = reverse("admin:updater_device_change", args=[obj.device_id])
        return format_html('<a href="{}">{}</a>', url, obj.device)
    view_device_link.short_description = 'Устройство'

    def view_version_link(self, obj):
        url = reverse("admin:updater_version_change", args=[obj.version_id])
        return format_html('<a href="{}">{}</a>', url, obj.version)
    view_version_link.short_description = 'Версия'

    def view_author_link(self, obj):
        url = reverse("admin:auth_user_change", args=[obj.author_id])
        return format_html('<a href="{}">{}</a>', url, obj.author)
    view_author_link.short_description = 'Автор'

    def view_task_link(self, obj):
        url = reverse("admin:task_status", args=[obj.task_id])
        return format_html('<a href="{}"> Подробности </a>', url)
    view_task_link.short_description = 'Ссылка на задачу'

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        return super().save_model(request, obj, form, change)

