from django.contrib import admin

from projects.models import Project, Skill


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "status", "participants_count", "skills_list", "created_at")
    list_editable = ("status",)
    search_fields = ("name", "owner__email", "owner__name", "owner__surname")
    list_filter = ("status", "created_at")

    @admin.display(description="Участники")
    def participants_count(self, obj):
        return obj.participants.count()

    @admin.display(description="Скиллы")
    def skills_list(self, obj):
        return ", ".join(obj.skills.values_list("name", flat=True))


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
