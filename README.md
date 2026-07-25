# UTT-registration

A Flask web application for **participant registration, ticketing, and gate-level attendance tracking** at a festival — built for *Učiaca sa Trnava* (UTT), an education festival in Trnava, Slovakia.

Beyond issuing tickets, the system was designed for the COVID-19 era: gate controllers scan each attendee's QR code to validate their ticket for a specific workshop/talk **and** record which person passed through which gate. If a participant later tested positive, organizers could instantly identify and email everyone who shared a session with them and advise them to get tested.

> The interface and all participant emails are in Slovak.

## What it does

The app is split into three role-based interfaces, each a separate Flask blueprint:

| Interface | Blueprint / prefix | Used by | Purpose |
| --- | --- | --- | --- |
| **Participant** | `user` → `/user` | Attendees | Sign in, confirm registration, view their personal schedule of booked sessions, send feedback |
| **Gate controller** | `admin` → `/admin` | Staff at gates | Scan a participant's QR code, validate their ticket for the current session, and record their attendance; look up attendees, register walk-ups |
| **Organizer** | `head_admin` → `/head-admin` | Event managers | Create and edit program items, bulk-import registrations from Excel, manage controller accounts, and view per-session attendance statistics |

### QR scanning & attendance

Each participant has a unique `code` (a generated hash) encoded as their QR. When a controller opens a session's scan page and scans a code, the app resolves the hash to the participant, checks their ticket for that session, and marks them present. Presence is stored as a link between the participant and the session, so at any moment the organizer can see exactly who attended which workshop or talk.

### Contact tracing

Because every attendance is tied to a specific session, the organizer interface can pull the full list of people who attended a given session and trigger a mass email to all of them — the mechanism used to notify participants exposed to a positive case, or to announce a program change.

## Tech stack

- **Backend:** Python, [Flask](https://flask.palletsprojects.com/) 2.0 with blueprints
- **Auth:** Flask-Login (role separation via `rank` on admin accounts), Flask-WTF CSRF protection, hardened session cookies
- **Database:** SQLAlchemy (scoped session) on MySQL via PyMySQL, with a commented-out SQLite fallback for local use
- **Email:** Flask-Mail (SMTP), sent asynchronously on background threads
- **Data import:** pandas + openpyxl for bulk registration from Excel spreadsheets
- **Serving:** Gunicorn

## Data model

- **User** — a participant: profile details, email-confirmation flag, unique QR `code`, and the set of sessions they're booked into / present at
- **Admin** — a staff account; `rank` distinguishes gate controllers from head organizers
- **TicketType** — a single program item (workshop/talk): name, speaker, start/end time, capacity
- **TicketTypeType** — a grouping of program items (e.g. *Workshop I. blok*, *Workshop II. blok*, *Ďaľší program*)
- **Ticket** — a booking linking a participant to a program item
- **FeedBackMessages** — messages submitted through the participant interface

## Project structure

```
UTT-registration/
├── __init__.py           # App factory: config, blueprints, mail, login, contact-tracing routes
├── database.py           # SQLAlchemy engine + session
├── models.py             # User, Admin, Ticket, TicketType, TicketTypeType, FeedBackMessages
├── run_script.py         # Initialize the DB and seed sample data
├── gunicorn_config.py    # Production server config
├── requirements.txt
├── blueprints/
│   ├── user/             # Participant interface
│   ├── admin/            # Gate controller / scanner interface
│   └── head_admin/       # Organizer interface
├── templates/            # Jinja2 templates (incl. email templates)
└── static/               # CSS, JS (QR scanning), assets
```

## Running locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure the database and secrets (see Configuration below)

# 3. Initialize the database and seed sample data
python run_script.py

# 4. Run
#    Development:
flask run
#    Production:
gunicorn -c gunicorn_config.py __init__:app
```

For local development you can switch `database.py` to the SQLite engine (the commented line) instead of MySQL.

## Configuration

The database connection string and SMTP credentials should be supplied through **environment variables**, not committed to source. At minimum:

- `SECRET_KEY` — Flask session signing key
- Database URL (MySQL connection string, or SQLite for local development)
- Mail server, username, and password for the SMTP account

> **Note:** This repository dates from the original 2021 deployment and contains hardcoded credentials in `database.py` and `__init__.py`. Anyone reusing this code should remove those, rotate the affected secrets, and load them from the environment instead.

## Status

Built and deployed for a live event. Published here as an archive of the project; not actively maintained.
