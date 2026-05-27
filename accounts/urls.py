from django.urls import path
from .views import (
    signup_view,
    login_view,
    logout_view,
    jobseeker_dashboard,
    employer_dashboard,
    edit_profile,
    select_role,
    check_role,
    analytics_dashboard,
)

# ─── Account URL Patterns ─────────────────────────────────────────────────────
# All routes are prefixed with /accounts/ (set in config/urls.py)

urlpatterns = [
    # Auth
    path('signup/',  signup_view,  name='signup'),
    path('login/',   login_view,   name='login'),
    path('logout/',  logout_view,  name='logout'),

    # Dashboards
    path('dashboard/jobseeker/', jobseeker_dashboard, name='jobseeker_dashboard'),
    path('dashboard/employer/',  employer_dashboard,  name='employer_dashboard'),
    path('analytics/',           analytics_dashboard, name='analytics_dashboard'),

    # Profile
    path('profile/edit/', edit_profile, name='edit_profile'),

    # Role setup (shown once after signup)
    path('select-role/', select_role, name='select_role'),
    path('check-role/',  check_role,  name='check_role'),
]
