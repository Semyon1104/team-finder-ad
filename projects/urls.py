from django.urls import path

from projects import views

app_name = "projects"

urlpatterns = [
    path("list/", views.project_list_view, name="list"),
    path("create-project/", views.project_form_view, name="create"),
    path("skills/", views.skills_suggest_view, name="skills_suggest"),
    path("<int:project_id>/", views.project_detail_view, name="details"),
    path("<int:project_id>/edit/", views.project_form_view, name="edit"),
    path("<int:project_id>/skills/add/", views.add_project_skill_view, name="skills_add"),
    path(
        "<int:project_id>/skills/<int:skill_id>/remove/",
        views.remove_project_skill_view,
        name="skills_remove",
    ),
    path(
        "<int:project_id>/toggle-participate/",
        views.toggle_participate_view,
        name="toggle_participate",
    ),
    path("<int:project_id>/complete/", views.complete_project_view, name="complete"),
]
