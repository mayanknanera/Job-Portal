from django.urls import path
from . import views

# ─── Jobs URL Patterns ────────────────────────────────────────────────────────
# All routes are prefixed with /jobs/ (set in config/urls.py)

urlpatterns = [
    # Job listing & detail
    path('',       views.job_list_view,   name='job_list'),
    path('post/',  views.job_create_view, name='job_create'),

    # Job seeker actions
    path('apply/<int:job_id>/',    views.apply_job_view,   name='apply_job'),
    path('applied/',               views.applied_jobs_view, name='applied_jobs'),
    path('saved/',                 views.saved_jobs_view,   name='saved_jobs'),
    path('save/<int:job_id>/',     views.save_job_view,     name='save_job'),
    path('is-saved/<int:job_id>/', views.is_job_saved_view, name='is_job_saved'),

    # Employer actions
    path('my-jobs/',                                        views.employer_jobs_view,         name='employer_jobs'),
    path('all-applicants/',                                 views.all_applicants_view,         name='all_applicants'),
    path('view-applicants/<int:job_id>/',                   views.view_applicants_view,        name='view_applicants'),
    path('update-status/<int:app_id>/<str:status>/',        views.update_application_status,   name='update_application_status'),
    path('download-resume/<int:application_id>/',           views.download_resume,             name='download_resume'),

    # Job detail by slug — MUST be last to avoid matching other paths
    path('<slug:slug>/', views.job_detail_view, name='job_detail'),
]
