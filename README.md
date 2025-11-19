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

If port already in use: lsof -ti:5001 | xargs kill

This will create the database and populate it with sample data.

### 5. Run the Application

```bash
python app.py
```

The application will be available at: `http://localhost:5001`
Login Page: http://localhost:5001/login
Admin Page: http://localhost:5001/admin

## Sample Login Credentials

> **Note:** All sample data is loaded from `Enrollment example data for Lab8-1.xlsx`

### Students
| Username | Password | Full Name | Enrolled Courses |
|----------|----------|-----------|------------------|
| `jsantos` | `password123` | Jose Santos | Math 101 |
| `bbrown` | `password123` | Betty Brown | Math 101, Physics 121 |
| `jstuart` | `password123` | John Stuart | Math 101, Physics 121, CS 162 |
| `lcheng` | `password123` | Li Cheng | Math 101, Physics 121 |
| `nlittle` | `password123` | Nancy Little | Physics 121, CS 106, CS 162 |
| `mnorris` | `password123` | Mindy Norris | Physics 121, CS 106 |
| `aranganath` | `password123` | Aditya Ranganath | CS 106, CS 162 |
| `ychen` | `password123` | Yi Wen Chen | CS 106, CS 162 |

### Teachers
| Username | Password | Full Name | Courses Teaching |
|----------|----------|-----------|------------------|
| `ahepworth` | `password123` | Ammon Hepworth | CS 106, CS 162 |
| `swalker` | `password123` | Susan Walker | Physics 121 |
| `rjenkins` | `password123` | Ralph Jenkins | Math 101 |

### Admin
| Username | Password | Full Name | Access |
|----------|----------|-----------|--------|
| `admin` | `admin123` | System Administrator | Full CRUD access to all tables |

To access the admin panel, login as admin and navigate to `/admin`

## Course Enrollment Data

The database is initialized with the following courses and enrollments:

### Math 101
- **Teacher:** Ralph Jenkins
- **Time:** MWF 10:00-10:50 AM
- **Capacity:** 4/8 students
- **Enrolled Students:**
  - Jose Santos (Grade: 92)
  - Betty Brown (Grade: 65)
  - John Stuart (Grade: 86)
  - Li Cheng (Grade: 77)

### Physics 121
- **Teacher:** Susan Walker
- **Time:** TR 11:00-11:50 AM
- **Capacity:** 5/10 students
- **Enrolled Students:**
  - Nancy Little (Grade: 53)
  - Li Cheng (Grade: 85)
  - Mindy Norris (Grade: 94)
  - John Stuart (Grade: 91)
  - Betty Brown (Grade: 88)

### CS 106
- **Teacher:** Ammon Hepworth
- **Time:** MWF 2:00-2:50 PM
- **Capacity:** 4/10 students
- **Enrolled Students:**
  - Aditya Ranganath (Grade: 93)
  - Yi Wen Chen (Grade: 85)
  - Nancy Little (Grade: 57)
  - Mindy Norris (Grade: 68)

### CS 162
- **Teacher:** Ammon Hepworth
- **Time:** TR 3:00-3:50 PM
- **Capacity:** 4/4 students ⚠️ **FULL**
- **Enrolled Students:**
  - Aditya Ranganath (Grade: 99)
  - Nancy Little (Grade: 87)
  - Yi Wen Chen (Grade: 92)
  - John Stuart (Grade: 67)

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