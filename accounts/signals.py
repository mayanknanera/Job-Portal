from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, JobSeekerProfile, EmployerProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically runs after a new User is saved.

    - Creates the appropriate profile (JobSeekerProfile or EmployerProfile)
      based on the user's role.
    - Sends a welcome email to the new user.
    - Only runs on creation (not on every save/update).
    """
    if not created:
        return  # skip if this is an update, not a new user

    if instance.role == 'JOB_SEEKER':
        # Create a job seeker profile using the email as a placeholder name
        profile, profile_created = JobSeekerProfile.objects.get_or_create(
            user=instance,
            defaults={'full_name': instance.email},
        )
        if profile_created:
            _send_welcome(instance, profile)

    elif instance.role == 'EMPLOYER':
        # Create an employer profile with a default company name
        profile, profile_created = EmployerProfile.objects.get_or_create(
            user=instance,
            defaults={'company_name': 'New Company'},
        )
        if profile_created:
            _send_welcome(instance, profile)


def _send_welcome(user, profile):
    """Helper to send a welcome email, silently ignoring any errors."""
    from jobs.email_utils import send_welcome_email
    try:
        send_welcome_email(user, profile)
    except Exception as e:
        print(f"Welcome email error: {e}")
