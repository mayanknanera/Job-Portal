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


# ─── Authentication Views ─────────────────────────────────────────────────────

def signup_view(request):
    """Show the signup form and create a new user account on submission."""
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        # Log the user in immediately after signup
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        # Send to role selection (Job Seeker or Employer)
        return redirect('check_role')

    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    """Show the login form and authenticate the user on submission."""
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
        # Show error if credentials don't match
        messages.error(request, "Invalid credentials")

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Log the user out and redirect to the login page."""
    logout(request)
    return redirect('login')


# ─── Dashboards ───────────────────────────────────────────────────────────────

@login_required
def jobseeker_dashboard(request):
    """
    Show the job seeker's personal dashboard.
    Includes application stats, saved jobs, profile score, and chart data.
    """
    # Import here to avoid circular imports between apps
    from jobs.models import JobApplication, SavedJob

    profile = getattr(request.user, 'jobseekerprofile', None)
    if not profile:
        return redirect('select_role')

    # Convert comma-separated skills string into a list for the template
    skills_list = [s.strip() for s in profile.skills.split(',')] if profile.skills else []

    # All applications by this user, with related job and employer data
    app_qs = JobApplication.objects.filter(applicant=profile).select_related('job', 'job__employer')

    # Count applications grouped by status in a single DB query
    app_stats = app_qs.aggregate(
        total=Count('id'),
        pending=Count('id', filter=Q(status='PENDING')),
        accepted=Count('id', filter=Q(status='ACCEPTED')),
        rejected=Count('id', filter=Q(status='REJECTED')),
    )

    saved_qs = SavedJob.objects.filter(job_seeker=profile)

    # ── Profile completion score (out of 100) ──
    # Each section is worth 25 points
    score = 25                                          # base: account created
    if profile.resume:                  score += 25    # resume uploaded
    if profile.phone:                   score += 25    # phone number added
    if profile.skills and profile.experience: score += 25  # skills & experience filled

    # ── Monthly application chart data (last 6 months) ──
    monthly_labels = []  # e.g. ['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May']
    monthly_data   = []  # count of applications per month
    for i in range(5, -1, -1):
        # Go back i*30 days from today to get each month
        month_date = timezone.now() - timedelta(days=30 * i)
        monthly_labels.append(month_date.strftime('%b'))
        monthly_data.append(
            app_qs.filter(
                applied_at__year=month_date.year,
                applied_at__month=month_date.month,
            ).count()
        )

    # ── Job type breakdown chart data ──
    # Groups applications by job type (Full Time, Part Time, etc.)
    job_type_qs     = app_qs.values('job__job_type').annotate(count=Count('id')).order_by('-count')
    job_type_labels = [
        jt['job__job_type'].replace('_', ' ').title() if jt['job__job_type'] else 'Other'
        for jt in job_type_qs
    ]
    job_type_data = [jt['count'] for jt in job_type_qs]

    total    = app_stats['total'] or 0
    accepted = app_stats['accepted'] or 0

    context = {
        'profile':             profile,
        'skills_list':         skills_list,
        'app_stats':           app_stats,
        'recent_applications': app_qs.order_by('-id')[:5],
        'saved_jobs_count':    saved_qs.count(),
        'saved_jobs':          saved_qs.select_related('job', 'job__employer').order_by('-id')[:5],
        'profile_score':       score,
        'total_apps':          total,
        # Success rate = accepted / total * 100, or 0 if no applications yet
        'success_rate':        round((accepted / total * 100), 1) if total else 0,
        # Chart data must be JSON strings for use in JavaScript
        'monthly_labels':      json.dumps(monthly_labels),
        'monthly_data':        json.dumps(monthly_data),
        'status_data':         json.dumps([app_stats['pending'] or 0, accepted, app_stats['rejected'] or 0]),
        'job_type_labels':     json.dumps(job_type_labels),
        'job_type_data':       json.dumps(job_type_data),
        # Top 5 companies the user has applied to
        'top_companies': list(
            app_qs.values('job__employer__company_name')
                  .annotate(count=Count('id'))
                  .order_by('-count')[:5]
        ),
    }
    return render(request, 'accounts/jobseeker_dashboard.html', context)


@login_required
def employer_dashboard(request):
    """
    Show the employer's dashboard.
    Includes job stats, applicant counts, and chart data.
    """
    from jobs.models import Job, JobApplication

    profile = getattr(request.user, 'employerprofile', None)
    if not profile:
        return redirect('select_role')

    # All jobs posted by this employer, with applicant count per job
    jobs = (
        Job.objects
        .filter(employer=profile)
        .annotate(app_count=Count('applications'))
        .order_by('-created_at')
    )

    # All applications received across all of this employer's jobs
    applications = (
        JobApplication.objects
        .filter(job__employer=profile)
        .select_related('job', 'applicant')
        .order_by('-applied_at')
    )

    # Application status counts
    total_applicants   = applications.count()
    accepted_apps      = applications.filter(status='ACCEPTED').count()
    rejected_apps      = applications.filter(status='REJECTED').count()
    pending_applicants = applications.filter(status='PENDING').count()

    # ── Monthly application chart data (last 6 months) ──
    monthly_labels = []
    monthly_data   = []
    for i in range(5, -1, -1):
        month_date = timezone.now() - timedelta(days=30 * i)
        monthly_labels.append(month_date.strftime('%b'))
        monthly_data.append(
            applications.filter(
                applied_at__year=month_date.year,
                applied_at__month=month_date.month,
            ).count()
        )

    # Top 5 jobs by number of applicants (for bar chart)
    top_jobs = jobs.order_by('-app_count')[:5]

    # Job type breakdown (Full Time, Part Time, etc.)
    job_type_qs = jobs.values('job_type').annotate(count=Count('id')).order_by('-count')

    context = {
        'profile':            profile,
        'active_jobs_count':  jobs.filter(is_active=True).count(),
        'total_jobs':         jobs.count(),
        'total_applicants':   total_applicants,
        'recent_jobs':        jobs[:3],
        'recent_applications': applications[:5],
        'pending_applicants': pending_applicants,
        'accepted_apps':      accepted_apps,
        'rejected_apps':      rejected_apps,
        # Acceptance rate = accepted / total * 100, or 0 if no applicants yet
        'acceptance_rate': round((accepted_apps / total_applicants * 100), 1) if total_applicants else 0,
        # Chart data as JSON strings
        'monthly_labels':  json.dumps(monthly_labels),
        'monthly_data':    json.dumps(monthly_data),
        'status_data':     json.dumps([pending_applicants, accepted_apps, rejected_apps]),
        # Truncate job titles to 20 chars so they fit on the chart axis
        'top_jobs_labels': json.dumps([j.title[:20] for j in top_jobs]),
        'top_jobs_data':   json.dumps([j.app_count for j in top_jobs]),
        'job_type_labels': json.dumps([
            jt['job_type'].replace('_', ' ').title() if jt['job_type'] else 'Other'
            for jt in job_type_qs
        ]),
        'job_type_data': json.dumps([jt['count'] for jt in job_type_qs]),
    }
    return render(request, 'accounts/employer_dashboard.html', context)


# ─── Profile ──────────────────────────────────────────────────────────────────

@login_required
def edit_profile(request):
    """
    Let the logged-in user edit their profile.
    Job seekers edit personal info; employers edit company info.
    """
    user = request.user

    # Pick the right profile object and form based on the user's role
    if user.role == 'JOB_SEEKER':
        profile     = getattr(user, 'jobseekerprofile', None)
        ProfileForm = JobSeekerProfileForm
    elif user.role == 'EMPLOYER':
        profile     = getattr(user, 'employerprofile', None)
        ProfileForm = EmployerProfileForm
    else:
        messages.error(request, "Invalid user role.")
        return redirect('home')

    if not profile:
        messages.error(request, "Please complete your profile setup first.")
        return redirect('select_role')

    if request.method == 'POST':
        user_form    = UserEditForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():  # save both forms together or not at all
                user_form.save()

                # Handle image/file clear requests (user clicked "Remove")
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

            # Redirect to the appropriate dashboard after saving
            return redirect('jobseeker_dashboard' if user.role == 'JOB_SEEKER' else 'employer_dashboard')
    else:
        # Pre-fill forms with existing data on GET request
        user_form    = UserEditForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    return render(request, 'accounts/edit_profile.html', {
        'user_form':    user_form,
        'profile_form': profile_form,
        'profile':      profile,
    })


# ─── Role Selection ───────────────────────────────────────────────────────────

@login_required
def select_role(request):
    """
    Let a new user choose whether they are a Job Seeker or Employer.
    Creates the appropriate profile and removes the other if it exists.
    Only shown once — skipped if role is already confirmed.
    """
    user = request.user

    # If the user already picked a role, skip this page
    if user.is_role_confirmed:
        return redirect('home')

    if request.method == 'POST':
        role = request.POST.get('role')

        if role in ['JOB_SEEKER', 'EMPLOYER']:
            user.role             = role
            user.is_role_confirmed = True
            user.save()

            if role == 'JOB_SEEKER':
                # Create a job seeker profile (use email as placeholder name)
                JobSeekerProfile.objects.get_or_create(user=user, defaults={'full_name': user.email})
                # Remove employer profile if it somehow exists
                if hasattr(user, 'employerprofile'):
                    user.employerprofile.delete()
            else:
                # Create an employer profile with a default company name
                EmployerProfile.objects.get_or_create(user=user, defaults={'company_name': 'My Company'})
                # Remove job seeker profile if it somehow exists
                if hasattr(user, 'jobseekerprofile'):
                    user.jobseekerprofile.delete()

            return redirect('home')

    return render(request, 'accounts/select_role.html')


@login_required
def check_role(request):
    """
    Redirect the user to the correct page based on their role.
    - Not confirmed yet → role selection page
    - Job Seeker → job seeker dashboard
    - Employer → employer dashboard
    """
    user = request.user

    if not user.is_role_confirmed:
        return redirect('select_role')
    if user.role == 'JOB_SEEKER':
        return redirect('jobseeker_dashboard')
    elif user.role == 'EMPLOYER':
        return redirect('employer_dashboard')

    return redirect('home')


def analytics_dashboard(request):
    """Redirect to the appropriate dashboard, or login if not authenticated."""
    if request.user.is_authenticated:
        if request.user.role == 'EMPLOYER':
            return redirect('employer_dashboard')
        return redirect('jobseeker_dashboard')
    return redirect('login')
