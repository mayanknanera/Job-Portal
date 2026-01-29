from django.urls import path
from .views import (
    job_create_view, job_list_view, 
    apply_job_view, view_applicants_view, 
    update_application_status, applied_jobs_view,
    job_detail_view
)


urlpatterns = [
    path('post/', job_create_view, name='post_job'),
    path('list/', job_list_view, name='job_list'),
    path('apply/<int:job_id>/', apply_job_view, name='apply_job'),
    path('applicants/<int:job_id>/', view_applicants_view, name='view_applicants'),
    path('update-status/<int:app_id>/<str:status>/', update_application_status, name='update_application_status'),
    path('applied/', applied_jobs_view, name='applied_jobs'),
    path('<slug:slug>/', job_detail_view, name='job_detail'),

]
