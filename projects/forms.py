from django import forms

from projects.models import Project
from team_finder.validators import validate_repository_url


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
        if "status" in self.fields:
            self.fields["status"].choices = Project.STATUS_CHOICES

    def clean_github_url(self):
        return validate_repository_url(self.cleaned_data.get("github_url", ""))
