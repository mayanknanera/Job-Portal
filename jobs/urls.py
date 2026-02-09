from django.urls import path
from . import views

urlpatterns = [
    path('post/', views.job_create_view, name='job_create'),
    path('', views.job_list_view, name='job_list'),
    path('apply/<int:job_id>/', views.apply_job_view, name='apply_job'),
    path('applied/', views.applied_jobs_view, name='applied_jobs'),
    path('saved/', views.saved_jobs_view, name='saved_jobs'),
    path('save/<int:job_id>/', views.save_job_view, name='save_job'),
    path('is-saved/<int:job_id>/', views.is_job_saved_view, name='is_job_saved'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('view-applicants/<int:job_id>/', views.view_applicants_view, name='view_applicants'),
    path('update-status/<int:app_id>/<str:status>/', views.update_application_status, name='update_application_status'),
    path('download-resume/<int:application_id>/', views.download_resume, name='download_resume'),
    
    # Messaging URLs - MUST come before the slug pattern
    path('messages/', views.inbox_view, name='inbox'),
    path('messages/compose/', views.compose_message_view, name='compose_message'),
    path('messages/<int:thread_id>/', views.message_thread_view, name='message_thread'),
    path('messages/<int:thread_id>/send/', views.send_message_view, name='send_message'),
    path('messages/with-applicant/<int:application_id>/', views.message_with_applicant_view, name='message_with_applicant'),
    
    # Job detail slug pattern - MUST be last
    path('<slug:slug>/', views.job_detail_view, name='job_detail'),
]