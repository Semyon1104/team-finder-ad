from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_user_favorites"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="is_superuser",
            field=models.BooleanField(default=False),
        ),
    ]
