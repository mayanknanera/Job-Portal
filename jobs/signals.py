from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import JobApplication
import sys

@receiver(post_save, sender=JobApplication)
def job_application_created(sender, instance, created, **kwargs):
    if created:
        job = instance.job
        applicant = instance.applicant
        employer = job.employer
        
        # Get applicant name, fallback to email if full_name is empty
        applicant_name = applicant.full_name.strip() if applicant.full_name else applicant.user.email
        
        print(f"\n=== NEW JOB APPLICATION ===", file=sys.stdout)
        print(f"Applicant: {applicant_name}", file=sys.stdout)
        print(f"Company: {employer.company_name}", file=sys.stdout)
        print(f"Job: {job.title}", file=sys.stdout)
        print(f"Applicant Email: {applicant.user.email}", file=sys.stdout)
        print(f"Employer Email: {employer.user.email}", file=sys.stdout)
        print("===========================\n", file=sys.stdout)

        # Email to Job Seeker
        try:
            send_mail(
                subject="Application Submitted Successfully",
                message=f"You have applied for {job.title} at {employer.company_name}.",
                from_email=None,
                recipient_list=[applicant.user.email],
            )
        except Exception as e:
            print(f"Error sending email to applicant: {e}", file=sys.stderr)

        # Email to Employer
        try:
            send_mail(
                subject="New Job Application Received",
                message=f"{applicant_name} has applied for {job.title}.",
                from_email=None,
                recipient_list=[employer.user.email],
            )
        except Exception as e:
            print(f"Error sending email to employer: {e}", file=sys.stderr)

@receiver(pre_save, sender=JobApplication)
def job_application_status_changed(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        previous = JobApplication.objects.get(pk=instance.pk)
        
        if previous.status != instance.status:
            # Get applicant name, fallback to email if full_name is empty
            applicant_name = instance.applicant.full_name.strip() if instance.applicant.full_name else instance.applicant.user.email
            
            print(f"\n=== APPLICATION STATUS CHANGED ===", file=sys.stdout)
            print(f"Applicant: {applicant_name}", file=sys.stdout)
            print(f"Job: {instance.job.title}", file=sys.stdout)
            print(f"Status: {previous.status} → {instance.status}", file=sys.stdout)
            print("===================================\n", file=sys.stdout)
            
            try:
                send_mail(
                    subject="Application Status Updated",
                    message=f"Your application for {instance.job.title} is now {instance.status}.",
                    from_email=None,
                    recipient_list=[instance.applicant.user.email],
                )
            except Exception as e:
                print(f"Error sending status update email: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Error in status change signal: {e}", file=sys.stderr)
