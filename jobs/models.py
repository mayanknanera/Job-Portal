from django.db import models
from django.utils.text import slugify
from .validators import validate_resume
from accounts.models import EmployerProfile, JobSeekerProfile


# ─── Job Category ─────────────────────────────────────────────────────────────
# Groups jobs into categories like "Software Development", "Marketing", etc.

class JobCategory(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    slug        = models.SlugField(unique=True, blank=True)       # auto-generated from name
    description = models.TextField(blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Job Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        # Auto-generate slug from name if not already set
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ─── Industry ─────────────────────────────────────────────────────────────────
# The sector a company operates in, e.g. "Healthcare", "Finance", "Technology".

class Industry(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    slug        = models.SlugField(unique=True, blank=True)       # auto-generated from name
    description = models.TextField(blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Industry'
        verbose_name_plural = 'Industries'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ─── Job ──────────────────────────────────────────────────────────────────────
# The main model. Each job is posted by an employer and can be applied to.

class Job(models.Model):

    # What kind of employment is offered
    JOB_TYPE_CHOICES = (
        ('FULL_TIME',  'Full Time'),
        ('PART_TIME',  'Part Time'),
        ('CONTRACT',   'Contract'),
        ('INTERNSHIP', 'Internship'),
        ('FREELANCE',  'Freelance'),
        ('TEMPORARY',  'Temporary'),
    )

    # Where the work takes place
    WORK_LOCATION_TYPE_CHOICES = (
        ('ONSITE', 'On-site'),
        ('REMOTE', 'Remote'),
        ('HYBRID', 'Hybrid'),
    )

    # ── Core fields ──
    title       = models.CharField(max_length=200)
    slug        = models.SlugField(max_length=250, unique=True, blank=True)  # used in the URL
    description = models.TextField()
    location    = models.CharField(max_length=200)

    # ── Requirements ──
    skills_required     = models.TextField(help_text="Comma-separated skills")
    experience_required = models.PositiveIntegerField(default=0, help_text="Years of experience required")

    # ── Salary ──
    salary_min     = models.PositiveIntegerField(null=True, blank=True)
    salary_max     = models.PositiveIntegerField(null=True, blank=True)
    salary_display = models.CharField(                                        # human-readable label
        max_length=100, null=True, blank=True,
        help_text="e.g. 'Negotiable' or '$50k-80k'",
    )

    # ── Type & location ──
    job_type           = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='FULL_TIME')
    work_location_type = models.CharField(max_length=20, choices=WORK_LOCATION_TYPE_CHOICES, default='ONSITE')

    # ── Relationships ──
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name='jobs')
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, blank=True)
    industry = models.ForeignKey(Industry,     on_delete=models.SET_NULL, null=True, blank=True)

    # ── Status & timestamps ──
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Build slug from title + company name + id on first save
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.employer.company_name}-{self.id}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} at {self.employer.company_name}"


# ─── Job Application ──────────────────────────────────────────────────────────
# Created when a job seeker applies to a job.

class JobApplication(models.Model):

    STATUS_CHOICES = [
        ('PENDING',  'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]

    job          = models.ForeignKey(Job,              on_delete=models.CASCADE, related_name='applications')
    applicant    = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(blank=True)
    resume       = models.FileField(upload_to='resumes/', validators=[validate_resume])
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    applied_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        # A job seeker can only apply to the same job once
        unique_together = ['job', 'applicant']

    def __str__(self):
        return f"{self.applicant.full_name} applied for {self.job.title}"


# ─── Saved Job ────────────────────────────────────────────────────────────────
# Created when a job seeker bookmarks a job to apply later.

class SavedJob(models.Model):
    job_seeker = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='saved_jobs')
    job        = models.ForeignKey(Job,              on_delete=models.CASCADE, related_name='saved_by')
    saved_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        # A job seeker can only save the same job once
        unique_together = ['job_seeker', 'job']

    def __str__(self):
        return f"{self.job_seeker.full_name} saved {self.job.title}"
