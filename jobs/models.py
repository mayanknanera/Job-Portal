from django.db import models
from django.utils.text import slugify
from accounts.models import EmployerProfile, JobSeekerProfile

class Job(models.Model):
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    slug = models.SlugField(null=True, blank=True)
    description = models.TextField()
    location = models.CharField(max_length=100)
    skills_required = models.TextField()
    experience_required = models.CharField(max_length=5, blank=True, null=True, help_text="Years of experience required")
    salary = models.CharField(max_length=10, blank=True, null=True, help_text="Salary range or amount")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.title)
            counter = 1
            self.slug = slug
            while Job.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
        

    def __str__(self):
        return f"{self.title} at {self.employer.company_name}"

class JobApplication(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    )
    
    job = models.ForeignKey('Job', on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'applicant')

    def __str__(self):
        return f"{self.applicant.full_name} → {self.job.title}"
