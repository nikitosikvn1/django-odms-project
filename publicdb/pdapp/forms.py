from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import DatasetFile, Dataset
from .validators import validate_csv_file

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email address'}))

    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2',)
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Repeat your password'


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(CustomAuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['password'].widget.attrs['placeholder'] = 'Password'
        self.fields['username'].widget.attrs['autofocus'] = True


class DatasetFileUploadForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea)
    file_csv = forms.FileField(widget=forms.FileInput, validators=[validate_csv_file])
    dataset = forms.ModelChoiceField(queryset=Dataset.objects.all())

    class Meta:
        model = DatasetFile
        fields = ('name', 'description', 'file_csv', 'dataset', 'provider',)
    
    def __init__(self, *args, **kwargs):
        super(DatasetFileUploadForm, self).__init__(*args, **kwargs)

        for key, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        self.fields['name'].widget.attrs['autofocus'] = True
        self.fields['name'].widget.attrs['placeholder'] = 'Dataset file name'
        self.fields['description'].widget.attrs['placeholder'] = 'Description'
        self.fields['provider'].widget.attrs['placeholder'] = 'Provider'
    
