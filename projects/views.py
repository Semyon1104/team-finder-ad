import json
from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from projects.forms import ProjectForm
from projects.models import Project, Skill
from projects.services import get_projects_queryset
from team_finder.constants import (
    ITEMS_PER_PAGE,
    PROJECT_STATUS_CLOSED,
    PROJECT_STATUS_OPEN,
    SKILLS_SUGGEST_LIMIT,
)
from team_finder.services import paginate_queryset


@require_GET
def project_list_view(request):
    projects_qs = get_projects_queryset()
    all_skills = Skill.objects.order_by("name").values_list("name", flat=True)
    active_skill = request.GET.get("skill")
    if active_skill:
        projects_qs = projects_qs.filter(skills__name=active_skill).distinct()

    projects_qs = projects_qs.order_by("-created_at")
    page_obj = paginate_queryset(projects_qs, ITEMS_PER_PAGE, request.GET.get("page"))
    return render(
        request,
        "projects/project_list.html",
        {
            "projects": page_obj.object_list,
            "page_obj": page_obj,
            "all_skills": all_skills,
            "active_skill": active_skill,
        },
    )


@require_GET
def project_detail_view(request, project_id):
    project = get_object_or_404(
        get_projects_queryset(),
        pk=project_id,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def project_form_view(request, project_id=None):
    project = None
    is_edit = project_id is not None
    if is_edit:
        project = get_object_or_404(Project, pk=project_id, owner=request.user)

    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        project = form.save(commit=False)
        if not is_edit:
            project.owner = request.user
        project.save()
        if not is_edit:
            project.participants.add(request.user)
        return redirect(reverse("projects:details", kwargs={"project_id": project.id}))

    return render(
        request,
        "projects/create-project.html",
        {
            "form": form,
            "is_edit": is_edit,
        },
    )


@login_required
@require_POST
def toggle_participate_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    is_participant = project.participants.filter(pk=request.user.pk).exists()
    if is_participant:
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)
    return JsonResponse({"status": "ok", "participant": not is_participant})


@login_required
@require_POST
def complete_project_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id or project.status != PROJECT_STATUS_OPEN:
        return JsonResponse({"status": "error"}, status=HTTPStatus.BAD_REQUEST)
    project.status = PROJECT_STATUS_CLOSED
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": PROJECT_STATUS_CLOSED})


@require_GET
def skills_suggest_view(request):
    query = request.GET.get("q", "").strip()
    queryset = Skill.objects.all()
    if query:
        queryset = queryset.filter(name__istartswith=query)
    skills = queryset.order_by("name").values("id", "name")[:SKILLS_SUGGEST_LIMIT]
    return JsonResponse(list(skills), safe=False)


@login_required
@require_POST
def add_project_skill_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id:
        return JsonResponse({"status": "error"}, status=HTTPStatus.FORBIDDEN)

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"status": "error"}, status=HTTPStatus.BAD_REQUEST)
    skill_id = payload.get("skill_id")
    name = (payload.get("name") or "").strip()

    skill = None
    created = False
    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    elif name:
        skill, created = Skill.objects.get_or_create(name=name)
    else:
        return JsonResponse({"status": "error"}, status=HTTPStatus.BAD_REQUEST)

    added = not project.skills.filter(pk=skill.pk).exists()
    if added:
        project.skills.add(skill)

    return JsonResponse(
        {
            "skill_id": skill.id,
            "id": skill.id,
            "name": skill.name,
            "created": created,
            "added": added,
        }
    )


@login_required
@require_POST
def remove_project_skill_view(request, project_id, skill_id):
    project = get_object_or_404(Project, pk=project_id)
    skill = get_object_or_404(Skill, pk=skill_id)
    if project.owner_id != request.user.id:
        return JsonResponse({"status": "error"}, status=HTTPStatus.FORBIDDEN)
    if not project.skills.filter(pk=skill.pk).exists():
        return JsonResponse({"status": "error"}, status=HTTPStatus.BAD_REQUEST)

    project.skills.remove(skill)
    return JsonResponse({"status": "ok"})
