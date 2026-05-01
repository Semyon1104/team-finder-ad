from http import HTTPStatus

from django.urls import reverse
from django.test import TestCase

from users.models import User


class AuthViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.login_user = User.objects.create_user(
            email="anna@example.com",
            name="Anna",
            surname="Petrova",
            password="StrongPass123!",
        )

    def test_register_redirects_to_login(self):
        response = self.client.post(
            reverse("users:register"),
            data={
                "name": "Ivan",
                "surname": "Ivanov",
                "email": "ivan@example.com",
                "password": "StrongPass123!",
            },
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse("users:login"))
        self.assertTrue(User.objects.filter(email="ivan@example.com").exists())

    def test_login_by_email(self):
        response = self.client.post(
            reverse("users:login"),
            data={"email": self.login_user.email, "password": "StrongPass123!"},
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse("projects:list"))
