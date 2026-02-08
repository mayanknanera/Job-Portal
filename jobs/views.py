from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Job, JobApplication
from .forms import JobForm
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from accounts.decorators import role_required
from django.views.decorators.http import require_POST
from django.http import FileResponse, HttpResponseForbidden

import mimetypes

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
    jobs = Job.objects.filter(is_active=True).select_related('employer')

    # GET parameters
    keyword = request.GET.get('keyword')
    location = request.GET.get('location')
    skill = request.GET.get('skill')
    experience = request.GET.get('experience')

    if keyword:
        jobs = jobs.filter(
            Q(title__icontains=keyword) |
            Q(description__icontains=keyword)
        )

    if location:
        jobs = jobs.filter(location__icontains=location)

    if skill:
        jobs = jobs.filter(skills_required__icontains=skill)

    if experience:
        try:
            experience = int(experience)
            jobs = jobs.filter(experience_required__lte=experience)
        except (ValueError, TypeError):
            pass
    
    # Apply pagination
    paginator = Paginator(jobs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    applied_job_ids = []
    if request.user.role == 'JOB_SEEKER':
        profile = getattr(request.user, 'jobseekerprofile', None)
        if profile:
            applied_job_ids = JobApplication.objects.filter(
                applicant=profile
            ).values_list('job_id', flat=True)
        else:
            applied_job_ids = []
    else:
        applied_job_ids = []

    return render(request, 'jobs/job_list.html', {
        'page_obj': page_obj,
        'applied_job_ids': applied_job_ids
    })

@login_required
@role_required('JOB_SEEKER')
def apply_job_view(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    profile = getattr(request.user, 'jobseekerprofile', None)
    if not profile:
        messages.error(request, "Please complete your profile first.")
        return redirect('edit_profile')
    
    # Prevent duplicate signal connections
    if JobApplication.objects.filter(job=job, applicant=profile).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect('job_list')

    if request.method == "POST":
        # System check: Ensure the profile actually has a resume
        if not profile.resume:
            messages.error(request, "Resume missing")
            return redirect('edit_profile')

        # Create the application using the profile's resume
        JobApplication.objects.create(
            job=job,
            applicant=profile,
            resume=profile.resume, # Re-uses the existing profile file
            cover_letter=request.POST.get('cover_letter')
        )
        
        messages.success(request, "Application successful. Profile dossier linked!")
        return redirect('applied_jobs')

    return render(request, 'jobs/apply_job.html', {'job': job, 'profile': profile})

@login_required
@role_required('EMPLOYER')
def view_applicants_view(request, job_id):
    job = get_object_or_404(Job, id=job_id, employer=request.user.employerprofile)
    applications = job.applications.all()
    
    return render(request, 'jobs/view_applicants.html', {
        'job': job,
        'applications': applications
    })

@login_required
@role_required('EMPLOYER')
@require_POST
def update_application_status(request, app_id, status):
    application = JobApplication.objects.get(id=app_id)
    if application.job.employer != request.user.employerprofile:
        messages.error(request, "Unauthorized")
        return redirect('employer_dashboard')
    
    if status in ['ACCEPTED', 'REJECTED']:
        application.status = status
        application.save()
        messages.success(request, f"Application status updated to {status}")
    
    return redirect('view_applicants', job_id=application.job.id)

@login_required
@role_required('JOB_SEEKER')
def applied_jobs_view(request):
    applications = JobApplication.objects.filter(
        applicant=request.user.jobseekerprofile
    ).select_related('job', 'job__employer')

    return render(request, 'jobs/applied_jobs.html', {
        'applications': applications
    })

def job_detail_view(request, slug):
    job = get_object_or_404(
        Job.objects.select_related('employer'),
        slug=slug
    )

    applied = False
    if request.user.is_authenticated and request.user.role == 'JOB_SEEKER':
        applied = JobApplication.objects.filter(
            job=job,
            applicant=request.user.jobseekerprofile
        ).exists()

    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'applied': applied
    })


@login_required
@role_required('EMPLOYER')
def download_resume(request, application_id):
    # 1. First, find the application. If it doesn't exist at all, 404 is correct.
    application = get_object_or_404(JobApplication, id=application_id)
    
    # 2. Check if the logged-in employer owns the job for this application.
    # If they don't, return 403 Forbidden.
    if application.job.employer.user != request.user:
        return HttpResponseForbidden("You are not authorized to access this dossier.")
    
    if not application.resume:
        messages.error(request, "Resume file not found.")
        return redirect('view_applicants', job_id=application.job.id)
        
    try:
        # Detect MIME type based on file extension
        mime_type, _ = mimetypes.guess_type(application.resume.name)
        if not mime_type:
            mime_type = 'application/octet-stream'  # fallback

        response = FileResponse(
            application.resume.open(), 
            content_type=mime_type
        )
        filename = application.resume.name.split('/')[-1]  # Get actual filename
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
    except FileNotFoundError:
        return HttpResponseForbidden("Physical file missing from storage.")