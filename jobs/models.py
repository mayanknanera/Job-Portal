from django.db import models
from django.utils.text import slugify
from .validators import validate_resume
from accounts.models import EmployerProfile, JobSeekerProfile, User

class JobCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Job Categories"
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Industry(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Job(models.Model):
    # Class-level constants to resolve AttributeError in views
    JOB_TYPE_CHOICES = (
        ('FULL_TIME', 'Full Time'),
        ('PART_TIME', 'Part Time'),
        ('CONTRACT', 'Contract'),
        ('INTERNSHIP', 'Internship'),
        ('FREELANCE', 'Freelance'),
        ('TEMPORARY', 'Temporary'),
    )
    
    WORK_LOCATION_TYPE_CHOICES = (
        ('ONSITE', 'On-site'),
        ('REMOTE', 'Remote'),
        ('HYBRID', 'Hybrid'),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField()
    location = models.CharField(max_length=200)
    skills_required = models.TextField(help_text="Comma-separated skills")
    experience_required = models.PositiveIntegerField(default=0, help_text="Years of experience required")
    salary_min = models.PositiveIntegerField(null=True, blank=True, help_text="Minimum salary")
    salary_max = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum salary")
    salary_display = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="How salary is displayed (e.g., 'Negotiable', '$50k-80k')"
    )
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='FULL_TIME')
    work_location_type = models.CharField(max_length=20, choices=WORK_LOCATION_TYPE_CHOICES, default='ONSITE')
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name='jobs')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, blank=True)
    industry = models.ForeignKey(Industry, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.employer.company_name}-{self.id}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} at {self.employer.company_name}"

class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(blank=True)
    resume = models.FileField(upload_to='resumes/', validators=[validate_resume])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['job', 'applicant']

    def __str__(self):
        return f"{self.applicant.full_name} applied for {self.job.title}"

class SavedJob(models.Model):
    job_seeker = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['job_seeker', 'job']

    def __str__(self):
        return f"{self.job_seeker.full_name} saved {self.job.title}"

class EmailNotification(models.Model):
    NOTIFICATION_TYPES = [
        ('APPLICATION_ACCEPTED', 'Application Accepted'),
        ('APPLICATION_REJECTED', 'Application Rejected'),
        ('NEW_MESSAGE', 'New Message'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    job_application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.notification_type} for {self.recipient.email}"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200)
    content = models.TextField()
    job_application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, null=True, blank=True, related_name='messages')
    message_thread = models.ForeignKey('MessageThread', on_delete=models.CASCADE, null=True, blank=True, related_name='messages')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"From {self.sender.email} to {self.recipient.email}: {self.subject}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update thread timestamp
        if self.message_thread:
            self.message_thread.save()

class MessageThread(models.Model):
    """Group messages by conversation thread"""
    participants = models.ManyToManyField(User, related_name='message_threads')
    job_application = models.OneToOneField(JobApplication, on_delete=models.CASCADE, null=True, blank=True, related_name='message_thread')
    subject = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Thread: {self.subject}"

    def get_last_message(self):
        return self.messages.first()

    def get_unread_count(self, user):
        return self.messages.filter(recipient=user, is_read=False).count()