from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import EmailNotification

class NotificationService:
    @staticmethod
    def send_application_status_notification(application):
        """Send email notification for application status change"""
        
        # Determine notification type and message
        if application.status == 'ACCEPTED':
            notification_type = 'APPLICATION_ACCEPTED'
            subject = f"🎉 Congratulations! Your application for {application.job.title} has been accepted!"
            message = f"""
            Dear {application.applicant.full_name},
            
            Great news! Your application for the position of {application.job.title} at {application.job.employer.company_name} has been accepted.
            
            Next steps:
            - The employer may contact you soon for an interview
            - Prepare for the interview process
            - Review the job details again: {application.job.title}
            
            View your application status here: http://127.0.0.1:8000/jobs/applied/
            
            Best regards,
            The {application.job.employer.company_name} Team
            """
        elif application.status == 'REJECTED':
            notification_type = 'APPLICATION_REJECTED'
            subject = f"Application Update: {application.job.title}"
            message = f"""
            Dear {application.applicant.full_name},
            
            We regret to inform you that your application for the position of {application.job.title} at {application.job.employer.company_name} has been carefully reviewed and, at this time, will not be proceeding further.
            
            This doesn't reflect on your qualifications or potential. We encourage you to continue your job search and wish you the best in finding the right opportunity.
            
            View other opportunities: http://127.0.0.1:8000/jobs/
            
            Sincerely,
            The {application.job.employer.company_name} Hiring Team
            """
        else:
            return None  # No notification needed for other statuses

        # Create notification record
        EmailNotification.objects.create(
            recipient=application.applicant.user,
            job_application=application,
            notification_type=notification_type,
            message=message,
        )
        
        # Send email
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[application.applicant.user.email],
                html_message=render_to_string('jobs/email/notification.html', {
                    'subject': subject,
                    'message': message,
                    'application': application,
                    'job': application.job,
                })
            )
            return True
        except Exception:
            # Log error silently in production
            return False
