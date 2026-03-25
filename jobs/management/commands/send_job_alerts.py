"""
Management command to send job alerts to users
Run with: python manage.py send_job_alerts
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import User, JobSeekerProfile
from jobs.models import Job
from jobs.email_utils import send_job_alert_email


class Command(BaseCommand):
    help = 'Send job alert emails to job seekers with matching jobs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Number of days to look back for new jobs (default: 1)'
        )
        parser.add_argument(
            '--max-jobs',
            type=int,
            default=5,
            help='Maximum number of jobs to include in alert (default: 5)'
        )

    def handle(self, *args, **options):
        days = options['days']
        max_jobs = options['max_jobs']
        
        # Get date threshold
        date_threshold = timezone.now() - timedelta(days=days)
        
        # Get all job seekers
        job_seekers = User.objects.filter(role='JOB_SEEKER', is_active=True)
        
        emails_sent = 0
        
        for user in job_seekers:
            try:
                profile = user.jobseekerprofile
                
                # Skip if no skills defined
                if not profile.skills:
                    continue
                
                # Get user's skills as list
                user_skills = [skill.strip().lower() for skill in profile.skills.split(',')]
                
                # Find matching jobs
                matching_jobs = []
                recent_jobs = Job.objects.filter(
                    is_active=True,
                    created_at__gte=date_threshold
                ).order_by('-created_at')
                
                for job in recent_jobs:
                    job_skills = [skill.strip().lower() for skill in job.skills_required.split(',')]
                    
                    # Check if any user skill matches job skills
                    if any(user_skill in job_skills for user_skill in user_skills):
                        matching_jobs.append(job)
                        
                        if len(matching_jobs) >= max_jobs:
                            break
                
                # Send email if matching jobs found
                if matching_jobs:
                    success = send_job_alert_email(user, matching_jobs)
                    if success:
                        emails_sent += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Sent job alert to {user.email} ({len(matching_jobs)} jobs)'
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f'Failed to send email to {user.email}')
                        )
                        
            except JobSeekerProfile.DoesNotExist:
                continue
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing {user.email}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nJob alerts sent: {emails_sent} out of {job_seekers.count()} job seekers'
            )
        )
