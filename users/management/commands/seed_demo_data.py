from django.core.management.base import BaseCommand

from projects.models import Project
from users.models import User


class Command(BaseCommand):
    help = "Create demo users and one project for each user"

    def handle(self, *args, **options):
        demo_users = [
            ("alex@example.com", "Alex", "Ivanov"),
            ("maria@example.com", "Maria", "Petrova"),
            ("oleg@example.com", "Oleg", "Sidorov"),
        ]

        created_count = 0
        for email, name, surname in demo_users:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "name": name,
                    "surname": surname,
                    "phone": "",
                    "about": f"Demo profile for {name}",
                },
            )
            if created:
                user.set_password("DemoPass123!")
                user.save(update_fields=["password"])
                created_count += 1

            project, project_created = Project.objects.get_or_create(
                name=f"{name}'s demo project",
                owner=user,
                defaults={
                    "description": "Demo project created for manual testing",
                    "status": "open",
                },
            )
            if project_created:
                project.participants.add(user)

        self.stdout.write(
            self.style.SUCCESS(
                "Demo data is ready. "
                f"New users: {created_count}. Password for new users: DemoPass123!"
            )
        )
