from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

SITE_URL = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')


def send_html_email(subject, template_name, context, recipient_list):
    context['site_url'] = SITE_URL
    try:
        html_content = render_to_string(template_name, context)
        email = EmailMultiAlternatives(
            subject=subject,
            body=strip_tags(html_content),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list,
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


def send_welcome_email(user, user_profile):
    name = getattr(user_profile, 'full_name', None) or getattr(user_profile, 'company_name', user.email)
    dashboard_path = "/accounts/jobseeker-dashboard/" if user.role == "JOB_SEEKER" else "/accounts/employer-dashboard/"
    return send_html_email(
        subject=f'Welcome to CareerPlus, {name}!',
        template_name='emails/welcome_email.html',
        context={
            'user_name': name,
            'user_role': "Job Seeker" if user.role == "JOB_SEEKER" else "Employer",
            'dashboard_url': SITE_URL + dashboard_path,
        },
        recipient_list=[user.email],
    )


def send_application_confirmation_email(application):
    return send_html_email(
        subject=f'Application Submitted: {application.job.title}',
        template_name='emails/application_confirmation.html',
        context={
            'applicant_name': application.applicant.full_name,
            'job_title': application.job.title,
            'company_name': application.job.employer.company_name,
            'job_location': application.job.location,
            'applied_date': application.applied_at.strftime('%B %d, %Y'),
            'job_url': f"{SITE_URL}/jobs/{application.job.slug}/",
            'dashboard_url': f"{SITE_URL}/jobs/applied/",
        },
        recipient_list=[application.applicant.user.email],
    )


def send_application_status_update_email(application):
    status_display = {'ACCEPTED': 'Accepted', 'REJECTED': 'Rejected', 'PENDING': 'Pending'}
    prefix = "🎉 " if application.status == "ACCEPTED" else ""
    return send_html_email(
        subject=f'{prefix}Application Status Update: {application.job.title}',
        template_name='emails/application_status_update.html',
        context={
            'applicant_name': application.applicant.full_name,
            'job_title': application.job.title,
            'company_name': application.job.employer.company_name,
            'status': application.status,
            'status_display': status_display.get(application.status, application.status),
            'dashboard_url': f"{SITE_URL}/jobs/applied/",
            'browse_jobs_url': f"{SITE_URL}/jobs/",
        },
        recipient_list=[application.applicant.user.email],
    )


def send_job_alert_email(user, jobs):
    job_list = [{
        'title': job.title,
        'company_name': job.employer.company_name,
        'location': job.location,
        'job_type': job.get_job_type_display(),
        'salary': job.salary_display,
        'description': job.description,
        'url': f"{SITE_URL}/jobs/{job.slug}/",
    } for job in jobs]

    count = len(jobs)
    name = getattr(getattr(user, 'jobseekerprofile', None), 'full_name', user.email)
    return send_html_email(
        subject=f'🚀 {count} New Job{"s" if count > 1 else ""} Matching Your Profile',
        template_name='emails/job_alert.html',
        context={
            'user_name': name,
            'job_count': count,
            'jobs': job_list,
            'browse_jobs_url': f"{SITE_URL}/jobs/",
            'unsubscribe_url': f"{SITE_URL}/accounts/settings/",
        },
        recipient_list=[user.email],
    )


def send_new_applicant_notification_email(job, application):
    return send_html_email(
        subject=f'New Application: {application.applicant.full_name} applied for {job.title}',
        template_name='emails/new_applicant_notification.html',
        context={
            'employer_name': job.employer.company_name,
            'applicant_name': application.applicant.full_name,
            'job_title': job.title,
            'applied_date': application.applied_at.strftime('%B %d, %Y'),
            'applicant_experience': application.applicant.experience or 'Not specified',
            'view_applicant_url': f"{SITE_URL}/jobs/{job.id}/applicants/",
        },
        recipient_list=[job.employer.user.email],
    )
