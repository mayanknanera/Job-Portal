from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Job, JobApplication

User = get_user_model()

# --------------------------------------------------
# Test Helpers (Factories)
# --------------------------------------------------

def create_employer(email="emp@test.com", password="testpass123"):
    """
    Create an employer user and return EmployerProfile.
    """
    user = User.objects.create_user(
        email=email,
        password=password,
        role="EMPLOYER"
    )
    return user.employerprofile


def create_jobseeker(email="js@test.com", password="testpass123"):
    """
    Create a job seeker user and return their JobSeekerProfile instance.
    (JobApplication.applicant expects a JobSeekerProfile instance)
    """
    user = User.objects.create_user(
        email=email,
        password=password,
        role="JOB_SEEKER"
    )
    # FIX: Return the profile instance, not the User object
    return user.jobseekerprofile 


# --------------------------------------------------
# Job Model Tests
# --------------------------------------------------

class JobModelTests(TestCase):

    def test_job_creation(self):
        employer_profile = create_employer("emp@test.com")

        # FIX: Removed 'job_type' as it is not in your current model
        job = Job.objects.create(
            title="Django Developer",
            employer=employer_profile,
            location="Remote",
            experience_required=2,
            salary="80k-100k",
            description="Mission-critical backend development."
        )

        self.assertEqual(job.title, "Django Developer")
        self.assertEqual(job.employer.user.email, "emp@test.com")


# --------------------------------------------------
# Job Application Tests
# --------------------------------------------------

class JobApplicationTests(TestCase):

    def test_apply_for_job_with_resume(self):
        employer_profile = create_employer("emp2@test.com")
        jobseeker_profile = create_jobseeker("seeker@test.com")

        job = Job.objects.create(
            title="Backend Developer",
            employer=employer_profile
        )

        resume = SimpleUploadedFile(
            "resume.pdf",
            b"Dummy resume content",
            content_type="application/pdf"
        )

        # FIX: Passing the profile instance to 'applicant'
        application = JobApplication.objects.create(
            job=job,
            applicant=jobseeker_profile,
            resume=resume
        )

        self.assertEqual(application.job.title, "Backend Developer")
        # Access email via application.applicant.user
        self.assertEqual(application.applicant.user.email, "seeker@test.com")


# --------------------------------------------------
# Resume Access Permission Tests
# --------------------------------------------------

class ResumeAccessTests(TestCase):

    def test_only_employer_can_download_resume(self):
        employer_profile = create_employer("emp3@test.com")
        other_employer_profile = create_employer("other@test.com", password="pass")

        seeker_profile = create_jobseeker("seeker2@test.com", password="pass")

        job = Job.objects.create(
            title="Python Dev",
            employer=employer_profile
        )

        resume = SimpleUploadedFile(
            "resume.pdf",
            b"Test resume",
            content_type="application/pdf"
        )

        application = JobApplication.objects.create(
            job=job,
            applicant=seeker_profile,
            resume=resume
        )

        # Login as OTHER employer (not the job owner)
        self.client.login(email="other@test.com", password="pass")

        response = self.client.get(
            reverse("download_resume", args=[application.id])
        )

        # Expecting Forbidden access for non-owner employers
        self.assertEqual(response.status_code, 403)