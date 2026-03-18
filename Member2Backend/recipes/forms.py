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
        fields = [
            "title",
            "origin_country",
            "cuisine",
            "difficulty",
            "occasion",
            "description",
            "prep_time_minutes",
            "cooking_time_minutes",
            "serving_size",
            "instructions",
            "ingredients",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "input", "placeholder": "e.g. Tomato Braised Beef Pasta"}),
            "cuisine": forms.TextInput(attrs={"class": "input", "placeholder": "e.g. Italian"}),
            "difficulty": forms.NumberInput(attrs={"class": "input", "min": 1, "max": 5}),
            "occasion": forms.TextInput(attrs={"class": "input", "placeholder": "e.g. Weeknight dinner"}),
            "description": forms.Textarea(attrs={"class": "input input--textarea", "rows": 3}),
            "prep_time_minutes": forms.NumberInput(attrs={"class": "input", "min": 0}),
            "cooking_time_minutes": forms.NumberInput(attrs={"class": "input", "min": 0}),
            "serving_size": forms.TextInput(attrs={"class": "input", "placeholder": "e.g. 2 servings"}),
            "instructions": forms.Textarea(attrs={"class": "input input--textarea", "rows": 10}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["photo"].widget.attrs.update({"class": "input", "accept": "image/*"})


class ReviewForm(forms.ModelForm):
    mark_cooked = forms.BooleanField(required=False)

    class Meta:
        model = Review
        fields = ["rating", "comment", "pinned"]
        widgets = {
            "rating": forms.Select(
                choices=[(i, f"{i} / 5") for i in range(5, 0, -1)],
                attrs={"class": "input"},
            ),
            "comment": forms.Textarea(attrs={"class": "input input--textarea", "rows": 4}),
            "pinned": forms.CheckboxInput(),
        }
