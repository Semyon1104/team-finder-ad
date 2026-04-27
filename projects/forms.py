from urllib.parse import urlparse

from django import forms

from projects.models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "GitHub",
            "status": "Статус",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Название проекта"}),
            "description": forms.Textarea(attrs={"placeholder": "Описание проекта"}),
            "github_url": forms.URLInput(attrs={"placeholder": "Ссылка на GitHub"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Оставляем значения open/closed (как в модели),
        # но показываем пользователю русские подписи.
        if "status" in self.fields:
            self.fields["status"].choices = [
                ("open", "Открыт"),
                ("closed", "Закрыт"),
            ]

    def clean_github_url(self):
        value = self.cleaned_data.get("github_url", "")
        if not value:
            return value
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or "github.com" not in parsed.netloc.lower():
            raise forms.ValidationError("Ссылка должна вести на github.com")
        return value
