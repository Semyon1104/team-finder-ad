from urllib.parse import urlparse

from django.core.exceptions import ValidationError

from team_finder.constants import REPOSITORY_HOST, VALID_REPOSITORY_SCHEMES


def validate_repository_url(value: str) -> str:
    if not value:
        return value

    parsed = urlparse(value)
    if (
        parsed.scheme not in VALID_REPOSITORY_SCHEMES
        or REPOSITORY_HOST not in parsed.netloc.lower()
    ):
        raise ValidationError(f"Ссылка должна вести на {REPOSITORY_HOST}")
    return value
