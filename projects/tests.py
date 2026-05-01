from http import HTTPStatus

from django.urls import reverse
from django.test import Client, TestCase

from projects.models import Project, Skill
from team_finder.constants import ITEMS_PER_PAGE, PROJECT_STATUS_OPEN, SKILLS_SUGGEST_LIMIT
from users.models import User


class ProjectsViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="owner@example.com",
            name="Owner",
            surname="User",
            password="StrongPass123!",
        )
        cls.owner_client = Client()
        cls.owner_client.force_login(cls.user)

    def test_project_list_pagination(self):
        for idx in range(ITEMS_PER_PAGE + 1):
            Project.objects.create(name=f"Project {idx}", owner=self.user)
        response = self.client.get(reverse("projects:list"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.context["projects"]), ITEMS_PER_PAGE)

    def test_create_project_adds_owner_to_participants(self):
        response = self.owner_client.post(
            reverse("projects:create"),
            data={
                "name": "New Project",
                "description": "Desc",
                "github_url": "https://github.com/example/repo",
                "status": PROJECT_STATUS_OPEN,
            },
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
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

        response = self.client.get(reverse("projects:list"), data={"skill": "Python"})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(project_with_python, response.context["projects"])
        self.assertNotIn(project_with_js, response.context["projects"])
        self.assertEqual(response.context["active_skill"], "Python")

    def test_skills_suggest_returns_up_to_10_ordered(self):
        Skill.objects.create(name="Python")
        Skill.objects.create(name="Pytest")
        Skill.objects.create(name="Django")
        response = self.client.get(reverse("projects:skills_suggest"), data={"q": "Py"})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertLessEqual(len(data), SKILLS_SUGGEST_LIMIT)
        self.assertEqual([item["name"] for item in data], ["Pytest", "Python"])

    def test_owner_can_add_and_remove_skill(self):
        project = Project.objects.create(name="Skill Project", owner=self.user)
        response = self.owner_client.post(
            reverse("projects:skills_add", kwargs={"project_id": project.id}),
            data='{"name":"Django"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        payload = response.json()
        self.assertTrue(payload["created"])
        self.assertTrue(payload["added"])
        self.assertTrue(project.skills.filter(pk=payload["skill_id"]).exists())

        response = self.owner_client.post(
            reverse(
                "projects:skills_remove",
                kwargs={"project_id": project.id, "skill_id": payload["skill_id"]},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(project.skills.filter(pk=payload["skill_id"]).exists())
