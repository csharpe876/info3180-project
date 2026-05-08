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
- **Profile Management** — Create and edit profiles with photo upload (Cloudinary in production, local disk in dev), bio, location, interests, occupation, and education level
- **Account Settings** — Update username, email address, and password from the profile page
- **Matching System** — Score-based algorithm (interests, age, location, gender preference), Like/Pass buttons, mutual match detection
- **Messaging** — Polled real-time chat between matched users with full conversation history
- **Search & Discovery** — Filter by name, parish, age range, interests, and gender with match score sorting
- **Favourites** — Bookmark profiles for later
- **Flash Notifications** — Global toast message system for success, error, and info feedback across all pages

### Optional (implemented)
1. **Report & Block System** — Report users for spam/harassment/fake profiles; block users from appearing in browse
2. **Admin Dashboard** — Site statistics, user management, and report moderation (accessible to user ID #1)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue 3, Vue Router 4, Pinia, Axios, Vite |
| Backend | Flask 3, Flask-SQLAlchemy, Flask-Migrate, Flask-Login, Flask-CORS |
| Auth | JWT (PyJWT), bcrypt |
| Database | PostgreSQL (production) / SQLite (development) |
| Storage | Cloudinary (production) / local `uploads/` folder (development) |
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
# Edit .env and set your DATABASE_URL, SECRET_KEY, and optional Cloudinary credentials
```

### 3. Database setup
```bash
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
Visit **http://localhost:5173** in your browser (dev), or **https://info3180-project-dt4x.onrender.com/** for the live deployment.

---

## Environment Variables

Copy `.env.sample` to `.env` and fill in:

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key for sessions/JWT | random string |
| `DATABASE_URL` | PostgreSQL connection string | SQLite fallback |
| `UPLOAD_FOLDER` | Directory for uploaded photos (dev only) | `uploads/` |
| `JWT_EXPIRY_HOURS` | JWT token lifetime in hours | `24` |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name (production) | — |
| `CLOUDINARY_API_KEY` | Cloudinary API key (production) | — |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret (production) | — |

When `CLOUDINARY_CLOUD_NAME` is set, photo uploads are sent to Cloudinary. Otherwise photos are saved to `UPLOAD_FOLDER` on disk.

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

### Account Settings

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| PUT | `/users/<user_id>/account` | Update username, email, or password | Yes (own account only) |

**Body:**
```json
{
  "username": "new_username",
  "email": "new@example.com",
  "current_password": "oldpass123",
  "new_password": "newpass456",
  "confirm_password": "newpass456"
}
```

- `current_password` is **required** when changing `email` or `new_password`.
- All fields are optional — only include the ones you want to change.

---

### Profiles

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/profiles` | Browse/search profiles (query params: `q`, `parish`, `age_min`, `age_max`, `gender`, `interests`, `sort`) |
| GET | `/profiles/<user_id>` | Get single profile |
| PUT | `/profiles/<user_id>` | Update own profile (multipart/form-data for photo upload, or JSON) |

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

## Frontend Structure

```
src/
├── App.vue                  # Root component — mounts global FlashMessage
├── main.js
├── router/index.js          # Vue Router (guarded routes)
├── stores/
│   ├── auth.js              # Pinia: JWT token, user, login/register/logout
│   ├── profile.js           # Pinia: cached own profile
│   └── flash.js             # Pinia: global toast notification queue
├── services/api.js          # Axios client with JWT interceptor
├── components/
│   ├── AppNav.vue
│   ├── AppHeader.vue
│   ├── AppFooter.vue
│   └── FlashMessage.vue     # Fixed-position toast container
└── views/
    ├── LoginView.vue
    ├── RegisterView.vue
    ├── DashboardView.vue    # Browse + like/pass + bookmark + report
    ├── ProfileView.vue      # Edit profile + account settings
    ├── MatchesView.vue
    ├── MessagesView.vue
    ├── FavouritesView.vue
    └── AdminView.vue
```

---

## Known Issues / Limitations

- Messaging uses 4-second polling (not WebSocket). For production, consider upgrading to Flask-SocketIO.
- Admin access is determined by user ID #1 — in production use a proper role/permission system.
- Photo uploads fall back to local disk in development; set Cloudinary credentials for persistent storage in production.

---

## Deployment

The application is deployed on **Render**.

**Backend:** `gunicorn app:app` — set all environment variables in the Render service dashboard.

**Frontend:** `npm run build` — deploy the `dist/` folder as a Render Static Site with the rewrite rule `/* → /index.html`.


---

