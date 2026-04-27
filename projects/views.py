from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST
import json

from projects.forms import ProjectForm
from projects.models import Project, Skill


@require_GET
def project_list_view(request):
    projects_qs = Project.objects.select_related("owner").prefetch_related("participants", "skills")
    all_skills = Skill.objects.order_by("name").values_list("name", flat=True)
    active_skill = request.GET.get("skill")
    if active_skill:
        projects_qs = projects_qs.filter(skills__name=active_skill).distinct()

    projects_qs = projects_qs.order_by("-created_at")
    paginator = Paginator(projects_qs, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
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
        Project.objects.select_related("owner").prefetch_related("participants", "skills"),
        pk=project_id,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def project_form_view(request, project_id=None):
    project = None
    is_edit = project_id is not None
    if is_edit:
        project = get_object_or_404(Project, pk=project_id, owner=request.user)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save(commit=False)
            if not is_edit:
                project.owner = request.user
            project.save()
            if not is_edit:
                project.participants.add(request.user)
            return redirect(f"/projects/{project.id}/")
    else:
        form = ProjectForm(instance=project)

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
    if project.owner_id != request.user.id or project.status != "open":
        return JsonResponse({"status": "error"}, status=400)
    project.status = "closed"
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": "closed"})


@require_GET
def skills_suggest_view(request):
    q = request.GET.get("q", "").strip()
    queryset = Skill.objects.all()
    if q:
        queryset = queryset.filter(name__istartswith=q)
    skills = queryset.order_by("name").values("id", "name")[:10]
    return JsonResponse(list(skills), safe=False)


@login_required
@require_POST
def add_project_skill_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id:
        return JsonResponse({"status": "error"}, status=403)

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"status": "error"}, status=400)
    skill_id = payload.get("skill_id")
    name = (payload.get("name") or "").strip()

    skill = None
    created = False
    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    elif name:
        skill, created = Skill.objects.get_or_create(name=name)
    else:
        return JsonResponse({"status": "error"}, status=400)

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
        return JsonResponse({"status": "error"}, status=403)
    if not project.skills.filter(pk=skill.pk).exists():
        return JsonResponse({"status": "error"}, status=400)

    project.skills.remove(skill)
    return JsonResponse({"status": "ok"})
