from __future__ import annotations

from django import forms
from django.contrib.auth import get_user_model

from .models import Profile


class ProfileEditForm(forms.Form):
    display_name = forms.CharField(max_length=80, required=False)
    username = forms.CharField(max_length=150, required=True)
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 5}))
    avatar = forms.FileField(required=False)
    cover = forms.FileField(required=False)

    def __init__(self, *, user, profile: Profile, data=None, files=None):
        super().__init__(data=data, files=files)
        self.user = user
        self.profile = profile

        if data is None and files is None:
            self.initial = {
                "display_name": profile.display_name,
                "username": user.username,
                "bio": profile.bio,
            }

    def clean_username(self) -> str:
        username = (self.cleaned_data.get("username") or "").strip()
        if not username:
            raise forms.ValidationError("Username is required.")
        User = get_user_model()
        exists = User.objects.filter(username__iexact=username).exclude(pk=self.user.pk).exists()
        if exists:
            raise forms.ValidationError("That username is already taken.")
        return username

