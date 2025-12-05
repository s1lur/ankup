from django.contrib import admin
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import path
from django.contrib.admin.apps import AdminConfig
from celery.result import AsyncResult


class CustomAdminConfig(AdminConfig):
    default_site = "ankup.admin.CustomAdminSite"


class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "task-status/<str:task_id>/",
                self.admin_view(self.admin_task_status_view),
                name="task_status",
            )
        ]
        return custom_urls + urls

    def admin_task_status_view(self, request, task_id):
        task = AsyncResult(task_id)
        task_data = {
            "id": task.id,
            "name": task.name,
            "state": task.state,
            "result": task.result,
        }

        if request.headers.get("Accept", "").startswith("application/json"):
            return JsonResponse(task_data)

        return render(
            request,
            "admin/task_status.html",
            {
                "title": "Состояние задачи",
                "task": task_data,
            },
        )