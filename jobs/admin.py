from django.contrib import admin
from .models import Job, JobApplication

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'location', 'experience_required', 'salary', 'is_active')
    list_filter = ('is_active', 'location')
    search_fields = ('title', 'skills_required', 'employer__company_name')

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'applicant', 'status', 'applied_at')
    list_filter = ('status',)
    search_fields = ('job__title', 'applicant__full_name')
