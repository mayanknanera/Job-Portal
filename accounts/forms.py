from django import forms
from .models import User, JobSeekerProfile, EmployerProfile

class UserCreationForm(forms.ModelForm):
    company_name = forms.CharField(
        required=False,
        label="Company Name",
        widget=forms.TextInput(attrs={'placeholder': 'Your Company Ltd.'})
    )

    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'})
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'})
    )

    class Meta:
        model = User
        fields = ('email', 'role', 'company_name', 'password1', 'password2')

    # 🔐 FILTER ROLES (HIDE ADMIN)
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

    # 🛡️ EXTRA SECURITY: BLOCK ADMIN EVEN IF FORGED
    def clean_role(self):
        role = self.cleaned_data.get('role')
        if role == 'ADMIN':
            raise forms.ValidationError("Invalid role selection.")
        return role

    def clean_password2(self):
        pw1 = self.cleaned_data.get("password1")
        pw2 = self.cleaned_data.get("password2")
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError("Passwords do not match. Please try again.")
        return pw2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

            # 🧩 Update employer profile if needed
            if user.role == 'EMPLOYER':
                profile = getattr(user, 'employerprofile', None)
                if profile:
                    profile.company_name = self.cleaned_data.get('company_name')
                    profile.save()

        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'email@example.com'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'})
    )


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

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
            'skills': 'Separate skills with commas (e.g. Python, UI Design, Marketing)',
            'resume': 'Upload a PDF version of your latest CV.',
        }
        widgets = {
            'skills': forms.TextInput(attrs={'placeholder': 'Python, JavaScript, React...'}),
        }

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            if not resume.name.lower().endswith('.pdf'):
                raise forms.ValidationError("Please upload your resume in PDF format.")
            if resume.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("Resume file size cannot exceed 5MB.")
        return resume

    def clean_experience(self):
        experience = self.cleaned_data.get('experience')
        if experience:
            if not experience.isdigit():
                raise forms.ValidationError("Experience must be a positive whole number.")
            if int(experience) < 0:
                raise forms.ValidationError("Experience cannot be negative.")
        return experience

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove any common separators if present (though we'll encourage 10 digits)
            phone = ''.join(filter(str.isdigit, phone))
            if len(phone) != 10:
                raise forms.ValidationError("Phone number must be exactly 10 digits.")
        return phone

    def clean_full_name(self):
        name = self.cleaned_data.get('full_name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise forms.ValidationError("Full name must be at least 2 characters long.")
        return name


class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        fields = ['company_name', 'company_description', 'website', 'location', 'company_logo']
        widgets = {
            'company_description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_company_name(self):
        name = self.cleaned_data.get('company_name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise forms.ValidationError("Company name must be at least 2 characters long.")
        return name

    def clean_location(self):
        location = self.cleaned_data.get('location')
        if location:
            location = location.strip()
            if len(location) < 2:
                raise forms.ValidationError("Location must be at least 2 characters long.")
        return location
