from __future__ import annotations

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from social.models import Profile


User = get_user_model()


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "input", "placeholder": "Email address", "autocomplete": "email"}),
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "Username", "autocomplete": "username"}),
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "input", "placeholder": "Password", "autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "input", "placeholder": "Confirm password", "autocomplete": "new-password"}
        ),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "username", "password1", "password2")

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        email = (self.cleaned_data.get("email") or "").strip()
        if hasattr(user, "email"):
            user.email = email
        if commit:
            user.save()
        return user


class ProfileEditForm(forms.Form):
    display_name = forms.CharField(max_length=80, required=False)
    username = forms.CharField(max_length=150, required=True)
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 5}))

    def __init__(self, *, user, profile: Profile, data=None):
        super().__init__(data=data)
        self.user = user
        self.profile = profile
        if data is None:
            self.initial = {
                "display_name": profile.display_name,
                "username": user.username,
                "bio": profile.bio,
            }

    def clean_username(self) -> str:
        username = (self.cleaned_data.get("username") or "").strip()
        if not username:
            raise forms.ValidationError("Username is required.")
        exists = User.objects.filter(username__iexact=username).exclude(pk=self.user.pk).exists()
        if exists:
            raise forms.ValidationError("That username is already taken.")
        return username

