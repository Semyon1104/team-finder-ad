from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0003_user_is_superuser"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="favorites",
        ),
    ]
