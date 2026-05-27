# 🎓 Student Management System — REST API

A production-style REST API backend built with **Flask**, **SQLAlchemy**, and **JWT Authentication**.

---

## 📁 Project Structure

```
student-management/
│
├── app.py              ← Main entry point — creates and runs the Flask app
├── config.py           ← All app settings (database URL, secret keys, JWT config)
├── models.py           ← Database models (User, Student) using SQLAlchemy ORM
├── requirements.txt    ← Python dependencies
├── .env.example        ← Template for environment variables
├── .gitignore          ← Files to exclude from Git
│
├── routes/
│   ├── __init__.py
│   ├── auth.py         ← Register, Login, Profile routes
│   └── students.py     ← Full CRUD + Search + Filter + Pagination
│
├── database/
│   └── database.db     ← SQLite database file (auto-created on first run)
│
└── utils/
    ├── __init__.py
    └── helpers.py      ← Reusable validation and response helpers
```

---

## ⚙️ Setup & Installation

### Step 1 — Clone or download the project

```bash
git clone https://github.com/yourusername/student-management.git
cd student-management
```

### Step 2 — Create a virtual environment

A virtual environment keeps your project's dependencies isolated from other Python projects.

```bash
# Create the virtual environment
python -m venv venv

# Activate it:
# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

You'll see `(venv)` in your terminal when it's active.

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Set up environment variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env and set your secret keys (any random string works for dev)
```

### Step 5 — Run the application

```bash
python app.py
```

You should see:
```
✅ Database tables created (or already exist)

=======================================================
  🎓 Student Management System API
=======================================================
  Server running at: http://127.0.0.1:5000
=======================================================
```

---

## 🔑 Authentication

This API uses **JWT (JSON Web Tokens)** for authentication.

**Flow:**
1. Register a user → `POST /api/auth/register`
2. Login → `POST /api/auth/login` → get a token
3. Use the token in all student requests: `Authorization: Bearer <your_token>`

---

## 📮 API Reference

### Auth Routes

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register a new user | No |
| POST | `/api/auth/login` | Login and get JWT token | No |
| GET | `/api/auth/me` | Get current user profile | ✅ Yes |

### Student Routes

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/students/` | Add a new student | ✅ Yes |
| GET | `/api/students/` | Get all students | ✅ Yes |
| GET | `/api/students/<id>` | Get student by ID | ✅ Yes |
| PUT | `/api/students/<id>` | Update student | ✅ Yes |
| DELETE | `/api/students/<id>` | Delete student | ✅ Yes |
| GET | `/api/students/courses` | List all courses | ✅ Yes |
| GET | `/api/students/stats` | Student statistics | ✅ Yes |

---

## 🔍 Search, Filter & Pagination

The `GET /api/students/` endpoint supports query parameters:

```
GET /api/students/?search=Alice&course=Python&min_age=18&max_age=25&page=1&per_page=5
```

| Parameter | Description | Example |
|-----------|-------------|---------|
| `search` | Search by name (partial match) | `search=ali` |
| `course` | Filter by course name | `course=Python` |
| `age` | Filter by exact age | `age=20` |
| `min_age` | Filter by minimum age | `min_age=18` |
| `max_age` | Filter by maximum age | `max_age=25` |
| `page` | Page number (default: 1) | `page=2` |
| `per_page` | Results per page (default: 10, max: 50) | `per_page=5` |

---

## 🧪 Postman Testing Guide

### 1. Register a User

```
POST http://127.0.0.1:5000/api/auth/register
Content-Type: application/json

{
    "username": "admin",
    "email": "admin@example.com",
    "password": "password123"
}
```

Expected Response (201):
```json
{
    "success": true,
    "message": "User registered successfully",
    "data": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "created_at": "2024-01-01T10:00:00"
    }
}
```

### 2. Login

```
POST http://127.0.0.1:5000/api/auth/login
Content-Type: application/json

{
    "username": "admin",
    "password": "password123"
}
```

Expected Response (200):
```json
{
    "success": true,
    "message": "Login successful",
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "Bearer",
        "user": { "id": 1, "username": "admin" }
    }
}
```

**Copy the `access_token`** — you'll use it in all student requests.

### 3. Add a Student

```
POST http://127.0.0.1:5000/api/students/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
    "name": "Alice Johnson",
    "age": 20,
    "course": "Python Development",
    "email": "alice@example.com"
}
```

### 4. Get All Students with Filters

```
GET http://127.0.0.1:5000/api/students/?course=Python&page=1&per_page=5
Authorization: Bearer <your_token>
```

### 5. Update a Student

```
PUT http://127.0.0.1:5000/api/students/1
Authorization: Bearer <your_token>
Content-Type: application/json

{
    "age": 21,
    "course": "Advanced Python"
}
```

### 6. Delete a Student

```
DELETE http://127.0.0.1:5000/api/students/1
Authorization: Bearer <your_token>
```

---

## 🚀 Deployment on Render

### Step 1 — Create a `render.yaml` file

```yaml
services:
  - type: web
    name: student-management-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:create_app()
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: student-db
          property: connectionString

databases:
  - name: student-db
    plan: free
```

### Step 2 — Add gunicorn to requirements.txt

```
gunicorn==21.2.0
```

### Step 3 — Push to GitHub and connect to Render

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Set environment variables in the Render dashboard
5. Deploy!

---

## 🐘 Switching to PostgreSQL

In `config.py`, change:
```python
# FROM (SQLite):
SQLALCHEMY_DATABASE_URI = f"sqlite:///{...}/database.db"

# TO (PostgreSQL):
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
```

Also add `psycopg2-binary` to `requirements.txt`:
```
psycopg2-binary==2.9.9
```

That's it! SQLAlchemy handles the rest — your model code stays the same.

---

## 📌 Suggested Git Commit Messages

```bash
git init
git add .
git commit -m "feat: initial project structure and Flask setup"

git add models.py
git commit -m "feat: add User and Student SQLAlchemy models"

git add routes/auth.py
git commit -m "feat: add user registration and login with JWT"

git add routes/students.py
git commit -m "feat: add Student CRUD routes with JWT protection"

git add utils/helpers.py
git commit -m "refactor: add validation helpers and standardized responses"

git commit -m "feat: add search, filter, and pagination to student listing"

git add README.md
git commit -m "docs: add comprehensive README with setup and API guide"
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Flask | Web framework |
| Flask-SQLAlchemy | ORM for database operations |
| Flask-JWT-Extended | JWT authentication |
| Werkzeug | Password hashing |
| SQLite | Development database |
| PostgreSQL | Production database (Render) |

---

## 📝 License

MIT License — free to use and modify.
