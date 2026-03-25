from django import forms
from .models import Job


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'category', 'industry', 'job_type', 'work_location_type',
            'description', 'location', 'skills_required', 'experience_required',
            'salary_min', 'salary_max', 'salary_display',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'industry': forms.Select(attrs={'class': 'form-select'}),
            'job_type': forms.Select(attrs={'class': 'form-select'}),
            'work_location_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
            'location': forms.TextInput(attrs={'class': 'form-input'}),
            'skills_required': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'experience_required': forms.NumberInput(attrs={'class': 'form-input'}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Min salary'}),
            'salary_max': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Max salary'}),
            'salary_display': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., $50k-$70k'}),
        }
