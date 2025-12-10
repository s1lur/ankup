from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django import forms


class VersionedDependencyFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        if any(self.errors):
            return

        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE'):
                continue

            dependency_pkg = form.cleaned_data.get('dependency')
            if not dependency_pkg:
                continue

            selected_versions = form.cleaned_data.get('versions')
            if not selected_versions:
                continue

            invalid_versions = selected_versions.exclude(package_id=dependency_pkg.id)

            if invalid_versions.exists():
                invalid_numbers = ", ".join([v.number for v in invalid_versions])
                correct_pkg_names = ", ".join(set([v.package.name for v in invalid_versions]))

                form.add_error(
                    'versions',
                    ValidationError(
                        f"Ошибка версий: [{invalid_numbers}]. "
                        f"Они принадлежат пакету(ам) '{correct_pkg_names}', "
                        f"а вы выбрали зависимость от '{dependency_pkg.name}'. "
                    )
                )


class DependencyInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['dependency'].disabled = True


class DependencyInline(admin.TabularInline):
    model = None
    form = DependencyInlineForm
    fk_name = 'dependant'
    autocomplete_fields = [
        'dependency',
    ]
    extra = 0

class VersionedDependencyInline(DependencyInline):
    autocomplete_fields = [
        'dependency',
        'versions',
    ]
    formset = VersionedDependencyFormSet

