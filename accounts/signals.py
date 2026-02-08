from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, JobSeekerProfile, EmployerProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create profile ONLY for public roles.
    ADMIN users must NOT get public profiles.
    """
    if not created:
        return

    # Job Seeker Profile
    if instance.role == 'JOB_SEEKER':
        JobSeekerProfile.objects.get_or_create(
            user=instance,
            defaults={
                'full_name': instance.email
            }
        )

    # Employer Profile
    elif instance.role == 'EMPLOYER':
        EmployerProfile.objects.get_or_create(
            user=instance,
            defaults={
                'company_name': 'New Company'
            }
        )
