from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    """
    Task Form with EXACTLY four user-facing fields:
    1. Name
    2. Date
    3. Task Title
    4. Description
    """
    class Meta:
        model = Task
        fields = ['name', 'date', 'task_title', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Alex Johnson',
                'maxlength': '100',
                'autocomplete': 'off',
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'task_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Prepare quarterly financial overview',
                'maxlength': '200',
                'autocomplete': 'off',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Provide thorough details and key steps for this task...',
            }),
        }
        labels = {
            'name': 'Name',
            'date': 'Date',
            'task_title': 'Task Title',
            'description': 'Description',
        }
        error_messages = {
            'name': {
                'required': 'Name is required and cannot be blank.',
                'max_length': 'Name cannot exceed 100 characters.',
            },
            'date': {
                'required': 'Date is required.',
                'invalid': 'Please enter a valid date in YYYY-MM-DD format.',
            },
            'task_title': {
                'required': 'Task Title is required and cannot be blank.',
                'max_length': 'Task Title cannot exceed 200 characters.',
            },
            'description': {
                'required': 'Description is required and cannot be blank.',
            },
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError("Name is required and cannot be blank.")
        return name

    def clean_task_title(self):
        title = self.cleaned_data.get('task_title', '').strip()
        if not title:
            raise forms.ValidationError("Task Title is required and cannot be blank.")
        return title

    def clean_description(self):
        desc = self.cleaned_data.get('description', '').strip()
        if not desc:
            raise forms.ValidationError("Description is required and cannot be blank.")
        return desc


from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class UserRegisterForm(UserCreationForm):
    """User registration form with Bootstrap styling and required unique email."""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a unique username'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists. Please log in.")
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if 'password' in name.lower():
                field.widget.attrs['placeholder'] = '••••••••'

class UserLoginForm(AuthenticationForm):
    """User login authentication form with Bootstrap styling."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '••••••••'
        })
