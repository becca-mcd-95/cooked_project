from __future__ import annotations

from django import forms

from .models import Recipe, Review
from social.models import Country, Ingredient


class RecipeForm(forms.ModelForm):
    photo = forms.FileField(required=False)

    origin_country = forms.ModelChoiceField(
        queryset=Country.objects.all().order_by("name"),
        required=False,
        widget=forms.Select(attrs={"class": "input"}),
    )

    ingredients = forms.ModelMultipleChoiceField(
        queryset=Ingredient.objects.all().order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Recipe
        fields = ["title", "origin_country", "cooking_time_minutes", "instructions", "ingredients"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "input", "placeholder": "e.g. Tomato Braised Beef Pasta"}),
            "cooking_time_minutes": forms.NumberInput(attrs={"class": "input", "min": 0}),
            "instructions": forms.Textarea(attrs={"class": "input input--textarea", "rows": 10}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["photo"].widget.attrs.update({"class": "input", "accept": "image/*"})


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.Select(
                choices=[(i, f"{i} / 5") for i in range(5, 0, -1)],
                attrs={"class": "input"},
            ),
            "comment": forms.Textarea(attrs={"class": "input input--textarea", "rows": 4}),
        }
