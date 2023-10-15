from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import DatasetFile
from .validators import validate_csv_file


class RegistrationForm(UserCreationForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Password',
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Repeat your password',
    }))

    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2',)
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email address',
            }),
            'username': forms.TextInput(attrs={
                'placeholder': 'Username',
            }),
        }


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Username',
        'autofocus': True,
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Password',
    }))

    class Meta:
        model = User
        fields = ('username', 'password',)


class UserUpdateForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password',
    }))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'confirm_password',)
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email',
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name',
            }),
        }


class DatasetFileUploadForm(forms.ModelForm):
    file_csv = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}), validators=[validate_csv_file])

    class Meta:
        model = DatasetFile
        fields = ('name', 'description', 'file_csv', 'dataset', 'provider',)
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Description',
            }),
            'dataset': forms.Select(attrs={
                'class': 'form-control',
            }),
            'provider': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Provider',
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dataset file name',
                'autofocus': True,
            }),
        }
