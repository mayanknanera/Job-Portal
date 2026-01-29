from django.urls import path
from .views import signup_view, login_view, logout_view, jobseeker_dashboard, employer_dashboard

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/jobseeker/', jobseeker_dashboard, name='jobseeker_dashboard'),
    path('dashboard/employer/', employer_dashboard, name='employer_dashboard'),
]
