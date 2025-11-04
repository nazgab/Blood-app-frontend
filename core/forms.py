# core/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Profile
from .legacy_models import LegacyUser

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "first_name", "last_name", "blood_group", "iin",
            "age", "weight", "city", "address", "phone",
        ]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 2}),
        }

class SignupForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            "class": "auth2-input",
            "placeholder": "you@example.com",
            "autocapitalize": "none",
            "autocomplete": "email",
        }),
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "auth2-input"}),
        validators=[validate_password],
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={"class": "auth2-input"}),
    )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже зарегистрирован.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Пароли не совпадают.")
        return cleaned
