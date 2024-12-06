from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import StoryComment
from .models import Profile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    birthdate = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    phone_number = forms.CharField(max_length=15, required=True)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "birthdate",
            "phone_number",
            "profile_picture",
            "password1",
            "password2",
        ]
        widgets = {
            "phone_number": forms.TextInput(
                attrs={
                    "placeholder": "0000-000-0000",  # Add your desired placeholder
                    "class": "form-input block w-full",  # Optional: Add custom classes for styling
                }
            ),
        }

class StoryCommentForm(forms.ModelForm):
    class Meta:
        model = StoryComment
        fields = ['content']

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email"]

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["profile_picture", "birthdate", "phone_number"]
        widgets = {
            'birthdate': forms.DateInput(attrs={'type': 'date'})
        }

class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email"]
