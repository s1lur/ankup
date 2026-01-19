from django.contrib import admin
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import path
from django.contrib.admin.apps import AdminConfig
from celery.result import AsyncResult


class CustomAdminConfig(AdminConfig):
    default_site = "ankup.admin.CustomAdminSite"


class CustomAdminSite(admin.AdminSite):
    site_header = 'Система автоматизированного обновления АС «Анклав»'
    site_title = 'САО АС «Анклав»'

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

    def _parse_salt_result(self, raw_result):
        if not raw_result:
            return None

        parsed_data = {}

        for minion_id, steps in raw_result.items():
            minion_steps = []

            if isinstance(steps, str):
                minion_steps.append({
                    'name': 'Error',
                    'status': False,
                    'comment': steps,
                    'changes': None
                })
            elif isinstance(steps, dict):
                for step_id, step_data in steps.items():
                    if step_id == 'retcode': continue

                    step_info = {
                        'name': step_data.get('name', step_id),
                        'status': step_data.get('result', False),
                        'comment': step_data.get('comment', ''),
                        'changes': step_data.get('changes', {}),
                        'duration': step_data.get('duration', 0)
                    }

                    minion_steps.append(step_info)

            parsed_data[minion_id] = minion_steps

        return parsed_data

    def admin_task_status_view(self, request, task_id):
        task = AsyncResult(task_id)
        task_data = {
            "id": task.id,
            "state": task.state,
        }

        if task.state in ['SUCCESS', 'FAILURE']:
            if isinstance(task.result, Exception):
                task_data["error"] = str(task.result)
            else:
                task_data["salt_output"] = self._parse_salt_result(task.result)

        if request.headers.get("Accept", "").startswith("application/json"):
            return JsonResponse(task_data)
        return render(
            request,
            "admin/task_status.html",
            {
                "title": "Состояние задачи",
                "task": task_data,
                "is_popup": False,
            },
        )
