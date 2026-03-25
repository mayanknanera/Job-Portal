from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, JobSeekerProfile, EmployerProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.role == 'JOB_SEEKER':
        profile, profile_created = JobSeekerProfile.objects.get_or_create(
            user=instance,
            defaults={'full_name': instance.email}
        )
        if profile_created:
            from jobs.email_utils import send_welcome_email
            try:
                send_welcome_email(instance, profile)
            except Exception as e:
                print(f"Welcome email error: {e}")

    elif instance.role == 'EMPLOYER':
        profile, profile_created = EmployerProfile.objects.get_or_create(
            user=instance,
            defaults={'company_name': 'New Company'}
        )
        if profile_created:
            from jobs.email_utils import send_welcome_email
            try:
                send_welcome_email(instance, profile)
            except Exception as e:
                print(f"Welcome email error: {e}")
