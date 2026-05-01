from io import BytesIO
import random

from django import forms
from PIL import Image, ImageDraw, ImageFont

from team_finder.constants import (
    AVATAR_BACKGROUND_COLORS,
    AVATAR_IMAGE_SIZE,
    AVATAR_TEXT_ANCHOR,
    AVATAR_TEXT_COLOR,
    AVATAR_TEXT_Y_OFFSET,
    DEFAULT_AVATAR_LETTER,
)


def normalize_phone(phone: str) -> str:
    value = phone.strip()
    if value.startswith("8") and len(value) == 11 and value[1:].isdigit():
        return f"+7{value[1:]}"
    if value.startswith("+7") and len(value) == 12 and value[2:].isdigit():
        return value
    raise forms.ValidationError("Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX")


def generate_avatar_bytes(letter: str) -> bytes:
    image = Image.new("RGB", AVATAR_IMAGE_SIZE, color=random.choice(AVATAR_BACKGROUND_COLORS))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    text = (letter or DEFAULT_AVATAR_LETTER).upper()[0]
    text_bbox = draw.textbbox(AVATAR_TEXT_ANCHOR, text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (AVATAR_IMAGE_SIZE[0] - text_width) / 2
    y = (AVATAR_IMAGE_SIZE[1] - text_height) / 2 + AVATAR_TEXT_Y_OFFSET
    draw.text((x, y), text, font=font, fill=AVATAR_TEXT_COLOR)

    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()
