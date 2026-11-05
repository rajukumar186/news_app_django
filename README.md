# The People's Era

A Django-based news portal and admin dashboard with support chat, user authentication, promotions, weather, stock widgets, and a custom admin control panel.

## Overview

This project is a multi-feature web application for publishing news, managing promotional content, handling user ID cards, contact forms, stock/weather widgets, and a support chat flow between site users and admin.

The application is built with:
- Django 6.0
- PostgreSQL-ready configuration for production
- Redis-ready Channels for WebSocket chat support
- SQLite for local development
- Whitenoise for static file serving
- Django CSP for security headers
- Custom admin dashboard for superusers

## Features

- News homepage and article listing
- Weather page with caching
- Stocks dashboard with real-time-like data widgets
- User signup and authentication
- Password reset flow
- Contact form with OTP verification
- Promotion submission workflow
- ID card management and approval
- Custom admin dashboard
- Support chat between users and admin
- Live presence indicator for chat
- Security hardening for production deployment

## Tech Stack

- Python 3.11+
- Django 6.0.2
- Channels 4.x
- Redis (optional for production chat layer)
- PostgreSQL (recommended for production)
- SQLite (default for local development)
- Django Jazzmin
- Django CSP
- Django Anymail / Resend

## Project Structure

```text
news_app_django/
├── chat/
│   ├── consumers.py
│   ├── models.py
│   ├── routing.py
│   ├── templates/
│   ├── urls.py
│   └── views.py
├── main_app/
│   ├── templates/
│   ├── static/
│   ├── forms.py
│   ├── models.py
│   ├── views.py
│   └── ...
├── my_project/
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── .env.example
├── .gitignore
├── manage.py
├── requirements.txt
├── README.md
└── db.sqlite3   # local dev database
```

## Local Setup

### 1. Clone the repo

```bash
git clone https://github.com/rajukumar186/news_app_django.git
cd news_app_django
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create environment file

Copy the example file:

```bash
copy .env.example .env
```

Or on Linux/macOS:

```bash
cp .env.example .env
```

Update values in `.env` before running the app.

### 5. Run database migrations

```bash
python manage.py migrate
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

### 7. Run locally

For standard Django HTTP pages:

```bash
python manage.py runserver
```

For chat/WebSocket support, use an ASGI server:

```bash
python -m daphne my_project.asgi:application --bind 127.0.0.1 --port 8000
```

Or:

```bash
python -m uvicorn my_project.asgi:application --host 127.0.0.1 --port 8000
```

## Environment Variables

Use the following variables in `.env`:

```env
DEBUG=False
SECRET_KEY=your-long-random-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1,thepeoplesera.com,www.thepeoplesera.com
SITE_URL=https://thepeoplesera.com
CSRF_TRUSTED_ORIGINS=https://thepeoplesera.com,https://www.thepeoplesera.com
DATABASE_URL=postgres://user:password@host:5432/dbname
REDIS_URL=redis://127.0.0.1:6379/1
NEWS_API_KEY=
GNEWS_API_KEY=
GA_MEASUREMENT_ID=
DEFAULT_FROM_EMAIL=noreply@thepeoplesera.com
EMAIL_HOST=smtp.resend.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-resend-user
EMAIL_HOST_PASSWORD=your-resend-password
RESEND_API_KEY=your-resend-api-key
```

Notes:
- `DATABASE_URL` is used in production mode when `DEBUG=False`.
- `REDIS_URL` is used for production channel layer and caching.
- Never commit your real `.env` file to GitHub.

## Production Deployment

This project is prepared for production with:
- secure settings
- CSRF protection
- same-site cookies
- HTTPS support for domain deployment
- CSP headers
- Redis-ready Channels config
- Postgres-ready database config
- static file compression via WhiteNoise

### Recommended production services
- PostgreSQL
- Redis
- Email provider such as Resend
- Hosting provider such as Render, Railway, VPS, or similar

### Production launch example

```bash
export DEBUG=False
export SECRET_KEY=your-production-secret
export DATABASE_URL=postgres://user:password@host:5432/dbname
export REDIS_URL=redis://host:6379/1
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn my_project.wsgi:application
```

For WebSocket chat support in production, use an ASGI worker such as:

```bash
daphne my_project.asgi:application --bind 0.0.0.0 --port 8000
```

## Security Notes

The app includes:
- Django CSRF protection
- secure cookie settings
- HSTS headers
- no-sniff and referrer controls
- CSP directives
- admin-only access for protected views
- session expiration on browser close
- strong password hashing

## Chat Flow

The support chat supports:
- a user opening a support chat
- the user clicking a ping/admin notification
- admin receiving pending requests in the custom dashboard
- live messages between both sides
- presence/online status indicator

Important: the WebSocket route needs ASGI runtime. Do not run chat features using plain `manage.py runserver` in production or for tests relying on WebSockets.

## Common Commands

Create migrations:

```bash
python manage.py makemigrations
```

Apply migrations:

```bash
python manage.py migrate
```

Run checks:

```bash
python manage.py check
python manage.py check --deploy
```

Run tests:

```bash
python manage.py test
```

## GitHub

Before pushing:

```bash
git status
git add .
git commit -m "Prepare project for deployment"
git push origin main
```

## License

This project is for personal/project use and can be adjusted for production deployment based on your hosting and business requirements.

## Contact

Project domain: https://thepeoplesera.com
