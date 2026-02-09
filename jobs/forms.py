from django import forms
from .models import Job, Message, MessageThread
from accounts.models import User

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'category', 'industry', 'job_type', 'work_location_type', 
                 'description', 'location', 'skills_required', 'experience_required', 
                 'salary_min', 'salary_max', 'salary_display']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'industry': forms.Select(attrs={'class': 'form-control'}),
            'job_type': forms.Select(attrs={'class': 'form-control'}),
            'work_location_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'skills_required': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'experience_required': forms.NumberInput(attrs={'class': 'form-control'}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min salary'}),
            'salary_max': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max salary'}),
            'salary_display': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., $50k-$70k'}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'content']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter message subject'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Type your message here...'
            })
        }

class NewMessageForm(forms.ModelForm):
    recipient = forms.ModelChoiceField(
        queryset=None,
        empty_label="Select recipient",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'content']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter message subject'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Type your message here...'
            })
        }
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter recipients based on user role
        if user.role == 'EMPLOYER':
            # Employers can message job seekers who applied to their jobs
            from .models import JobApplication
            applied_seekers = JobApplication.objects.filter(
                job__employer=user.employerprofile
            ).values_list('applicant__user', flat=True).distinct()
            self.fields['recipient'].queryset = User.objects.filter(
                id__in=applied_seekers
            )
        elif user.role == 'JOB_SEEKER':
            # Job seekers can message employers whose jobs they applied to
            from .models import JobApplication
            applied_employers = JobApplication.objects.filter(
                applicant=user.jobseekerprofile
            ).values_list('job__employer__user', flat=True).distinct()
            self.fields['recipient'].queryset = User.objects.filter(
                id__in=applied_employers
            )
