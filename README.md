# CareerPlus — Job Portal

A full-stack job portal where employers can post jobs and job seekers can apply — built with Django and Tailwind CSS.

---

## What it does

**For Job Seekers**
- Browse and filter jobs, save for later, apply with resume
- Track application status from dashboard
- AI career assistant for resume tips and interview prep

**For Employers**
- Post job listings with category, industry, salary, and work type
- View applicants, accept or reject with one click
- Dashboard with application analytics

**General**
- Email + Google OAuth login
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
git clone https://github.com/mayanknanera/Job-Portal.git
cd Job-Portal

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt

cp .env.example .env
# Fill in SECRET_KEY and GROQ_API_KEY in .env

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000`

---

## Email Notifications

The project sends 4 emails:

| Trigger | Recipient |
|---|---|
| New user signs up | Welcome email → user |
| Job seeker applies | Confirmation → seeker, Alert → employer |
| Employer accepts/rejects | Status update → seeker |

> **Note:** Emails currently print to the terminal (console backend).
> To send real emails, update `EMAIL_BACKEND` in `settings.py` with your SMTP credentials.

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
