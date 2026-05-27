from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

# Base URL used to build links inside emails
SITE_URL = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')


# ─── Core Email Sender ────────────────────────────────────────────────────────

def send_html_email(subject, template_name, context, recipient_list):
    """
    Render an HTML email template and send it.

    - Automatically adds a plain-text fallback (stripped HTML) for email clients
      that don't support HTML.
    - Returns True on success, False on failure.
    """
    context['site_url'] = SITE_URL  # make site URL available in all email templates

    try:
        html_content = render_to_string(template_name, context)
        email = EmailMultiAlternatives(
            subject    = subject,
            body       = strip_tags(html_content),  # plain-text version
            from_email = settings.DEFAULT_FROM_EMAIL,
            to         = recipient_list,
        )
        email.attach_alternative(html_content, "text/html")  # attach HTML version
        email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


# ─── Welcome Email ────────────────────────────────────────────────────────────

def send_welcome_email(user, user_profile):
    """Send a welcome email to a newly registered user."""
    # Get the display name from whichever profile type this is
    name = (
        getattr(user_profile, 'full_name', None)
        or getattr(user_profile, 'company_name', user.email)
    )

    # Point to the correct dashboard based on role
    dashboard_path = (
        "/accounts/jobseeker-dashboard/"
        if user.role == "JOB_SEEKER"
        else "/accounts/employer-dashboard/"
    )

    return send_html_email(
        subject        = f'Welcome to CareerPlus, {name}!',
        template_name  = 'emails/welcome_email.html',
        context        = {
            'user_name':     name,
            'user_role':     "Job Seeker" if user.role == "JOB_SEEKER" else "Employer",
            'dashboard_url': SITE_URL + dashboard_path,
        },
        recipient_list = [user.email],
    )


# ─── Application Emails ───────────────────────────────────────────────────────

def send_application_confirmation_email(application):
    """Notify the job seeker that their application was received."""
    return send_html_email(
        subject        = f'Application Submitted: {application.job.title}',
        template_name  = 'emails/application_confirmation.html',
        context        = {
            'applicant_name': application.applicant.full_name,
            'job_title':      application.job.title,
            'company_name':   application.job.employer.company_name,
            'job_location':   application.job.location,
            'applied_date':   application.applied_at.strftime('%B %d, %Y'),
            'job_url':        f"{SITE_URL}/jobs/{application.job.slug}/",
            'dashboard_url':  f"{SITE_URL}/jobs/applied/",
        },
        recipient_list = [application.applicant.user.email],
    )


def send_application_status_update_email(application):
    """Notify the job seeker that their application status has changed."""
    status_display = {
        'ACCEPTED': 'Accepted',
        'REJECTED': 'Rejected',
        'PENDING':  'Pending',
    }
    # Add a celebration emoji for accepted applications
    prefix = "🎉 " if application.status == "ACCEPTED" else ""

    return send_html_email(
        subject        = f'{prefix}Application Status Update: {application.job.title}',
        template_name  = 'emails/application_status_update.html',
        context        = {
            'applicant_name':  application.applicant.full_name,
            'job_title':       application.job.title,
            'company_name':    application.job.employer.company_name,
            'status':          application.status,
            'status_display':  status_display.get(application.status, application.status),
            'dashboard_url':   f"{SITE_URL}/jobs/applied/",
            'browse_jobs_url': f"{SITE_URL}/jobs/",
        },
        recipient_list = [application.applicant.user.email],
    )


def send_new_applicant_notification_email(job, application):
    """Notify the employer that someone applied to their job."""
    return send_html_email(
        subject        = f'New Application: {application.applicant.full_name} applied for {job.title}',
        template_name  = 'emails/new_applicant_notification.html',
        context        = {
            'employer_name':         job.employer.company_name,
            'applicant_name':        application.applicant.full_name,
            'job_title':             job.title,
            'applied_date':          application.applied_at.strftime('%B %d, %Y'),
            'applicant_experience':  application.applicant.experience or 'Not specified',
            'view_applicant_url':    f"{SITE_URL}/jobs/{job.id}/applicants/",
        },
        recipient_list = [job.employer.user.email],
    )

