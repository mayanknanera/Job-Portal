from django.contrib import admin
from .models import User, JobSeekerProfile, EmployerProfile


# ─── User ─────────────────────────────────────────────────────────────────────

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin view for all users (admins, job seekers, employers)."""
    list_display = ('email', 'role', 'is_staff', 'is_active')


# ─── Job Seeker Profile ───────────────────────────────────────────────────────

@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    """Admin view for job seeker profiles."""
    list_display = ('full_name', 'user', 'experience')


# ─── Employer Profile ─────────────────────────────────────────────────────────

@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    """Admin view for employer profiles."""
    list_display = ('company_name', 'user', 'location')
