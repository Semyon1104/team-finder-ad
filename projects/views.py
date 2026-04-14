from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from projects.forms import ProjectForm
from projects.models import Project


@require_GET
def project_list_view(request):
    projects_qs = (
        Project.objects.select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )
    paginator = Paginator(projects_qs, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "projects/project_list.html",
        {
            "projects": page_obj.object_list,
            "page_obj": page_obj,
        },
    )


@require_GET
def project_detail_view(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"),
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
@require_GET
def favorite_projects_view(request):
    projects = (
        request.user.favorites.select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )
    return render(request, "projects/favorite_projects.html", {"projects": projects})


@login_required
@require_POST
def toggle_favorite_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    is_favorite = request.user.favorites.filter(pk=project.pk).exists()
    if is_favorite:
        request.user.favorites.remove(project)
    else:
        request.user.favorites.add(project)
    return JsonResponse({"status": "ok", "favorited": not is_favorite})


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
