# 💞 DriftDater

A full-stack dating web application built with **Vue 3** (frontend) and **Flask** (backend REST API).

---

## Team Members & Roles

| Name | Role |
|------|------|
| *Kira Hall* | Project Manager |
| *Antoine Stewart* | Backend Lead |
| *Chanchal Khiani* | Frontend Lead |
| *Daniel Graham* | QA / Testing Lead |
| *Carl Sharpe* | Deployment Lead |

---

## Features

### Core
- **Authentication** — Register, login, logout with JWT tokens and bcrypt password hashing
- **Profile Management** — Create and edit profiles with photo upload, bio, location, interests, occupation, education
- **Matching System** — Score-based algorithm (interests, age, location, gender preference), Like/Pass buttons, mutual match detection
- **Messaging** — Real-time (polled) chat between matched users with full message history
- **Search & Discovery** — Filter by name, parish, age range, interests with match score sorting
- **Favourites** — Bookmark profiles for later

### Optional (implemented)
1. **Report & Block System** — Report users for spam/harassment/fake profiles; block users from appearing in browse
2. **Admin Dashboard** — Site statistics, user management, report moderation (accessible to user ID #1)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue 3, Vue Router 4, Pinia, Axios, Vite |
| Backend | Flask 3, Flask-SQLAlchemy, Flask-Migrate, Flask-Login, Flask-CORS |
| Auth | JWT (PyJWT), bcrypt |
| Database | PostgreSQL (production) / SQLite (development) |
| Deployment | Render (backend + frontend) |

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (or use SQLite for local dev)

### 1. Clone the repository
```bash
git clone https://github.com/{username}/info3180-project.git
cd info3180-project
```

### 2. Backend setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
.\venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.sample .env
# Edit .env and set your DATABASE_URL and SECRET_KEY
```

### 3. Database setup
```bash
flask db init
flask db migrate -m "initial schema"
flask db upgrade

# Optional: seed sample data
python seed.py
```

### 4. Start the Flask API
```bash
flask --app app --debug run
# Runs on http://localhost:5000
```

### 5. Frontend setup (new terminal)
```bash
npm install
npm run dev
# Runs on http://localhost:5173
```

### 6. Open the app
Visit **https://info3180-project-1-4z3c.onrender.com/** in your browser

---

## Environment Variables

Copy `.env.sample` to `.env` and fill in:

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key for sessions/JWT | random string |
| `DATABASE_URL` | PostgreSQL connection string | SQLite fallback |
| `UPLOAD_FOLDER` | Directory for uploaded photos | `uploads/` |
| `JWT_EXPIRY_HOURS` | JWT token lifetime in hours | `24` |

---

## API Documentation

All endpoints are prefixed with `/api/v1/`.

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/login` | Login → returns JWT | No |
| POST | `/auth/logout` | Logout | Yes |

**Register body:**
```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "secret123",
  "first_name": "Alice",
  "last_name": "Wonder",
  "date_of_birth": "1999-03-15",
  "gender": "female",
  "looking_for": "any"
}
```

**Login body:**
```json
{ "email": "alice@example.com", "password": "secret123" }
```

**Login response:**
```json
{ "token": "<jwt>", "user": { "id": 1, "username": "alice", "email": "..." } }
```

> All protected endpoints require: `Authorization: Bearer <token>`

---

### Profiles

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/profiles` | Browse/search profiles (query params: `q`, `parish`, `age_min`, `age_max`, `gender`, `interests`, `sort`) |
| GET | `/profiles/<user_id>` | Get single profile |
| PUT | `/profiles/<user_id>` | Update own profile (multipart/form-data for photo) |

**Browse query params:**
- `q` — text search (name, bio, occupation)
- `parish` — filter by parish
- `age_min` / `age_max` — age range
- `gender` — filter by gender
- `interests` — comma-separated interest names
- `sort` — `match_score` (default) or `newest`

---

### Likes & Matching

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/profiles/<user_id>/like` | Like or pass. Body: `{ "action": "like" \| "pass" }`. Automatically creates a Match on mutual like. |
| GET | `/matches` | Get all mutual matches |

---

### Messaging

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/conversations` | List all conversations with latest message |
| GET | `/matches/<match_id>/messages` | Get message history |
| POST | `/matches/<match_id>/messages` | Send a message. Body: `{ "body": "Hello!" }` |

---

### Favourites

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/favourites` | List bookmarked profiles |
| POST | `/favourites/<profile_id>` | Bookmark a profile |
| DELETE | `/favourites/<profile_id>` | Remove bookmark |

---

### Report & Block

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/users/<user_id>/report` | Report a user. Body: `{ "reason": "spam\|harassment\|fake\|inappropriate\|other", "details": "..." }` |
| POST | `/users/<user_id>/block` | Block a user |
| DELETE | `/users/<user_id>/block` | Unblock a user |
| GET | `/blocks` | List blocked users |

---

### Admin (User ID #1 only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/stats` | Site-wide statistics |
| GET | `/admin/users` | List all users |
| DELETE | `/admin/users/<id>` | Delete a user |
| GET | `/admin/reports` | List reports (query: `?status=pending\|reviewed\|dismissed`) |
| PUT | `/admin/reports/<id>` | Update report status. Body: `{ "status": "reviewed\|dismissed" }` |

---

### Interests

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/interests` | List all available interests |

---

## Database Schema

### Tables
- **users** — Authentication (id, username, email, password_hash, created_at)
- **profiles** — Profile details (user_id FK, name, DOB, gender, bio, location, occupation, education, photo, preferences)
- **interests** — Reference table of interests/hobbies
- **profile_interests** — Many-to-many: profiles ↔ interests
- **likes** — Like/pass actions between users
- **matches** — Mutual likes (created automatically)
- **messages** — Chat messages within a match
- **favourites** — Bookmarked profiles
- **reports** — User reports for moderation
- **blocks** — Blocked user pairs

---

## Known Issues / Limitations

- Messaging uses 5-second polling (not WebSocket). For production, upgrade to Flask-SocketIO.
- Admin access is determined by user ID #1 — in production use a proper role system.
- Photo uploads are stored locally. For production, use S3 or Cloudinary.

---

## Deployment

Render utilized for deploypment of application on the web.

For the Flask backend, run `pip install -r requirements.txt` and then deploy the app with `gunicorn app:app`

For the Vue frontend, run `npm run build` and deploy the `dist/` folder as a static site on Render

