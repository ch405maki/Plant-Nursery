from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import StoryComment, Profile
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        "class": "form-control",
        "placeholder": "example@gmail.com"
    }))
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Enter your first name"
    }))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Enter your last name"
    }))
    birthdate = forms.DateField(required=True, widget=forms.DateInput(attrs={
        "type": "date",
        "class": "form-control"
    }))
    phone_number = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "0000-000-0000"
    }))
    profile_picture = forms.ImageField(required=False)
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Choose a unique username"
    }))
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        help_text="Password must be at least 8 characters long and include a mix of uppercase letters, lowercase letters, numbers, and symbols.",
        validators=[
            RegexValidator(
                regex=r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
                message="Password must be at least 8 characters long and include a mix of uppercase letters, lowercase letters, numbers, and symbols.",
            ),
        ],
    )

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

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not any(char.isupper() for char in password):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not any(char.islower() for char in password):
            raise ValidationError("Password must contain at least one lowercase letter.")
        if not any(char.isdigit() for char in password):
            raise ValidationError("Password must contain at least one number.")
        if not any(char in "!@#$%^&*()-_+=" for char in password):
            raise ValidationError("Password must contain at least one special character.")
        return password


    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose a unique username.")
        return username


class StoryCommentForm(forms.ModelForm):
    class Meta:
        model = StoryComment
        fields = ['content']


class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Enter your first name"
    }))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Enter your last name"
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        "class": "form-control",
        "placeholder": "example@gmail.com"
    }))
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Choose a unique username"
    }))

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email"]


class ProfileUpdateForm(forms.ModelForm):
    birthdate = forms.DateField(required=True, widget=forms.DateInput(attrs={
        "type": "date",
        "class": "form-control"
    }))
    phone_number = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "0000-000-0000"
    }))
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ["profile_picture", "birthdate", "phone_number"]
    