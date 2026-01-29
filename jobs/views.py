from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Job, JobApplication
from django import forms
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from accounts.decorators import role_required
from django.shortcuts import render, get_object_or_404

# Job Post Form
class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'location', 'skills_required', 'experience_required', 'salary']

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
            experience = float(experience)
            jobs = jobs.filter(experience_required__lte=experience)
        except (ValueError, TypeError):
            pass
    
    # Apply pagination
    paginator = Paginator(jobs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    applied_job_ids = []
    if request.user.role == 'JOB_SEEKER':
        applied_job_ids = JobApplication.objects.filter(
            applicant=request.user.jobseekerprofile
        ).values_list('job_id', flat=True)

    return render(request, 'jobs/job_list.html', {
        'page_obj': page_obj,
        'applied_job_ids': applied_job_ids
    })

@login_required
@role_required('JOB_SEEKER')
def apply_job_view(request, job_id):
    job = Job.objects.select_related('employer').get(id=job_id)
    profile = request.user.jobseekerprofile

    if JobApplication.objects.filter(job=job, applicant=profile).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect('job_list')

    if request.method == "POST":
        cover_letter = request.POST.get('cover_letter')
        JobApplication.objects.create(
            job=job,
            applicant=profile,
            cover_letter=cover_letter
        )
        messages.success(request, "Application submitted successfully!")
        return redirect('applied_jobs')

    return render(request, 'jobs/apply_job.html', {'job': job})

@login_required
@role_required('EMPLOYER')
def view_applicants_view(request, job_id):
    job = Job.objects.get(id=job_id, employer=request.user.employerprofile)
    applications = job.applications.all()
    
    return render(request, 'jobs/view_applicants.html', {
        'job': job,
        'applications': applications
    })

@login_required
@role_required('EMPLOYER')
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