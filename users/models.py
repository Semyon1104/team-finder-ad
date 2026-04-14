from io import BytesIO
import random

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from django.utils.translation import gettext_lazy as _
from PIL import Image, ImageDraw, ImageFont

from users.managers import UserManager


def _generate_avatar_bytes(letter: str) -> bytes:
    colors = [
        (60, 78, 97),
        (75, 85, 99),
        (91, 33, 182),
        (29, 78, 216),
        (15, 118, 110),
    ]
    image = Image.new("RGB", (240, 240), color=random.choice(colors))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    text = (letter or "U").upper()[0]
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (240 - text_width) / 2
    y = (240 - text_height) / 2 - 8
    draw.text((x, y), text, font=font, fill=(255, 255, 255))

    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"), unique=True)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    phone = models.CharField(max_length=12, blank=True)
    github_url = models.URLField(blank=True)
    about = models.CharField(max_length=256, blank=True)
    favorites = models.ManyToManyField(
        "projects.Project",
        blank=True,
        related_name="interested_users",
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return f"{self.name} {self.surname} ({self.email})"

    def save(self, *args, **kwargs):
        if not self.avatar:
            filename = f"{self.email.split('@')[0]}_avatar.png"
            avatar_bytes = _generate_avatar_bytes(self.name[:1] if self.name else "U")
            self.avatar.save(filename, ContentFile(avatar_bytes), save=False)
        super().save(*args, **kwargs)
