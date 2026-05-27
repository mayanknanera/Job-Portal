from pathlib import Path
import os
from dotenv import load_dotenv

# ─── Base Setup ───────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from the .env file
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("Missing SECRET_KEY in environment")

DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Comma-separated list of allowed hostnames, e.g. "127.0.0.1,mysite.com"
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()]

# API key for the Groq AI chatbot
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# ─── Installed Apps ───────────────────────────────────────────────────────────

INSTALLED_APPS = [
    # Django built-ins
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",          # required by django-allauth

    # Our apps
    "accounts.apps.AccountsConfig",
    "jobs.apps.JobsConfig",
    "chatbot",

    # Third-party: Tailwind CSS
    "tailwind",
    "theme",
    "widget_tweaks",

    # Third-party: Google OAuth via django-allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
]


# ─── Middleware ───────────────────────────────────────────────────────────────

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",  # required by allauth
]

ROOT_URLCONF = "config.urls"


# ─── Templates ────────────────────────────────────────────────────────────────

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",        # project-level templates
            BASE_DIR / "theme" / "templates",  # Tailwind theme templates
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# ─── Database ─────────────────────────────────────────────────────────────────

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ─── Authentication ───────────────────────────────────────────────────────────

# Use our custom User model instead of Django's default
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Both standard login and Google OAuth are supported
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]


# ─── django-allauth Settings ──────────────────────────────────────────────────

SITE_ID = 1  # required by django.contrib.sites

# Use email (not username) to log in
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USER_MODEL_EMAIL_FIELD    = "email"
ACCOUNT_LOGIN_METHODS             = {"email"}
ACCOUNT_SIGNUP_FIELDS             = ["email*", "password1*", "password2*"]

ACCOUNT_EMAIL_VERIFICATION          = "mandatory"   # users must verify their email
ACCOUNT_UNIQUE_EMAIL                = True
ACCOUNT_RATE_LIMITS                 = {"login_failed": "5/5m"}  # max 5 failed logins per 5 minutes
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True   # log in automatically after verifying email
ACCOUNT_SESSION_REMEMBER            = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET     = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_EMAIL_SUBJECT_PREFIX        = "[CareerPlus] "

# ── Google OAuth ──────────────────────────────────────────────────────────────
SOCIALACCOUNT_LOGIN_ON_GET      = True   # skip the "confirm login" page
SOCIALACCOUNT_AUTO_SIGNUP       = True   # skip the extra allauth signup form
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"  # Google already verifies emails

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE":       ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        "VERIFIED_EMAIL": True,  # trust Google's email verification
    }
}

# Where to redirect after login / logout
LOGIN_REDIRECT_URL  = "check_role"
LOGOUT_REDIRECT_URL = "/"
LOGIN_URL           = "login"


# ─── Internationalisation ─────────────────────────────────────────────────────

LANGUAGE_CODE = "en-us"
TIME_ZONE     = "Asia/Kolkata"
USE_I18N      = True
USE_TZ        = True


# ─── Static & Media Files ─────────────────────────────────────────────────────

STATIC_URL       = "/static/"
STATIC_ROOT      = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "theme" / "static"]

MEDIA_URL  = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ─── Misc ─────────────────────────────────────────────────────────────────────

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Email: print to console in development; swap for SMTP in production
EMAIL_BACKEND    = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "CareerPlus <no-reply@careerplus.com>"

# Full base URL used when building links in emails
SITE_URL = os.getenv("SITE_URL", "http://127.0.0.1:8000")

# Tailwind CSS
TAILWIND_APP_NAME = "theme"
INTERNAL_IPS      = ["127.0.0.1"]
