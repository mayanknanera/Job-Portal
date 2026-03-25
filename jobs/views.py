import mimetypes
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.http import JsonResponse, FileResponse, HttpResponseForbidden
from django.utils import timezone

from accounts.decorators import role_required
from .models import Job, JobApplication, JobCategory, Industry, SavedJob
from .forms import JobForm


def _parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def home_view(request):
    latest_jobs = Job.objects.filter(is_active=True).select_related('employer').order_by('-created_at')[:3]
    return render(request, 'home.html', {'latest_jobs': latest_jobs})


@login_required
@role_required('EMPLOYER')
def job_create_view(request):
    form = JobForm(request.POST or None)
    if form.is_valid():
        job = form.save(commit=False)
        job.employer = request.user.employerprofile
        if not job.employer.company_name:
            job.employer.company_name = "Company Name Not Provided"
            job.employer.save()
        job.save()
        return redirect('job_list')
    return render(request, 'jobs/post_job.html', {'form': form})


@login_required
def job_list_view(request):
    jobs = Job.objects.filter(is_active=True).select_related('employer', 'category', 'industry').order_by('-created_at')

    keyword = request.GET.get('keyword')
    location = request.GET.get('location')
    skill = request.GET.get('skill')
    experience = request.GET.get('experience')
    category = request.GET.get('category')
    industry = request.GET.get('industry')
    job_type = request.GET.get('job_type')
    work_location_type = request.GET.get('work_location_type')
    salary_min = request.GET.get('salary_min')
    salary_max = request.GET.get('salary_max')
    date_posted = request.GET.get('date_posted')

    if keyword:
        jobs = jobs.filter(Q(title__icontains=keyword) | Q(description__icontains=keyword))
    if location:
        jobs = jobs.filter(location__icontains=location)
    if skill:
        jobs = jobs.filter(skills_required__icontains=skill)
    if experience:
        val = _parse_int(experience)
        if val is not None:
            jobs = jobs.filter(experience_required__lte=val)
    if category:
        jobs = jobs.filter(category_id=category)
    if industry:
        jobs = jobs.filter(industry_id=industry)
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    if work_location_type:
        jobs = jobs.filter(work_location_type=work_location_type)
    if salary_min:
        val = _parse_int(salary_min)
        if val is not None:
            jobs = jobs.filter(salary_min__gte=val)
    if salary_max:
        val = _parse_int(salary_max)
        if val is not None:
            jobs = jobs.filter(salary_max__lte=val)
    if date_posted:
        now = timezone.now()
        date_filters = {
            'today': {'created_at__date': now.date()},
            'week': {'created_at__gte': now - timedelta(days=7)},
            'month': {'created_at__gte': now - timedelta(days=30)},
            '3months': {'created_at__gte': now - timedelta(days=90)},
        }
        if date_posted in date_filters:
            jobs = jobs.filter(**date_filters[date_posted])

    paginator = Paginator(jobs, 5)
    page_obj = paginator.get_page(request.GET.get('page'))

    applied_job_ids, saved_job_ids = [], []
    if request.user.is_authenticated and request.user.role == 'JOB_SEEKER':
        profile = getattr(request.user, 'jobseekerprofile', None)
        if profile:
            applied_job_ids = list(JobApplication.objects.filter(applicant=profile).values_list('job_id', flat=True))
            saved_job_ids = list(SavedJob.objects.filter(job_seeker=profile).values_list('job_id', flat=True))

    return render(request, 'jobs/job_list.html', {
        'page_obj': page_obj,
        'applied_job_ids': applied_job_ids,
        'saved_job_ids': saved_job_ids,
        'categories': JobCategory.objects.all(),
        'industries': Industry.objects.all(),
        'job_types': Job.JOB_TYPE_CHOICES,
        'work_location_types': Job.WORK_LOCATION_TYPE_CHOICES,
        'date_posted_choices': [
            ('', 'Any Time'), ('today', 'Today'), ('week', 'Last Week'),
            ('month', 'Last Month'), ('3months', 'Last 3 Months'),
        ],
    })


