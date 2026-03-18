from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login
from cooked.models import UserProfile, Recipe, Review, Country, Ingredient
from django.shortcuts import redirect, render

# Becca forms

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('cooked:user_profile')
        else:
            form = AuthenticationForm()
            return render(request, 'cooked/login.html', {'form': form})

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'city', 'profile_picture', 'header_photo']

# Yanyan and Tuoyu forms

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
