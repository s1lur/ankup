from django.contrib import admin
from django.db import models
from django.urls import reverse
from django.utils.html import format_html, urlencode
from django_json_widget.widgets import JSONEditorWidget
from simple_history.admin import SimpleHistoryAdmin

from updater.models import ConfigTemplate


@admin.register(ConfigTemplate)
class ConfigTemplateAdmin(SimpleHistoryAdmin):
    model = ConfigTemplate
    list_display = [
        'id',
        'name',
        'file',
        'dest_path',
        'file_mode',
        'parameters',
        'view_package_link',
    ]
    list_display_links = [
        'id',
    ]
    search_fields = [
        'name',
    ]
    autocomplete_fields = [
        'package'
    ]
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

    def view_package_link(self, obj):
        url = reverse("admin:updater_package_change", args=[obj.package_id])
        return format_html('<a href="{}">{}</a>', url, obj.package)
    view_package_link.short_description = 'Пакет'
