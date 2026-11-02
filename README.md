# Student Performance Analysis System

A full-featured web application built with Python Flask for tracking student academic performance, attendance, rankings, and analytics.

## Features
- Student registration and login (by roll number, email, mobile, or student ID)
- Personalized dashboard with CGPA, rank, attendance, and marks
- Dense-rank leaderboard with tie handling (same CGPA = same rank)
- Admin panel: manage students, subjects, assessments, marks, attendance
- Class analysis: per-subject stats, CGPA distribution, top 10 performers
- VIP Demo Mode to preview the system without registering
- Beautiful UI: Bootstrap 5.3, Font Awesome 6, Inter font, animations

## Tech Stack
- **Backend**: Python 3.9+, Flask, SQLAlchemy
- **Database**: SQLite (dev) / PostgreSQL (production)
- **Frontend**: Bootstrap 5.3.2, Font Awesome 6.5.1, Inter (Google Fonts)

## Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd student-performance-system

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env
# Edit .env with your settings

# 5. Run the application
python app.py
# → http://localhost:5000
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `dev-secret-change-me` | Flask session secret key |
| `DATABASE_URL` | `sqlite:///student_performance.db` | SQLAlchemy DB URI |
| `VIP_ACCESS_KEY` | `VIP` | Key to access VIP demo dashboard |
| `ADMIN_PASSWORD` | `VIP420` | Admin account password |

## VIP Key Usage

On the login page, enter the VIP key (default: `VIP`) in the **VIP Demo Access** section to view a sample dashboard with demo data — no registration required.

## Ranking Algorithm

Rankings use **dense rank with tie handling**:
- Students are sorted by `entered_cgpa` descending.
- If two students share the same CGPA, they receive the same rank.
- The next distinct CGPA gets the next sequential rank (not skipped).
- Example: CGPA [9.5, 9.5, 8.0] → Ranks [1, 1, 3]

## Deploying to Render

1. Push code to GitHub.
2. Go to [render.com](https://render.com) → New → Web Service.
3. Connect your GitHub repository.
4. Set **Build Command**: `pip install -r requirements.txt`
5. Set **Start Command**: `gunicorn app:app`
6. Add environment variables:
   - `SECRET_KEY` → a long random string
   - `DATABASE_URL` → your PostgreSQL URL (from Render DB service)
   - `VIP_ACCESS_KEY` → your chosen key
   - `ADMIN_PASSWORD` → your chosen admin password
7. Deploy — Render handles the rest!

> **Note**: For PostgreSQL on Render, `psycopg2-binary` is already in `requirements.txt`.

