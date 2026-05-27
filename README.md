# CareerPlus — Job Portal

A full-stack job portal where employers can post jobs and job seekers can apply — built with Django and Tailwind CSS.

---

## What it does

**For Job Seekers**
- Sign up, pick a role, complete your profile
- Browse and filter jobs by keyword, location, skills, salary, job type, and more
- Save jobs for later, apply with your resume, track application status
- AI career assistant for resume tips and interview prep

**For Employers**
- Post job listings with category, industry, salary, and work type
- View and manage applicants, accept or reject with one click
- Dashboard with application analytics and charts

**General**
- Email + Google OAuth login
- Email notifications (welcome, application confirmation, status updates)
- Django admin panel for full data management

---

## Tech Stack

- **Backend** — Python / Django
- **Database** — SQLite
- **Frontend** — Tailwind CSS
- **AI Chatbot** — Groq API (LLaMA 3.1)
- **Auth** — django-allauth (email + Google OAuth)

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/mayanknanera/Job-Portal.git
cd Job-Portal

# 2. Virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Environment variables
cp .env.example .env
# Fill in SECRET_KEY and GROQ_API_KEY in .env

# 5. Database
python manage.py migrate
python manage.py createsuperuser

# 6. Run
python manage.py runserver
```

Open `http://127.0.0.1:8000`

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ | Django secret key |
| `DEBUG` | ✅ | `True` for development |
| `ALLOWED_HOSTS` | ✅ | e.g. `127.0.0.1,localhost` |
| `GROQ_API_KEY` | ✅ | From [groq.com](https://groq.com) |
| `GOOGLE_CLIENT_ID` | ⬜ | For Google OAuth (optional) |
| `GOOGLE_CLIENT_SECRET` | ⬜ | For Google OAuth (optional) |
