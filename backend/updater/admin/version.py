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
        'view_package_link',
    ]
    list_display_links = [
        'id',
    ]
    search_fields = [
        'id',
        'package__name',
    ]

    def get_readonly_fields(self, obj):
        if obj:
            return ['package']
        return []

    def view_package_link(self, obj):
        url = reverse("admin:updater_package_change", args=[obj.package_id])
        return format_html('<a href="{}">{}</a>', url, obj.package)
    view_package_link.short_description = 'Пакет'
