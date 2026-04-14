from django.test import Client, TestCase

from projects.models import Project
from users.models import User


class ProjectsViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="owner@example.com",
            name="Owner",
            surname="User",
            password="StrongPass123!",
        )

    def test_project_list_pagination_by_12(self):
        for idx in range(13):
            Project.objects.create(name=f"Project {idx}", owner=self.user)
        response = self.client.get("/projects/list/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["projects"]), 12)

    def test_create_project_adds_owner_to_participants(self):
        self.client.force_login(self.user)
        response = self.client.post(
            "/projects/create-project/",
            data={
                "name": "New Project",
                "description": "Desc",
                "github_url": "https://github.com/example/repo",
                "status": "open",
            },
        )
        self.assertEqual(response.status_code, 302)
        project = Project.objects.get(name="New Project")
        self.assertEqual(project.owner, self.user)
        self.assertTrue(project.participants.filter(pk=self.user.pk).exists())

    def test_toggle_favorite_requires_auth(self):
        project = Project.objects.create(name="P1", owner=self.user)
        response = self.client.post(f"/projects/{project.id}/toggle-favorite/")
        self.assertEqual(response.status_code, 302)

    def test_toggle_favorite_works_for_logged_in_user(self):
        project = Project.objects.create(name="P2", owner=self.user)
        self.client.force_login(self.user)
        response = self.client.post(f"/projects/{project.id}/toggle-favorite/")
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.favorites.filter(pk=project.pk).exists())

    def test_favorites_page_available_only_for_owner(self):
        response = self.client.get("/projects/favorites/")
        self.assertEqual(response.status_code, 302)
        self.client.force_login(self.user)
        response = self.client.get("/projects/favorites/")
        self.assertEqual(response.status_code, 200)
