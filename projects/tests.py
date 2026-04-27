from django.test import Client, TestCase

from projects.models import Project, Skill
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

    def test_project_list_filters_by_skill_name(self):
        python_skill = Skill.objects.create(name="Python")
        js_skill = Skill.objects.create(name="JavaScript")
        project_with_python = Project.objects.create(name="Backend", owner=self.user)
        project_with_python.skills.add(python_skill)
        project_with_js = Project.objects.create(name="Frontend", owner=self.user)
        project_with_js.skills.add(js_skill)

        response = self.client.get("/projects/list/?skill=Python")
        self.assertEqual(response.status_code, 200)
        self.assertIn(project_with_python, response.context["projects"])
        self.assertNotIn(project_with_js, response.context["projects"])
        self.assertEqual(response.context["active_skill"], "Python")

    def test_skills_suggest_returns_up_to_10_ordered(self):
        Skill.objects.create(name="Python")
        Skill.objects.create(name="Pytest")
        Skill.objects.create(name="Django")
        response = self.client.get("/projects/skills/?q=Py")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual([item["name"] for item in data], ["Pytest", "Python"])

    def test_owner_can_add_and_remove_skill(self):
        self.client.force_login(self.user)
        project = Project.objects.create(name="Skill Project", owner=self.user)
        response = self.client.post(
            f"/projects/{project.id}/skills/add/",
            data='{"name":"Django"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["created"])
        self.assertTrue(payload["added"])
        self.assertTrue(project.skills.filter(pk=payload["skill_id"]).exists())

        response = self.client.post(f"/projects/{project.id}/skills/{payload['skill_id']}/remove/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(project.skills.filter(pk=payload["skill_id"]).exists())
