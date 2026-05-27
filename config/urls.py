from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from jobs.views import home_view

# ─── Project URL Configuration ────────────────────────────────────────────────

urlpatterns = [
    # Homepage
    path("", home_view, name="home"),

    # Django admin panel
    path("admin/", admin.site.urls),

    # Our apps
    path("accounts/", include("accounts.urls")),   # login, signup, dashboards
    path("jobs/",     include("jobs.urls")),        # job listing, apply, etc.
    path("",          include("chatbot.urls")),     # AI chatbot

    # django-allauth routes (Google OAuth, email verification, password reset, etc.)
    path("accounts/", include("allauth.urls")),
]

# Serve uploaded media files (profile images, resumes, logos) in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
