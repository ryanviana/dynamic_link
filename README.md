# Dynamic Link - URL Shortener

![Python](https://img.shields.io/badge/Python-3-3776AB)
![Flask](https://img.shields.io/badge/Flask-3.0-000000)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57)

A lightweight URL shortener with click tracking, custom short codes, and a statistics dashboard. Built with Flask and SQLite.

## Features

- **URL Shortening** -- Generate random 6-character short codes or choose custom ones
- **Click Tracking** -- Automatic click counting on every redirect
- **Statistics Dashboard** -- Sortable, searchable, paginated table of all shortened URLs
- **Video Origin Tagging** -- Optional field to tag links by video or content source for campaign tracking
- **Custom Short Codes** -- Choose your own short code instead of a random one
- **URL Management** -- Delete shortened URLs from the stats page
- **Copy to Clipboard** -- One-click copy for generated short URLs

## Tech Stack

- **Backend:** Flask 3.0
- **Database:** SQLite via Flask-SQLAlchemy
- **Migrations:** Flask-Migrate (Alembic)
- **Validation:** validators
- **Templating:** Jinja2
- **Environment:** python-dotenv

## Getting Started

### Prerequisites

- Python 3.8+

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

Create a `.env` file:

```env
SECRET_KEY=your_secret_key
```

### Run

```bash
python app.py
```

The app starts on `http://localhost:5000`.

### Routes

| Route | Method | Description |
|---|---|---|
| `/` | GET/POST | Homepage -- shorten a URL |
| `/<short_id>` | GET | Redirect to original URL (increments click count) |
| `/stats` | GET | Statistics dashboard with sorting, search, and pagination |
| `/delete/<url_id>` | POST | Delete a shortened URL |
