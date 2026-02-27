# COSME Project – Vehicle Booking & Movement Tracker

A simple internal web application for the **COSME Project** to track vehicle bookings, movements, and avoid scheduling conflicts.

## Features

- **User Authentication & Roles** – admin, driver, requester roles with login/register
- **Vehicle Management** – add, edit, track vehicle status (available/in-use/maintenance)
- **Booking System** – request bookings, admin approval, automatic conflict detection
- **Driver Assignment** – assign drivers to approved bookings
- **Trip Tracking** – record actual start/end times, odometer readings, fuel usage
- **Maintenance Scheduling** – schedule, complete, or cancel vehicle maintenance
- **Fuel Cost & Budget Reports** – per-vehicle trip reports and project-code budget summaries
- **Excel Export** – download styled `.xlsx` trip reports
- **Calendar View** – visual calendar of all bookings (FullCalendar.js)
- **Email Notifications** – optional email alerts on booking approval and driver assignment
- **Comprehensive Validation** – server-side + client-side form validation

## Tech Stack

- **Backend:** Python 3.13, Flask, Flask-SQLAlchemy, Flask-Login, Flask-Mail
- **Database:** SQLite (auto-created on first run)
- **Frontend:** Bootstrap 5.3, Bootstrap Icons, FullCalendar.js (all via CDN)
- **Export:** openpyxl for Excel generation
- **Production:** Gunicorn WSGI server

## Quick Start (Local)

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/cosme-vehicle-tracker.git
cd cosme-vehicle-tracker

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Open **http://127.0.0.1:5000** and login with:
- Username: `admin`
- Password: `admin123`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `cosme-dev-secret-key` | Flask secret key (change in production!) |
| `DATABASE_URL` | `sqlite:///tracker.db` | Database connection string |
| `PORT` | `5000` | Server port |
| `FLASK_DEBUG` | `1` | Set to `0` in production |
| `MAIL_ENABLED` | `0` | Set to `1` to enable email notifications |
| `MAIL_SERVER` | `smtp.gmail.com` | SMTP server |
| `MAIL_PORT` | `587` | SMTP port |
| `MAIL_USERNAME` | _(empty)_ | SMTP username |
| `MAIL_PASSWORD` | _(empty)_ | SMTP password |
| `MAIL_DEFAULT_SENDER` | `noreply@cosme-project.org` | From address |

## Deployment

This app is configured for one-click deployment on **Render** (free tier):

1. Push to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Render auto-detects the `Procfile` and `requirements.txt`
5. Add environment variable: `SECRET_KEY` = _(a random string)_
6. Deploy!

## License

Internal use – COSME Project.
