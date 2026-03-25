from django import forms
from .models import User, JobSeekerProfile, EmployerProfile
from jobs.validators import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB


def _clean_min_length(value, min_len, error_message):
    if value:
        value = value.strip()
        if len(value) < min_len:
            raise forms.ValidationError(error_message)
    return value


class UserCreationForm(forms.ModelForm):
    company_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'input-dark'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'input-dark'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'input-dark'}))

    class Meta:
        model = User
        fields = ('email', 'role', 'company_name', 'password1', 'password2')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'input-dark'}),
            'role': forms.Select(attrs={'class': 'input-dark'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [
            ('JOB_SEEKER', 'Job Seeker'),
            ('EMPLOYER', 'Employer'),
        ]

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if role == 'ADMIN':
            raise forms.ValidationError("Invalid role selection.")
        return role

    def clean_password2(self):
        pw1 = self.cleaned_data.get("password1")
        pw2 = self.cleaned_data.get("password2")
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError("Passwords do not match.")
        return pw2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_role_confirmed = True
        if commit:
            user.save()
            if user.role == 'EMPLOYER':
                profile = getattr(user, 'employerprofile', None)
                if profile:
                    profile.company_name = self.cleaned_data.get('company_name')
                    profile.save()
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'input-dark'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input-dark'}))


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']
        widgets = {'email': forms.EmailInput(attrs={'class': 'form-input'})}

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("This email is already registered to another account.")
        return email


class JobSeekerProfileForm(forms.ModelForm):
    class Meta:
        model = JobSeekerProfile
        fields = ['full_name', 'phone', 'skills', 'experience', 'resume', 'profile_image']
        help_texts = {
            'skills': 'Separate skills with commas (e.g. Python, Django, React)',
            'resume': 'Upload your resume (PDF, DOC, or DOCX, max 5MB).',
        }
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'skills': forms.TextInput(attrs={'class': 'form-input'}),
            'experience': forms.TextInput(attrs={'class': 'form-input'}),
        }

    def clean_full_name(self):
        return _clean_min_length(self.cleaned_data.get('full_name'), 2, "Full name must be at least 2 characters.")

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            phone = ''.join(filter(str.isdigit, phone))
            if len(phone) < 10:
                raise forms.ValidationError("Phone number must be at least 10 digits.")
        return phone

    def clean_experience(self):
        experience = self.cleaned_data.get('experience')
        if experience:
            if not experience.isdigit():
                raise forms.ValidationError("Experience must be a positive whole number.")
        return experience

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            ext = resume.name.split(".")[-1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise forms.ValidationError("Only PDF and Word documents are allowed.")
            if resume.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                raise forms.ValidationError("Resume file size cannot exceed 5MB.")
        return resume


class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        fields = ['company_name', 'company_description', 'website', 'location', 'company_logo']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-input'}),
            'company_description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'website': forms.URLInput(attrs={'class': 'form-input'}),
            'location': forms.TextInput(attrs={'class': 'form-input'}),
        }

    def clean_company_name(self):
        return _clean_min_length(self.cleaned_data.get('company_name'), 2, "Company name must be at least 2 characters.")

    def clean_location(self):
        return _clean_min_length(self.cleaned_data.get('location'), 2, "Location must be at least 2 characters.")
