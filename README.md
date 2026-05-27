# CareerPlus — Job Portal

A full-stack job portal built with Django, Tailwind CSS, and the Groq AI API.
Supports role-based authentication for job seekers and employers, Google OAuth login,
an AI-powered career assistant, email notifications, and analytics dashboards.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.x / Django 6 |
| Database | SQLite (dev) |
| Frontend | Tailwind CSS, vanilla JS |
| AI Chatbot | Groq API (LLaMA 3.1 8B) |
| Auth | django-allauth (email + Google OAuth) |

---

## Features

- **Authentication** — Email/password signup & login, Google OAuth, role selection (Job Seeker or Employer)
- **Job Seeker** — Browse & filter jobs, view job details, apply with resume, save jobs, track application status
- **Employer** — Post jobs, manage listings, view & filter applicants, accept/reject applications
- **Dashboards** — Analytics with charts for both roles (applications over time, status breakdown, top jobs)
- **Email Notifications** — Welcome email, application confirmation, status updates, new applicant alerts
- **AI Chatbot** — Career assistant powered by Groq / LLaMA 3.1 (resume tips, interview prep, job advice)
- **Admin Panel** — Full Django admin for managing users, jobs, categories, industries, and applications

---

## Project Structure

```
careerplus/
├── accounts/          # User model, auth views, dashboards, profiles
├── jobs/              # Job model, views, forms, email utils
├── chatbot/           # AI chatbot views and API
├── config/            # Django settings, URLs, WSGI
├── templates/         # Project-level HTML templates
├── theme/             # Tailwind CSS theme app
├── media/             # Uploaded files (resumes, logos, profile images)
├── logs/              # Application logs
├── .env               # Environment variables (not committed)
├── .env.example       # Template for environment variables
├── manage.py
├── requirements.txt
└── test_project.py    # Functional test suite (90 tests)
```

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/your-username/careerplus.git
cd careerplus
```

### 2. Create a virtual environment
```bash
python -m venv .venv

# Activate it:
.venv\Scripts\activate       # Windows
source .venv/bin/activate    # macOS / Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

GROQ_API_KEY=your-groq-api-key

# Google OAuth (optional — see below)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### 5. Run database migrations
```bash
python manage.py migrate
```

### 6. Create a superuser (admin account)
```bash
python manage.py createsuperuser
```

### 7. Run the development server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000`

---

## Google OAuth Setup (Optional)

To enable "Sign in with Google":

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project → **APIs & Services** → **Credentials** → **Create OAuth 2.0 Client ID**
3. Application type: **Web application**
4. Add to **Authorised redirect URIs**:
   ```
   http://127.0.0.1:8000/accounts/google/login/callback/
   ```
5. Copy the **Client ID** and **Client Secret** into your `.env`
6. Fix the default Site domain in the Django admin:
   - Go to `http://127.0.0.1:8000/admin/` → **Sites** → change `example.com` to `127.0.0.1:8000`

> If you skip this step, email/password login still works normally.

---

## Admin Panel

Access the Django admin at `http://127.0.0.1:8000/admin/`

From there you can manage:
- Users, Job Seeker Profiles, Employer Profiles
- Jobs, Job Categories, Industries
- Job Applications, Saved Jobs
- Social Accounts (Google OAuth)

---

## Running Tests

A functional test suite covers all major features (90 tests):

```bash
python test_project.py
```

Tests cover: URL resolution, public pages, auth redirects, signup, login/logout,
job seeker flow, employer flow, role-based access control, chatbot, database integrity,
pagination, and migrations.

---

## Test Credentials

Seeded test accounts are listed in `test_credentials.txt`.

| Role | Email | Password |
|---|---|---|
| Employer | employer1@techcorp.com | tech123 |
| Employer | employer2@innovate.com | innovate123 |
| Job Seeker | john.doe@email.com | john123 |
| Job Seeker | jane.smith@email.com | jane123 |

See `test_credentials.txt` for the full list.

---

## Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ | Django secret key |
| `DEBUG` | ✅ | `True` for development, `False` for production |
| `ALLOWED_HOSTS` | ✅ | Comma-separated list of allowed hostnames |
| `GROQ_API_KEY` | ✅ | API key for the AI chatbot ([groq.com](https://groq.com)) |
| `GOOGLE_CLIENT_ID` | ⬜ | Google OAuth client ID (optional) |
| `GOOGLE_CLIENT_SECRET` | ⬜ | Google OAuth client secret (optional) |
| `SITE_URL` | ⬜ | Base URL used in emails (default: `http://127.0.0.1:8000`) |
