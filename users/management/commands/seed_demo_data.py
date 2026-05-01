import json
import random
from pathlib import Path

from django.core.management.base import BaseCommand

from projects.models import Project, Skill
from team_finder.constants import PROJECT_STATUS_OPEN
from users.models import User


class Command(BaseCommand):
    help = "Create demo users and one project for each user"

    def handle(self, *args, **options):
        data_path = Path(__file__).with_name("seed_demo_data.json")
        with data_path.open(encoding="utf-8") as fp:
            seed_data = json.load(fp)

        skills_pool = seed_data["skills_pool"]
        demo_users = seed_data["demo_users"]

        skill_objs = {}
        for skill_name in skills_pool:
            skill, _ = Skill.objects.get_or_create(name=skill_name)
            skill_objs[skill_name] = skill

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

            project, _ = Project.objects.get_or_create(
                name=f"{name}'s demo project",
                owner=user,
                defaults={
                    "description": "Demo project created for manual testing",
                    "status": PROJECT_STATUS_OPEN,
                },
            )
            if not project.participants.filter(pk=user.pk).exists():
                project.participants.add(user)

            target_count = random.randint(4, 5)
            current_skill_ids = set(project.skills.values_list("id", flat=True))
            if len(current_skill_ids) < 4:
                available_names = [
                    n for n in skills_pool if skill_objs[n].id not in current_skill_ids
                ]
                to_add = min(target_count - len(current_skill_ids), len(available_names))
                selected_names = random.sample(available_names, k=to_add)
                project.skills.add(*[skill_objs[n] for n in selected_names])

        self.stdout.write(
            self.style.SUCCESS(
                "Demo data is ready. "
                f"New users: {created_count}. Password for new users: DemoPass123!"
            )
        )
