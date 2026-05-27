from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


# ─── Custom User Manager ──────────────────────────────────────────────────────
# Handles how users are created in the database.
# We use email as the login identifier instead of a username.

class UserManager(BaseUserManager):

    def create_user(self, email, password=None, role=None):
        """Create and return a regular user with an email and password."""
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),  # lowercase the domain part
            role=role,
            is_active=True,
        )
        user.set_password(password)  # hashes the password before saving
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """Create and return a superuser (admin) with full permissions."""
        user = self.create_user(email=email, password=password, role='ADMIN')
        user.is_staff = True       # can access the admin panel
        user.is_superuser = True   # has all permissions
        user.save(using=self._db)
        return user


# ─── Custom User Model ────────────────────────────────────────────────────────
# Replaces Django's default User model.
# Every person on the site (admin, job seeker, employer) is a User.

class User(AbstractBaseUser, PermissionsMixin):

    # The three types of users on this platform
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('JOB_SEEKER', 'Job Seeker'),
        ('EMPLOYER', 'Employer'),
    )

    email             = models.EmailField(unique=True)
    role              = models.CharField(max_length=20, choices=ROLE_CHOICES, default='JOB_SEEKER')
    is_role_confirmed = models.BooleanField(default=False)  # True after user picks their role
    is_active         = models.BooleanField(default=True)   # False = account disabled
    is_staff          = models.BooleanField(default=False)  # True = can access admin panel
    date_joined       = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD  = 'email'   # use email to log in
    EMAIL_FIELD     = 'email'
    REQUIRED_FIELDS = []        # no extra fields required when creating a superuser

    # Some third-party packages expect a `username` attribute.
    # We map it to email so nothing breaks.
    @property
    def username(self):
        return self.email

    @username.setter
    def username(self, value):
        pass  # intentionally ignored

    def __str__(self):
        return self.email


# ─── Job Seeker Profile ───────────────────────────────────────────────────────
# Extra information for users who are looking for jobs.
# Created automatically when a user selects the JOB_SEEKER role.

class JobSeekerProfile(models.Model):
    user          = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name     = models.CharField(max_length=100)
    phone         = models.CharField(max_length=15, blank=True, null=True)
    skills        = models.TextField(blank=True, null=True)               # comma-separated, e.g. "Python, Django"
    experience    = models.CharField(max_length=5, blank=True, null=True, help_text="Years of experience")
    resume        = models.FileField(upload_to='resumes/', blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return self.full_name


# ─── Employer Profile ─────────────────────────────────────────────────────────
# Extra information for users who are posting jobs.
# Created automatically when a user selects the EMPLOYER role.

class EmployerProfile(models.Model):
    user                = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name        = models.CharField(max_length=150)
    company_description = models.TextField(blank=True, null=True)
    website             = models.URLField(blank=True, null=True)
    location            = models.CharField(max_length=100, blank=True, null=True)
    company_logo        = models.ImageField(upload_to='company_logos/', blank=True, null=True)

    def __str__(self):
        return self.company_name
