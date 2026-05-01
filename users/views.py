from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from team_finder.constants import ITEMS_PER_PAGE
from team_finder.services import paginate_queryset
from users.forms import LoginForm, ProfileEditForm, RegisterForm, UserPasswordChangeForm
from users.models import User


def register_view(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect(reverse("users:login"))
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    form = LoginForm(request, request.POST or None)
    if form.is_valid():
        login(request, form.user)
        return redirect(reverse("projects:list"))
    return render(request, "users/login.html", {"form": form})


def user_detail_view(request, user_id):
    profile_user = get_object_or_404(User.objects.prefetch_related("owned_projects"), pk=user_id)
    return render(request, "users/user-details.html", {"user": profile_user})


@login_required
def edit_profile_view(request):
    form = ProfileEditForm(request.POST or None, request.FILES or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect(reverse("users:details", kwargs={"user_id": request.user.id}))
    return render(request, "users/edit_profile.html", {"form": form, "user": request.user})


@login_required
def change_password_view(request):
    form = UserPasswordChangeForm(request.user, request.POST or None)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect(reverse("users:details", kwargs={"user_id": request.user.id}))
    return render(request, "users/change_password.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect(reverse("projects:list"))


def users_list_view(request):
    participants = User.objects.all().order_by("-created_at")

    page_obj = paginate_queryset(participants, ITEMS_PER_PAGE, request.GET.get("page"))

    return render(
        request,
        "users/participants.html",
        {
            "participants": page_obj.object_list,
            "page_obj": page_obj,
        },
    )
