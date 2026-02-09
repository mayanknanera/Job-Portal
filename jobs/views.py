from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Job, JobApplication, JobCategory, Industry, SavedJob, EmailNotification, Message, MessageThread
from .forms import JobForm, MessageForm, NewMessageForm
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from accounts.decorators import role_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, FileResponse, HttpResponseForbidden
from django.utils import timezone 
from datetime import timedelta 
from .services import NotificationService
from accounts.models import User

import mimetypes

def _parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

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
    # select_related avoids the N+1 query problem for foreign keys
    jobs = Job.objects.filter(is_active=True).select_related('employer', 'category', 'industry')
 
    # GET parameters
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
 
    # Q objects allow for complex OR lookups
    if keyword:
        jobs = jobs.filter(
            Q(title__icontains=keyword) | Q(description__icontains=keyword)
        )
 
    # Fields like location and title should be indexed for speed
    if location:
        jobs = jobs.filter(location__icontains=location)
 
    if skill:
        jobs = jobs.filter(skills_required__icontains=skill)
 
    if experience:
        experience_value = _parse_int(experience)
        if experience_value is not None:
            jobs = jobs.filter(experience_required__lte=experience_value)
    
    if category:
        jobs = jobs.filter(category_id=category)
    
    if industry:
        jobs = jobs.filter(industry_id=industry)
    
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    
    if work_location_type:
        jobs = jobs.filter(work_location_type=work_location_type)

    if salary_min:
        salary_min_value = _parse_int(salary_min)
        if salary_min_value is not None:
            jobs = jobs.filter(salary_min__gte=salary_min_value)
    
    if salary_max:
        salary_max_value = _parse_int(salary_max)
        if salary_max_value is not None:
            jobs = jobs.filter(salary_max__lte=salary_max_value)
    
    # Date posted filtering
    if date_posted:
        now = timezone.now()
        if date_posted == 'today':
            jobs = jobs.filter(created_at__date=now.date())
        elif date_posted == 'week':
            jobs = jobs.filter(created_at__gte=now - timedelta(days=7))
        elif date_posted == 'month':
            jobs = jobs.filter(created_at__gte=now - timedelta(days=30))
        elif date_posted == '3months':
            jobs = jobs.filter(created_at__gte=now - timedelta(days=90))
    
    # Pagination: 5 jobs per page as requested
    paginator = Paginator(jobs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    # Efficiently fetch applied jobs for the current seeker
    applied_job_ids = []
    saved_job_ids = []
    
    if request.user.role == 'JOB_SEEKER':
        profile = getattr(request.user, 'jobseekerprofile', None)
        if profile:
            # Using list() to force evaluation once, keeping it in memory for the template
            applied_job_ids = list(JobApplication.objects.filter(
                applicant=profile
            ).values_list('job_id', flat=True))
            
            saved_job_ids = list(SavedJob.objects.filter(
                job_seeker=profile
            ).values_list('job_id', flat=True))

    date_posted_choices = [
        ('', 'Any Time'),
        ('today', 'Today'),
        ('week', 'Last Week'),
        ('month', 'Last Month'),
        ('3months', 'Last 3 Months'),
    ]
    
    return render(request, 'jobs/job_list.html', {
        'page_obj': page_obj,
        'applied_job_ids': applied_job_ids,
        'saved_job_ids': saved_job_ids,
        'categories': JobCategory.objects.all(),
        'industries': Industry.objects.all(),
        'job_types': Job.JOB_TYPE_CHOICES,
        'work_location_types': Job.WORK_LOCATION_TYPE_CHOICES,
        'date_posted_choices': date_posted_choices,
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
    
    if application.job.employer.user != request.user:
        messages.error(request, "Unauthorized")
        return redirect('employer_dashboard')
    
    if status in ['ACCEPTED', 'REJECTED']:
        old_status = application.status
        application.status = status
        application.save()
        
        # Send email notification
        NotificationService.send_application_status_notification(application)
        
        messages.success(request, f"Application status updated to {status}")
    else:
        messages.error(request, "Invalid status")
    
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
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except FileNotFoundError:
        return HttpResponseForbidden("Physical file missing from storage.")

@login_required
def notifications_view(request):
    """Display notifications for current user"""
    notifications = EmailNotification.objects.filter(
        recipient=request.user,
        is_read=False
    ).select_related('job_application__job', 'job_application__applicant')
    
    # Mark notifications as read when viewed
    if request.method == 'POST':
        notification_ids = request.POST.getlist('notification_ids')
        EmailNotification.objects.filter(
            id__in=notification_ids,
            recipient=request.user
        ).update(is_read=True)
        return JsonResponse({'status': 'success'})
    
    # Apply pagination
    paginator = Paginator(notifications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'jobs/notifications.html', {
        'page_obj': page_obj
    })

@login_required
@role_required('JOB_SEEKER')
def saved_jobs_view(request):
    """Display saved jobs for the current job seeker"""
    profile = request.user.jobseekerprofile
    saved_jobs = SavedJob.objects.filter(
        job_seeker=profile
    ).select_related('job', 'job__employer', 'job__category', 'job__industry')
    
    # Apply pagination
    paginator = Paginator(saved_jobs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'jobs/saved_jobs.html', {
        'page_obj': page_obj
    })

@login_required
@role_required('JOB_SEEKER')
@require_POST
def save_job_view(request, job_id):
    """Save a job"""
    job = get_object_or_404(Job, id=job_id, is_active=True)
    profile = request.user.jobseekerprofile
    
    saved_job, created = SavedJob.objects.get_or_create(
        job_seeker=profile,
        job=job
    )
    
    if created:
        return JsonResponse({
            'saved': True,
            'message': "Job saved successfully!"
        })
    else:
        saved_job.delete()
        return JsonResponse({
            'saved': False,
            'message': "Job removed from saved list!"
        })

@login_required
@role_required('JOB_SEEKER')
def is_job_saved_view(request, job_id):
    """Check if a job is saved by the current user"""
    job = get_object_or_404(Job, id=job_id)
    profile = request.user.jobseekerprofile
    
    is_saved = SavedJob.objects.filter(
        job_seeker=profile,
        job=job
    ).exists()
    
    return JsonResponse({'is_saved': is_saved})

# Messaging Views
@login_required
def inbox_view(request):
    """Display user's message threads"""
    threads = MessageThread.objects.filter(
        participants=request.user
    ).select_related('job_application__job', 'job_application__applicant')
    
    # Get unread count for each thread
    for thread in threads:
        thread.unread_count = thread.get_unread_count(request.user)
    
    paginator = Paginator(threads, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'jobs/inbox.html', {
        'page_obj': page_obj
    })

@login_required
def message_thread_view(request, thread_id):
    """Display messages in a thread"""
    thread = get_object_or_404(MessageThread, id=thread_id, participants=request.user)
    
    # Mark messages as read
    Message.objects.filter(
        message_thread=thread,
        recipient=request.user,
        is_read=False
    ).update(is_read=True)
    
    messages = thread.messages.all().select_related('sender', 'recipient')
    
    # Get other participant
    other_participant = thread.participants.exclude(id=request.user.id).first()
    
    return render(request, 'jobs/message_thread.html', {
        'thread': thread,
        'messages': messages,
        'other_participant': other_participant
    })

@login_required
def compose_message_view(request):
    """Compose a new message"""
    if request.method == 'POST':
        form = NewMessageForm(request.user, request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            
            # Create or get message thread
            thread, created = MessageThread.objects.get_or_create(
                job_application=None,
                subject=message.subject,
                defaults={'subject': message.subject}
            )
            
            # Add participants to thread
            thread.participants.add(request.user, message.recipient)
            
            message.message_thread = thread
            message.save()
            
            # Create notification for recipient
            EmailNotification.objects.create(
                recipient=message.recipient,
                notification_type='NEW_MESSAGE',
                message=f"New message from {request.user.email}: {message.subject}"
            )
            
            messages.success(request, "Message sent successfully!")
            return redirect('inbox')
    else:
        form = NewMessageForm(request.user)
    
    return render(request, 'jobs/compose_message.html', {
        'form': form
    })

@login_required
@require_POST
def send_message_view(request, thread_id):
    """Send a reply in a thread"""
    thread = get_object_or_404(MessageThread, id=thread_id, participants=request.user)
    
    content = request.POST.get('content')
    if content:
        # Get other participant
        other_participant = thread.participants.exclude(id=request.user.id).first()
        
        message = Message.objects.create(
            sender=request.user,
            recipient=other_participant,
            subject=thread.subject,
            content=content,
            message_thread=thread
        )
        
        # Create notification for recipient
        EmailNotification.objects.create(
            recipient=other_participant,
            notification_type='NEW_MESSAGE',
            message=f"New message from {request.user.email}: {thread.subject}"
        )
        
        return JsonResponse({'status': 'success', 'message_id': message.id})
    
    return JsonResponse({'status': 'error', 'message': 'Message content is required'})

@login_required
def message_with_applicant_view(request, application_id):
    """Start a conversation with an applicant"""
    application = get_object_or_404(JobApplication, id=application_id)
    
    # Check permissions
    if request.user.role == 'EMPLOYER':
        if application.job.employer.user != request.user:
            return HttpResponseForbidden("Unauthorized")
        recipient = application.applicant.user
    elif request.user.role == 'JOB_SEEKER':
        if application.applicant.user != request.user:
            return HttpResponseForbidden("Unauthorized")
        recipient = application.job.employer.user
    else:
        return HttpResponseForbidden("Unauthorized")
    
    # Get or create thread
    thread, created = MessageThread.objects.get_or_create(
        job_application=application,
        subject=f"Re: {application.job.title} Application"
    )
    
    # Add participants if new thread
    if created:
        thread.participants.add(request.user, recipient)
    
    # Redirect to thread
    return redirect('message_thread', thread_id=thread.id)
