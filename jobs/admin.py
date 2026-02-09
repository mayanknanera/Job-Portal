from django.contrib import admin
from .models import Job, JobApplication, JobCategory, Industry, SavedJob, EmailNotification, Message, MessageThread

@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    ordering = ['name']

@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    ordering = ['name']

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'employer', 'job_type', 'work_location_type', 'location', 'is_active', 'created_at']
    list_filter = ['job_type', 'work_location_type', 'is_active', 'category', 'industry', 'created_at']
    search_fields = ['title', 'description', 'location', 'skills_required']
    list_editable = ['is_active']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'employer', 'category', 'industry')
        }),
        ('Job Details', {
            'fields': ('description', 'location', 'skills_required', 'experience_required')
        }),
        ('Job Type & Location', {
            'fields': ('job_type', 'work_location_type')
        }),
        ('Salary Information', {
            'fields': ('salary_min', 'salary_max', 'salary_display')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'job', 'status', 'applied_at']
    list_filter = ['status', 'applied_at', 'job__job_type', 'job__category']
    search_fields = ['applicant__full_name', 'applicant__user__email', 'job__title']
    readonly_fields = ['applied_at']
    
    fieldsets = (
        ('Application Details', {
            'fields': ('job', 'applicant', 'status', 'applied_at')
        }),
        ('Application Content', {
            'fields': ('cover_letter', 'resume')
        })
    )

@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ['job_seeker', 'job', 'saved_at']
    list_filter = ['saved_at']
    search_fields = ['job_seeker__full_name', 'job__title']
    readonly_fields = ['saved_at']

@admin.register(EmailNotification)
class EmailNotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notification_type', 'job_application', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['recipient__email', 'message']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('recipient', 'notification_type', 'job_application', 'is_read')
        }),
        ('Message Content', {
            'fields': ('message',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        })
    )

@admin.register(MessageThread)
class MessageThreadAdmin(admin.ModelAdmin):
    list_display = ['subject', 'job_application', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['subject']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['participants']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__email', 'recipient__email', 'subject', 'content']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Message Details', {
            'fields': ('sender', 'recipient', 'subject', 'is_read')
        }),
        ('Message Content', {
            'fields': ('content',)
        }),
        ('Related Objects', {
            'fields': ('job_application', 'message_thread')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        })
    )