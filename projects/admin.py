from django.contrib import admin

from projects.models import Project, Skill


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "status", "created_at")
    search_fields = ("name", "owner__email", "owner__name", "owner__surname")
    list_filter = ("status", "created_at")


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
