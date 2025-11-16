# Lab 8: Student Enrollment Web App

ACME University Student Enrollment System - A Flask web application for managing course enrollments.

## Features

### Student Features
- Log in/out of application
- View enrolled courses
- Browse all available courses
- See number of students enrolled in each course
- Enroll in new courses (if not at capacity)
- Drop courses

### Teacher Features
- Log in/out of application
- View all courses they teach
- See all students enrolled in each course
- View and edit student grades

### Admin Features
- Full CRUD operations on all database tables
- Manage users, courses, and enrollments via Flask-Admin interface

## Project Structure

```
CSE 108 - Lab 08 Project 1/
├── app.py                 #main Flask application
├── init_db.py             #database initialization script
├── requirements.txt       #python dependencies
├── venv/                  #virtual environment (created during setup)
├── enrollment.db          #sQLite database (created after init)
├── templates/             #HTML templates
│   ├── base.html
│   ├── login.html
│   ├── student_dashboard.html
│   ├── teacher_dashboard.html
│   └── teacher_course_detail.html
└── Lab 8.pdf              #assignment instructions
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
python3 -m venv venv
```

### 2. Activate Virtual Environment

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize the Database

```bash
python init_db.py
```

This will create the database and populate it with sample data.

### 5. Run the Application

```bash
python app.py
```

The application will be available at: `http://localhost:5001`
Login Page: http://localhost:5001/login
Admin Page: http://localhost:5001/admin

## Sample Login Credentials

### Students
- **Username:** `cnorris` | **Password:** `password123` (Chuck Norris)
- **Username:** `msherman` | **Password:** `password123` (Mindy Sherman)
- **Username:** `aranganath` | **Password:** `password123` (Aditya Ranganath)
- **Username:** `nlittle` | **Password:** `password123` (Nancy Little)
- **Username:** `ychen` | **Password:** `password123` (Yi Wen Chen)
- **Username:** `jstuart` | **Password:** `password123` (John Stuart)

### Teachers
- **Username:** `ahepworth` | **Password:** `password123` (Dr Hepworth)
- **Username:** `swalker` | **Password:** `password123` (Susan Walker)
- **Username:** `rjenkins` | **Password:** `password123` (Ralph Jenkins)

### Admin
- **Username:** `admin` | **Password:** `admin123`

To access the admin panel, login as admin and navigate to `/admin`

## Database Schema

### Users Table
- `id` (Primary Key)
- `username` (Unique)
- `password_hash`
- `full_name`
- `role` (student, teacher, or admin)

### Courses Table
- `id` (Primary Key)
- `course_name`
- `teacher_id` (Foreign Key to Users)
- `time`
- `capacity`

### Enrollments Table
- `id` (Primary Key)
- `student_id` (Foreign Key to Users)
- `course_id` (Foreign Key to Courses)
- `grade` (Default: 0.0)

## API Endpoints

### Authentication
- `GET /` - Redirects to appropriate dashboard based on role
- `GET/POST /login` - Login page
- `GET /logout` - Logout current user

### Student Routes
- `GET /student/dashboard` - Student dashboard with courses

### Teacher Routes
- `GET /teacher/dashboard` - Teacher dashboard
- `GET /teacher/course/<course_id>` - View course details and grades

### API Routes
- `POST /api/enroll` - Enroll student in a course
- `POST /api/unenroll` - Unenroll student from a course
- `POST /api/update_grade` - Update student grade (teachers only)

### Admin Routes
- `GET /admin` - Flask-Admin interface (admin only)

## Resetting the Database

To reset the database with fresh sample data:

```bash
python init_db.py
```

This will drop all existing data and recreate the tables with sample data.