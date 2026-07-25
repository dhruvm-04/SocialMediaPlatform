# Social Media Platform — Django + MySQL

A minimal, interview-ready social media app: users, posts, likes, comments, and friendships.

## Tech stack
- Django 5.2 (LTS)
- MySQL (via `mysqlclient`)
- Plain HTML/CSS templates (no frontend framework)

## Features
- Register, login, logout (Django's built-in auth, using the built-in `User` model)
- Global feed — newest posts first
- Create, edit, delete posts
- Like / unlike posts
- Add comments
- Friendships — add / remove (no request/accept step, an add is immediate)
- Admin panel for `Friendship`, `Post`, `Comment`

## Project structure
```
social/
  models.py                             Friendship, Post, Comment
  views.py                              all app views
  forms.py                              SignupForm, PostForm, CommentForm
  urls.py                               app routes
  admin.py                              admin registrations
  management/commands/seed_demo.py      optional demo data seeder
templates/                              base.html + one template per screen
sm_platform/                            project settings & root urls.py
```

## First-time setup

### 1. Create and activate a virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install django django-environ mysqlclient
```

### 3. Create the MySQL database
```sql
CREATE DATABASE social_db CHARACTER SET utf8mb4;
```
(name must match `DB_NAME` in `.env` below)

### 4. Configure `.env`
A `.env` file already exists in the project root. Update it to match your local MySQL credentials:
```
DEBUG=True
SECRET_KEY=change-me
ALLOWED_HOSTS=127.0.0.1,localhost
DB_NAME=social_db
DB_USER=root
DB_PASSWORD=<your-mysql-password>
DB_HOST=localhost
DB_PORT=3306
```
Use a real random `SECRET_KEY` for anything beyond local testing.

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Create a superuser (for `/admin`)
```bash
python manage.py createsuperuser
```

### 7. (Optional) Seed some demo data
Creates a handful of users, posts, likes, comments, and friendships so the feed isn't empty:
```bash
python manage.py seed_demo
```
Options: `--users N` (default 6, max 6) and `--posts-per-user N` (default 2). All seeded users share the password `Password@123`.

### 8. Run the dev server
```bash
python manage.py runserver
```
- App: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

---
- If `python manage.py migrate` fails with a connection error, double check `.env` credentials and that `mysql -u root -p` connects successfully outside Django first.