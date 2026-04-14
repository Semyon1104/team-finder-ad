from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from users.forms import LoginForm, ProfileEditForm, RegisterForm, UserPasswordChangeForm
from users.models import User


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/users/login/")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, request.POST)
        if form.is_valid():
            login(request, form.user)
            return redirect("/projects/list/")
    else:
        form = LoginForm(request)
    return render(request, "users/login.html", {"form": form})


def user_detail_view(request, user_id):
    profile_user = get_object_or_404(User.objects.prefetch_related("owned_projects"), pk=user_id)
    return render(request, "users/user-details.html", {"user": profile_user})


@login_required
def edit_profile_view(request):
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(f"/users/{request.user.id}/")
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, "users/edit_profile.html", {"form": form, "user": request.user})


@login_required
def change_password_view(request):
    if request.method == "POST":
        form = UserPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect(f"/users/{request.user.id}/")
    else:
        form = UserPasswordChangeForm(request.user)
    return render(request, "users/change_password.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("/projects/list/")


def users_list_view(request):
    participants = User.objects.all().order_by("-created_at")
    active_filter = None

    if request.user.is_authenticated:
        active_filter = request.GET.get("filter")
        if active_filter == "owners-of-favorite-projects":
            participants = participants.filter(
                owned_projects__interested_users=request.user
            ).distinct()
        elif active_filter == "owners-of-participating-projects":
            participants = participants.filter(owned_projects__participants=request.user).distinct()
        elif active_filter == "interested-in-my-projects":
            participants = participants.filter(favorites__owner=request.user).distinct()
        elif active_filter == "participants-of-my-projects":
            participants = participants.filter(participated_projects__owner=request.user).exclude(
                pk=request.user.pk
            ).distinct()

    paginator = Paginator(participants, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "users/participants.html",
        {
            "participants": page_obj.object_list,
            "page_obj": page_obj,
            "active_filter": active_filter,
            "active_skill": active_filter,
        },
    )
