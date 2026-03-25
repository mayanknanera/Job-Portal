import json
from datetime import timedelta

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone

from .forms import UserCreationForm, UserLoginForm, UserEditForm, JobSeekerProfileForm, EmployerProfileForm
from .models import JobSeekerProfile, EmployerProfile


def signup_view(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('check_role')
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    form = UserLoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password'],
        )
        if user:
            login(request, user)
            return redirect('check_role')
        messages.error(request, "Invalid credentials")
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def jobseeker_dashboard(request):
    from jobs.models import JobApplication, SavedJob

    profile = getattr(request.user, 'jobseekerprofile', None)
    if not profile:
        return redirect('select_role')

    skills_list = [s.strip() for s in profile.skills.split(',')] if profile.skills else []

    app_qs = JobApplication.objects.filter(applicant=profile).select_related('job', 'job__employer')
    app_stats = app_qs.aggregate(
        total=Count('id'),
        pending=Count('id', filter=Q(status='PENDING')),
        accepted=Count('id', filter=Q(status='ACCEPTED')),
        rejected=Count('id', filter=Q(status='REJECTED')),
    )

    saved_qs = SavedJob.objects.filter(job_seeker=profile)

    # Profile completion score
    score = 25
    if profile.resume: score += 25
    if profile.phone: score += 25
    if profile.skills and profile.experience: score += 25

    # Monthly applications (last 6 months)
    monthly_labels, monthly_data = [], []
    for i in range(5, -1, -1):
        d = timezone.now() - timedelta(days=30 * i)
        monthly_labels.append(d.strftime('%b'))
        monthly_data.append(app_qs.filter(applied_at__year=d.year, applied_at__month=d.month).count())

    job_type_qs = app_qs.values('job__job_type').annotate(count=Count('id')).order_by('-count')
    job_type_labels = [jt['job__job_type'].replace('_', ' ').title() if jt['job__job_type'] else 'Other' for jt in job_type_qs]
    job_type_data = [jt['count'] for jt in job_type_qs]

    total = app_stats['total'] or 0
    accepted = app_stats['accepted'] or 0

    context = {
        'profile': profile,
        'skills_list': skills_list,
        'app_stats': app_stats,
        'recent_applications': app_qs.order_by('-id')[:5],
        'saved_jobs_count': saved_qs.count(),
        'saved_jobs': saved_qs.select_related('job', 'job__employer').order_by('-id')[:5],
        'profile_score': score,
        'total_apps': total,
        'success_rate': round((accepted / total * 100), 1) if total else 0,
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_data': json.dumps(monthly_data),
        'status_data': json.dumps([app_stats['pending'] or 0, accepted, app_stats['rejected'] or 0]),
        'job_type_labels': json.dumps(job_type_labels),
        'job_type_data': json.dumps(job_type_data),
        'top_companies': list(
            app_qs.values('job__employer__company_name').annotate(count=Count('id')).order_by('-count')[:5]
        ),
    }
    return render(request, 'accounts/jobseeker_dashboard.html', context)


@login_required
def employer_dashboard(request):
    from jobs.models import Job, JobApplication

    profile = getattr(request.user, 'employerprofile', None)
    if not profile:
        return redirect('select_role')

    jobs = Job.objects.filter(employer=profile).annotate(app_count=Count('applications')).order_by('-created_at')
    applications = JobApplication.objects.filter(job__employer=profile).select_related('job', 'applicant').order_by('-applied_at')

    total_applicants = applications.count()
    accepted_apps = applications.filter(status='ACCEPTED').count()
    rejected_apps = applications.filter(status='REJECTED').count()
    pending_applicants = applications.filter(status='PENDING').count()

    # Monthly applications (last 6 months)
    monthly_labels, monthly_data = [], []
    for i in range(5, -1, -1):
        d = timezone.now() - timedelta(days=30 * i)
        monthly_labels.append(d.strftime('%b'))
        monthly_data.append(applications.filter(applied_at__year=d.year, applied_at__month=d.month).count())

    top_jobs = jobs.order_by('-app_count')[:5]
    job_type_qs = jobs.values('job_type').annotate(count=Count('id')).order_by('-count')

    context = {
        'profile': profile,
        'active_jobs_count': jobs.filter(is_active=True).count(),
        'total_jobs': jobs.count(),
        'total_applicants': total_applicants,
        'recent_jobs': jobs[:3],
        'recent_applications': applications[:5],
        'pending_applicants': pending_applicants,
        'accepted_apps': accepted_apps,
        'rejected_apps': rejected_apps,
        'acceptance_rate': round((accepted_apps / total_applicants * 100), 1) if total_applicants else 0,
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_data': json.dumps(monthly_data),
        'status_data': json.dumps([pending_applicants, accepted_apps, rejected_apps]),
        'top_jobs_labels': json.dumps([j.title[:20] for j in top_jobs]),
        'top_jobs_data': json.dumps([j.app_count for j in top_jobs]),
        'job_type_labels': json.dumps([jt['job_type'].replace('_', ' ').title() if jt['job_type'] else 'Other' for jt in job_type_qs]),
        'job_type_data': json.dumps([jt['count'] for jt in job_type_qs]),
    }
    return render(request, 'accounts/employer_dashboard.html', context)


@login_required
def edit_profile(request):
    user = request.user

    if user.role == 'JOB_SEEKER':
        profile = getattr(user, 'jobseekerprofile', None)
        ProfileForm = JobSeekerProfileForm
    elif user.role == 'EMPLOYER':
        profile = getattr(user, 'employerprofile', None)
        ProfileForm = EmployerProfileForm
    else:
        messages.error(request, "Invalid user role.")
        return redirect('home')

    if not profile:
        messages.error(request, "Please complete your profile setup first.")
        return redirect('select_role')

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user_form.save()

                if user.role == 'JOB_SEEKER' and request.POST.get('profile_image-clear'):
                    profile.profile_image.delete(save=False)
                    profile.profile_image = None
                elif user.role == 'EMPLOYER' and request.POST.get('company_logo-clear'):
                    profile.company_logo.delete(save=False)
                    profile.company_logo = None

                if request.POST.get('resume-clear'):
                    profile.resume.delete(save=False)
                    profile.resume = None

                profile_form.save()

            return redirect('jobseeker_dashboard' if user.role == 'JOB_SEEKER' else 'employer_dashboard')
    else:
        user_form = UserEditForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    return render(request, 'accounts/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
    })


@login_required
def select_role(request):
    user = request.user

    if user.is_role_confirmed:
        return redirect('home')

    if request.method == 'POST':
        role = request.POST.get('role')
        if role in ['JOB_SEEKER', 'EMPLOYER']:
            user.role = role
            user.is_role_confirmed = True
            user.save()

            if role == 'JOB_SEEKER':
                JobSeekerProfile.objects.get_or_create(user=user, defaults={'full_name': user.email})
                if hasattr(user, 'employerprofile'):
                    user.employerprofile.delete()
            else:
                EmployerProfile.objects.get_or_create(user=user, defaults={'company_name': 'My Company'})
                if hasattr(user, 'jobseekerprofile'):
                    user.jobseekerprofile.delete()

            return redirect('home')

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
    return redirect('home')


def analytics_dashboard(request):
    if request.user.is_authenticated:
        if request.user.role == 'EMPLOYER':
            return redirect('employer_dashboard')
        return redirect('jobseeker_dashboard')
    return redirect('login')
