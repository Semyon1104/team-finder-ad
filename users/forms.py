from urllib.parse import urlparse

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm

from users.models import User


def _normalize_phone(phone: str) -> str:
    value = phone.strip()
    if value.startswith("8") and len(value) == 11 and value[1:].isdigit():
        return f"+7{value[1:]}"
    if value.startswith("+7") and len(value) == 12 and value[2:].isdigit():
        return value
    raise forms.ValidationError("Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX")


def _validate_github_url(value: str) -> str:
    if not value:
        return value
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or "github.com" not in parsed.netloc.lower():
        raise forms.ValidationError("Ссылка должна вести на github.com")
    return value


class RegisterForm(forms.ModelForm):
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("name", "surname", "email", "password")
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "email": "Email",
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user = None

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if email and password:
            self.user = authenticate(self.request, email=email, password=password)
            if self.user is None:
                raise forms.ValidationError("Неверный email или пароль")
        return cleaned_data


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("name", "surname", "avatar", "about", "phone", "github_url")
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "avatar": "Аватар",
            "about": "О себе",
            "phone": "Телефон",
            "github_url": "GitHub",
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")
        if not phone:
            return ""
        normalized = _normalize_phone(phone)
        qs = User.objects.filter(phone=normalized)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Такой номер телефона уже используется")
        return normalized

    def clean_github_url(self):
        return _validate_github_url(self.cleaned_data.get("github_url", ""))


class UserPasswordChangeForm(PasswordChangeForm):
    pass
