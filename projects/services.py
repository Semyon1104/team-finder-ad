from projects.models import Project


def get_projects_queryset():
    return Project.objects.select_related("owner").prefetch_related("participants", "skills")
