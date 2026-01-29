from django import forms
from .models import User

class UserCreationForm(forms.ModelForm):
    company_name = forms.CharField(required=False, label="Company Name")
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    

    class Meta:
        model = User
        fields = (
            'email',
            'role',
            'company_name',
            'password1',
            'password2',
        )

    def clean_password2(self):
        pw1 = self.cleaned_data.get("password1")
        pw2 = self.cleaned_data.get("password2")
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError("Passwords don't match")
        return pw2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            if user.role == 'EMPLOYER':
                user.employerprofile.company_name = self.cleaned_data.get('company_name')
                user.employerprofile.save()
        return user

class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
