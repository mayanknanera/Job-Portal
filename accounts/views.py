from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserCreationForm, UserLoginForm, UserEditForm, JobSeekerProfileForm, EmployerProfileForm
from django.contrib import messages
from django.db import transaction

def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            if user.role == 'JOB_SEEKER':
                return redirect('jobseeker_dashboard')
            return redirect('employer_dashboard')

    else:
        form = UserCreationForm()

    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                if user.role == 'JOB_SEEKER':
                    return redirect('jobseeker_dashboard')
                else:
                    return redirect('employer_dashboard')
            else:
                messages.error(request, "Invalid credentials")
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def jobseeker_dashboard(request):
    profile = request.user.jobseekerprofile
    user = request.user

    # ✅ split skills by comma AND trim spaces
    skills_list = []
    if profile.skills:
        skills_list = [skill.strip() for skill in profile.skills.split(',')]

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = JobSeekerProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user_form.save()
                profile_form.save()

            messages.success(request, "Profile updated successfully.")
            return redirect('jobseeker_dashboard')

    else:
        user_form = UserEditForm(instance=user)
        profile_form = JobSeekerProfileForm(instance=profile)

    context = {
        'profile': profile,
        'user_form': user_form,
        'profile_form': profile_form,
        'skills_list': skills_list,
    }

    return render(request, 'accounts/jobseeker_dashboard.html', context)

@login_required
def employer_dashboard(request):
    profile = request.user.employerprofile
    user = request.user

    # Handle profile editing
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = EmployerProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user_form.save()
                profile_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('employer_dashboard')
    else:
        user_form = UserEditForm(instance=user)
        profile_form = EmployerProfileForm(instance=profile)

    context = {
        'profile': profile,
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/employer_dashboard.html', context)

@login_required
def edit_profile(request):
    user = request.user

    # Select profile + form based on role
    if user.role == 'JOB_SEEKER':
        profile = user.jobseekerprofile
        ProfileForm = JobSeekerProfileForm
    elif user.role == 'EMPLOYER':
        profile = user.employerprofile
        ProfileForm = EmployerProfileForm
    else:
        messages.error(request, "Invalid user role.")
        return redirect('dashboard')

    if request.method == 'POST':
        user_form = UserEditForm(
            request.POST,
            instance=user
        )
        profile_form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user_form.save()
                
                # Handle image deletion manually if clear checkbox is checked
                if user.role == 'JOB_SEEKER':
                    if request.POST.get('profile_image-clear'):
                        profile.profile_image.delete(save=False)
                        profile.profile_image = None
                elif user.role == 'EMPLOYER':
                    if request.POST.get('company_logo-clear'):
                        profile.company_logo.delete(save=False)
                        profile.company_logo = None
                
                profile_form.save()

            messages.success(request, "Profile updated successfully.")
            if user.role == 'JOB_SEEKER':
                return redirect('jobseeker_dashboard')
            else:
                return redirect('employer_dashboard')

    else:
        user_form = UserEditForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
    }
    return render(request, 'accounts/edit_profile.html', context)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import User, JobSeekerProfile, EmployerProfile

@login_required
def select_role(request):
    user = request.user

    # If the user has already confirmed their role, redirect to home/dashboard
    if user.is_role_confirmed:
        return redirect('home')

    if request.method == 'POST':
        role = request.POST.get('role')
        if role in ['JOB_SEEKER', 'EMPLOYER']:
            # Update user's role and mark as confirmed
            user.role = role
            user.is_role_confirmed = True
            user.save()

            # Handle profile creation & cleanup
            if role == 'JOB_SEEKER':
                # Ensure JobSeekerProfile exists
                JobSeekerProfile.objects.get_or_create(
                    user=user,
                    defaults={'full_name': user.email}  # Adjust as needed
                )
                # Delete EmployerProfile if exists
                if hasattr(user, 'employerprofile'):
                    user.employerprofile.delete()

            elif role == 'EMPLOYER':
                # Ensure EmployerProfile exists
                EmployerProfile.objects.get_or_create(
                    user=user,
                    defaults={'company_name': 'My Company'}  # Adjust as needed
                )
                # Delete JobSeekerProfile if exists
                if hasattr(user, 'jobseekerprofile'):
                    user.jobseekerprofile.delete()

            # Redirect to dashboard/home after selection
            return redirect('home')

    # Render role selection page
    return render(request, 'accounts/select_role.html')

@login_required
def check_role(request):
    user = request.user
    
    if not user.is_role_confirmed:
        return redirect('select_role')

    if user.role == 'JOB_SEEKER':
        return redirect('jobseeker_dashboard')
    elif user.role == 'EMPLOYER':
        return redirect('employer_dashboard')
    else:
        return redirect('home')  