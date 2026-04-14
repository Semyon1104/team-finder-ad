from django.test import Client, TestCase

from users.models import User


class AuthViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_redirects_to_login(self):
        response = self.client.post(
            "/users/register/",
            data={
                "name": "Ivan",
                "surname": "Ivanov",
                "email": "ivan@example.com",
                "password": "StrongPass123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/users/login/")
        self.assertTrue(User.objects.filter(email="ivan@example.com").exists())

    def test_login_by_email(self):
        user = User.objects.create_user(
            email="anna@example.com",
            name="Anna",
            surname="Petrova",
            password="StrongPass123!",
        )
        response = self.client.post(
            "/users/login/",
            data={"email": user.email, "password": "StrongPass123!"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/projects/list/")