@login_required
@role_required('JOB_SEEKER')
def apply_job_view(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    profile = getattr(request.user, 'jobseekerprofile', None)

    if not profile:
        messages.error(request, "Please complete your profile first.")
        return redirect('edit_profile')

    if JobApplication.objects.filter(job=job, applicant=profile).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect('job_list')

    if request.method == "POST":
        if not profile.resume:
            messages.error(request, "Please upload your resume before applying.")
            return redirect('edit_profile')

        application = JobApplication.objects.create(
            job=job,
            applicant=profile,
            resume=profile.resume,
            cover_letter=request.POST.get('cover_letter'),
        )

        from .email_utils import send_application_confirmation_email, send_new_applicant_notification_email
        try:
            send_application_confirmation_email(application)
            send_new_applicant_notification_email(job, application)
        except Exception as e:
            print(f"Email notification error: {e}")

        messages.success(request, "Application submitted successfully!")
        return redirect('applied_jobs')

    return render(request, 'jobs/apply_job.html', {'job': job, 'profile': profile})


@login_required
@role_required('EMPLOYER')
def view_applicants_view(request, job_id):
    job = get_object_or_404(Job, id=job_id, employer=request.user.employerprofile)
    paginator = Paginator(job.applications.all().order_by('-applied_at'), 5)
    return render(request, 'jobs/view_applicants.html', {
        'job': job,
        'page_obj': paginator.get_page(request.GET.get('page')),
    })


@login_required
@role_required('EMPLOYER')
@require_POST
def update_application_status(request, app_id, status):
    application = get_object_or_404(JobApplication, id=app_id)

    if application.job.employer.user != request.user:
        messages.error(request, "Unauthorized")
        return redirect('employer_dashboard')

    if status in ['ACCEPTED', 'REJECTED']:
        application.status = status
        application.save()

        from .email_utils import send_application_status_update_email
        try:
            send_application_status_update_email(application)
        except Exception as e:
            print(f"Email notification error: {e}")

        messages.success(request, f"Application {status.lower()}.")
    else:
        messages.error(request, "Invalid status.")

    return redirect('view_applicants', job_id=application.job.id)


@login_required
@role_required('JOB_SEEKER')
def applied_jobs_view(request):
    applications = JobApplication.objects.filter(
        applicant=request.user.jobseekerprofile
    ).select_related('job', 'job__employer').order_by('-applied_at')
    return render(request, 'jobs/applied_jobs.html', {'applications': applications})


def job_detail_view(request, slug):
    job = get_object_or_404(Job.objects.select_related('employer'), slug=slug)

    applied = False
    applied_job_ids = []
    if request.user.is_authenticated and request.user.role == 'JOB_SEEKER':
        profile = request.user.jobseekerprofile
        applied = JobApplication.objects.filter(job=job, applicant=profile).exists()
        applied_job_ids = list(JobApplication.objects.filter(applicant=profile).values_list('job_id', flat=True))

    skills_list = [s.strip() for s in job.skills_required.split(',')] if job.skills_required else []

    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'applied': applied,
        'applied_job_ids': applied_job_ids,
        'skills_list': skills_list,
    })


@login_required
@role_required('EMPLOYER')
def download_resume(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id)

    if application.job.employer.user != request.user:
        return HttpResponseForbidden("You are not authorized to access this resume.")

    if not application.resume:
        messages.error(request, "Resume file not found.")
        return redirect('view_applicants', job_id=application.job.id)

    try:
        mime_type, _ = mimetypes.guess_type(application.resume.name)
        response = FileResponse(application.resume.open(), content_type=mime_type or 'application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{application.resume.name.split("/")[-1]}"'
        return response
    except FileNotFoundError:
        return HttpResponseForbidden("Resume file is missing from storage.")


@login_required
@role_required('JOB_SEEKER')
def saved_jobs_view(request):
    profile = request.user.jobseekerprofile
    saved_jobs = SavedJob.objects.filter(job_seeker=profile).select_related('job', 'job__employer', 'job__category', 'job__industry')
    paginator = Paginator(saved_jobs, 5)
    return render(request, 'jobs/saved_jobs.html', {'page_obj': paginator.get_page(request.GET.get('page'))})


@login_required
@role_required('JOB_SEEKER')
@require_POST
def save_job_view(request, job_id):
    job = get_object_or_404(Job, id=job_id, is_active=True)
    saved_job, created = SavedJob.objects.get_or_create(job_seeker=request.user.jobseekerprofile, job=job)
    if not created:
        saved_job.delete()
    return JsonResponse({'saved': created, 'message': "Job saved!" if created else "Job removed from saved list."})


@login_required
@role_required('JOB_SEEKER')
def is_job_saved_view(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    is_saved = SavedJob.objects.filter(job_seeker=request.user.jobseekerprofile, job=job).exists()
    return JsonResponse({'is_saved': is_saved})


@login_required
@role_required('EMPLOYER')
def employer_jobs_view(request):
    jobs = Job.objects.filter(employer=request.user.employerprofile).annotate(
        app_count=Count('applications')
    ).select_related('category', 'industry').order_by('-created_at')
    paginator = Paginator(jobs, 5)
    return render(request, 'jobs/employer_jobs.html', {'page_obj': paginator.get_page(request.GET.get('page'))})


@login_required
@role_required('EMPLOYER')
def all_applicants_view(request):
    applications = JobApplication.objects.filter(
        job__employer=request.user.employerprofile
    ).select_related('job', 'applicant').order_by('-applied_at')
    paginator = Paginator(applications, 5)
    return render(request, 'jobs/all_applicants.html', {'page_obj': paginator.get_page(request.GET.get('page'))})
