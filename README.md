# Social Media Platform – Django + MySQL

A minimal social media platform with users, posts, friendships, likes, comments, and notifications.

## Tech stack
- Django 4.2 LTS (Python 3.9 compatible)
- MySQL (via PyMySQL driver)
- HTML/CSS (Bootstrap)

## Features
- Register, login/logout (Django auth)
- User profiles (extends Django User via Profile)
- Posts: create, edit, delete, list
- Likes: toggle per post
- Comments: add, delete (by author or post owner)
- Friendships: request and accept
- Admin panel to manage all entities

## Setup (Windows / PowerShell)

1. Create an `.env` file from the example and update MySQL credentials:

```
cp .env.example .env
```

Edit `.env`:
```
DEBUG=True
SECRET_KEY=change-me
ALLOWED_HOSTS=[]
DB_ENGINE=mysql
DB_NAME=social_db
DB_USER=social_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

2. Create the MySQL database and user (example):

```sql
CREATE DATABASE social_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'social_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON social_db.* TO 'social_user'@'localhost';
FLUSH PRIVILEGES;
```

3. Install dependencies (already installed by the workspace):
- Django 4.2, django-environ, PyMySQL

4. Run migrations and create a superuser:

```
# Make migrations for the social app
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

5. Start the server:

```
python manage.py runserver
```

Open http://127.0.0.1:8000/ and login/register.

Admin at http://127.0.0.1:8000/admin/

## Notes
- If `.env` has `DB_ENGINE=mysql`, Django uses MySQL via PyMySQL; otherwise it falls back to SQLite (file path in `DB_NAME`).
- On Windows, PyMySQL avoids the need for compiling `mysqlclient`.
- The minimal UI is Bootstrap-based and intentionally simple.
