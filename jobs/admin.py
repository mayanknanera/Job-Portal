from django.contrib import admin
from .models import Job, JobApplication, JobCategory, Industry, SavedJob


# ─── Job Category ─────────────────────────────────────────────────────────────

@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display  = ['name', 'created_at']
    search_fields = ['name']
    ordering      = ['name']


# ─── Industry ─────────────────────────────────────────────────────────────────

@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display  = ['name', 'created_at']
    search_fields = ['name']
    ordering      = ['name']


# ─── Job ──────────────────────────────────────────────────────────────────────

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display   = ['title', 'employer', 'job_type', 'work_location_type', 'location', 'is_active', 'created_at']
    list_filter    = ['job_type', 'work_location_type', 'is_active', 'category', 'industry', 'created_at']
    search_fields  = ['title', 'description', 'location', 'skills_required']
    list_editable  = ['is_active']
    readonly_fields = ['slug', 'created_at', 'updated_at']

    # Group fields into logical sections in the detail view
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'employer', 'category', 'industry'),
        }),
        ('Job Details', {
            'fields': ('description', 'location', 'skills_required', 'experience_required'),
        }),
        ('Job Type & Work Location', {
            'fields': ('job_type', 'work_location_type'),
        }),
        ('Salary', {
            'fields': ('salary_min', 'salary_max', 'salary_display'),
        }),
        ('Status', {
            'fields': ('is_active',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),  # hidden by default to reduce clutter
        }),
    )


# ─── Job Application ──────────────────────────────────────────────────────────

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display   = ['applicant', 'job', 'status', 'applied_at']
    list_filter    = ['status', 'applied_at', 'job__job_type', 'job__category']
    search_fields  = ['applicant__full_name', 'applicant__user__email', 'job__title']
    readonly_fields = ['applied_at']

    fieldsets = (
        ('Application Details', {
            'fields': ('job', 'applicant', 'status', 'applied_at'),
        }),
        ('Application Content', {
            'fields': ('cover_letter', 'resume'),
        }),
    )


# ─── Saved Job ────────────────────────────────────────────────────────────────

@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display   = ['job_seeker', 'job', 'saved_at']
    list_filter    = ['saved_at']
    search_fields  = ['job_seeker__full_name', 'job__title']
    readonly_fields = ['saved_at']
