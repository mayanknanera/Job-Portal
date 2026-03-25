# CareerPlus — Job Portal

A full-stack job portal built with Django, PostgreSQL, and Tailwind CSS. Features role-based auth for job seekers and employers, AI-powered career assistant, email notifications, and analytics dashboards.

## Tech Stack

- Python / Django
- PostgreSQL
- Tailwind CSS
- Groq API (LLaMA 3.1)
- django-allauth (Google OAuth)

## Features

- Email-based authentication + Google OAuth
- Job seeker & employer dashboards with analytics
- Job posting, filtering, and search
- Apply with resume, track application status
- Save jobs, email notifications
- AI career assistant chatbot (Groq / LLaMA)

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/your-username/careerplus.git
cd careerplus
```

**2. Create virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment**
```bash
cp .env.example .env
# Fill in your values in .env
```

**5. Set up the database**
```bash
python manage.py migrate
python manage.py createsuperuser
```

**6. Run the server**
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000`
