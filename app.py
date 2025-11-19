from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from werkzeug.security import generate_password_hash, check_password_hash
import os

#initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  #change this to a random secret key

#configure SQLAlchemy database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'enrollment.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#initialize database
db = SQLAlchemy(app)


#==================== Database Models ====================

class User(db.Model):
    """User model representing students, teachers, and admins"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  #'student', 'teacher', or 'admin'

    #relationships
    enrollments = db.relationship('Enrollment', backref='student', lazy=True, foreign_keys='Enrollment.student_id')

    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches the hash"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class Course(db.Model):
    """Course model representing a course offering"""
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

    #relationships
    instructor = db.relationship('User', foreign_keys=[teacher_id], backref='courses_taught')
    enrollments = db.relationship('Enrollment', backref='course', lazy=True, cascade='all, delete-orphan')

    def get_enrolled_count(self):
        """Get number of students enrolled in this course"""
        return len(self.enrollments)

    def is_full(self):
        """Check if course has reached capacity"""
        return self.get_enrolled_count() >= self.capacity

    def __repr__(self):
        return f'<Course {self.course_name}>'


class Enrollment(db.Model):
    """Enrollment model representing a student enrolled in a course"""
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    grade = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f'<Enrollment Student:{self.student_id} Course:{self.course_id}>'


#==================== Flask-Admin Setup ====================

#custom ModelView for admin panel
class SecureModelView(ModelView):
    """Secure model view that requires admin login"""
    def is_accessible(self):
        return session.get('role') == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


class UserAdmin(SecureModelView):
    """Admin view for User - only shows basic fields"""
    # Explicitly list only the fields we want in forms
    form_columns = ('username', 'full_name', 'role')
    column_list = ('username', 'full_name', 'role')
    column_exclude_list = ('password_hash',)

    def on_model_change(self, form, model, is_created):
        """Set default password for new users"""
        if is_created:
            model.set_password('password123')


class CourseAdmin(SecureModelView):
    """Admin view for Course with instructor selection"""
    column_list = ('course_name', 'instructor', 'time', 'capacity')

    # Display instructor's full name in the list view
    column_formatters = {
        'instructor': lambda v, c, m, p: m.instructor.full_name if m.instructor else 'No Instructor'
    }

    # Exclude teacher_id from column display but include in form
    form_columns = ('course_name', 'instructor', 'time', 'capacity')

    # Customize form args to filter teachers only
    form_args = {
        'instructor': {
            'label': 'Instructor',
            'query_factory': lambda: User.query.filter_by(role='teacher').all(),
            'get_label': 'full_name'
        }
    }


#initialize Flask-Admin
admin = Admin(app, name='ACME University Admin', template_mode='bootstrap3')
admin.add_view(UserAdmin(User, db.session))
admin.add_view(CourseAdmin(Course, db.session))
admin.add_view(SecureModelView(Enrollment, db.session))
# Add a logout link to the admin interface so admins can sign out easily
admin.add_link(MenuLink(name='Logout', url='/logout'))


#==================== Routes ====================

@app.route('/')
def index():
    """Redirect to appropriate dashboard or login"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    role = session.get('role')
    if role == 'student':
        return redirect(url_for('student_dashboard'))
    elif role == 'teacher':
        return redirect(url_for('teacher_dashboard'))
    elif role == 'admin':
        return redirect('/admin')

    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for all users"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['full_name'] = user.full_name
            session['role'] = user.role

            if request.is_json:
                return jsonify({
                    'success': True,
                    'role': user.role,
                    'redirect': url_for('student_dashboard') if user.role == 'student'
                               else url_for('teacher_dashboard') if user.role == 'teacher'
                               else '/admin'
                }), 200
            else:
                return redirect(url_for('index'))

        if request.is_json:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout current user"""
    session.clear()
    return redirect(url_for('login'))


@app.route('/student/dashboard')
def student_dashboard():
    """Student dashboard showing their courses and available courses"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('role') != 'student':
        return redirect(url_for('index'))

    user_id = session['user_id']

    #get student's enrolled courses
    enrollments = Enrollment.query.filter_by(student_id=user_id).all()
    my_courses = [{
        'id': e.course.id,
        'course_name': e.course.course_name,
        'teacher': e.course.instructor.full_name,
        'time': e.course.time,
        'enrolled': e.course.get_enrolled_count(),
        'capacity': e.course.capacity
    } for e in enrollments]

    #get all available courses
    all_courses = Course.query.all()
    enrolled_course_ids = [e.course_id for e in enrollments]

    available_courses = [{
        'id': c.id,
        'course_name': c.course_name,
        'teacher': c.instructor.full_name,
        'time': c.time,
        'enrolled': c.get_enrolled_count(),
        'capacity': c.capacity,
        'is_full': c.is_full(),
        'is_enrolled': c.id in enrolled_course_ids
    } for c in all_courses]

    return render_template('student_dashboard.html',
                         my_courses=my_courses,
                         available_courses=available_courses,
                         full_name=session['full_name'])


@app.route('/teacher/dashboard')
def teacher_dashboard():
    """Teacher dashboard showing their courses and enrolled students"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('role') != 'teacher':
        return redirect(url_for('index'))

    user_id = session['user_id']

    #get teacher's courses
    courses = Course.query.filter_by(teacher_id=user_id).all()

    courses_data = [{
        'id': c.id,
        'course_name': c.course_name,
        'teacher': c.instructor.full_name,
        'time': c.time,
        'enrolled': c.get_enrolled_count(),
        'capacity': c.capacity
    } for c in courses]

    return render_template('teacher_dashboard.html',
                         courses=courses_data,
                         full_name=session['full_name'])


@app.route('/teacher/course/<int:course_id>')
def teacher_course_detail(course_id):
    """View students and grades for a specific course"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('role') != 'teacher':
        return redirect(url_for('index'))

    course = Course.query.get_or_404(course_id)

    #ensure teacher owns this course
    if course.teacher_id != session['user_id']:
        return redirect(url_for('teacher_dashboard'))

    #get enrolled students
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()
    students = [{
        'enrollment_id': e.id,
        'student_name': e.student.full_name,
        'grade': e.grade
    } for e in enrollments]

    return render_template('teacher_course_detail.html',
                         course=course,
                         students=students,
                         full_name=session['full_name'])


#==================== Helper Functions ====================

def parse_time_slot(time_str):
    """
    Parse a time string like 'MWF 2:00-2:50 PM' or 'TR 11:00-11:50 AM'
    Returns: (days_set, start_minutes, end_minutes) or None if invalid
    """
    try:
        parts = time_str.strip().split()
        if len(parts) < 2:
            return None

        days_str = parts[0]
        time_range = ' '.join(parts[1:])

        # Parse days
        days = set()
        i = 0
        while i < len(days_str):
            if i + 1 < len(days_str) and days_str[i:i+2] in ['TR', 'Th']:
                days.add('R')  # Thursday
                i += 2
            elif days_str[i] in ['M', 'T', 'W', 'F']:
                days.add(days_str[i])
                i += 1
            else:
                i += 1

        # Parse time range (e.g., "2:00-2:50 PM" or "11:00-11:50 AM")
        if '-' not in time_range:
            return None

        times = time_range.split('-')
        start_time = times[0].strip()
        end_time_full = times[1].strip()

        # Determine AM/PM
        is_pm = 'PM' in end_time_full.upper()
        end_time = end_time_full.replace('AM', '').replace('PM', '').strip()

        # If start time doesn't have AM/PM, inherit from end time
        if 'AM' not in start_time.upper() and 'PM' not in start_time.upper():
            start_is_pm = is_pm
        else:
            start_is_pm = 'PM' in start_time.upper()
            start_time = start_time.replace('AM', '').replace('PM', '').strip()

        # Convert to minutes since midnight
        start_hour, start_min = map(int, start_time.split(':'))
        end_hour, end_min = map(int, end_time.split(':'))

        # Handle 12-hour format
        if start_is_pm and start_hour != 12:
            start_hour += 12
        elif not start_is_pm and start_hour == 12:
            start_hour = 0

        if is_pm and end_hour != 12:
            end_hour += 12
        elif not is_pm and end_hour == 12:
            end_hour = 0

        start_minutes = start_hour * 60 + start_min
        end_minutes = end_hour * 60 + end_min

        return (days, start_minutes, end_minutes)
    except:
        return None


def has_time_conflict(time1, time2):
    """
    Check if two course times conflict
    Returns True if there's a conflict, False otherwise
    """
    slot1 = parse_time_slot(time1)
    slot2 = parse_time_slot(time2)

    # If either time can't be parsed, assume no conflict (fail gracefully)
    if not slot1 or not slot2:
        return False

    days1, start1, end1 = slot1
    days2, start2, end2 = slot2

    # Check if they share any days
    if not days1.intersection(days2):
        return False

    # Check if times overlap (conflict if one starts before the other ends)
    return not (end1 <= start2 or end2 <= start1)


#==================== API Routes ====================

@app.route('/api/enroll', methods=['POST'])
def enroll_in_course():
    """Enroll a student in a course"""
    if 'user_id' not in session or session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 401

    # Handle both JSON and form data
    data = request.get_json() if request.is_json else request.form
    course_id = data.get('course_id')

    # Convert to int if it's a string
    try:
        course_id = int(course_id) if course_id else None
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid course ID'}), 400

    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404

    if course.is_full():
        return jsonify({'error': 'Course is full'}), 400

    #check if already enrolled
    existing = Enrollment.query.filter_by(
        student_id=session['user_id'],
        course_id=course_id
    ).first()

    if existing:
        return jsonify({'error': 'Already enrolled'}), 400

    #check for time conflicts with student's existing courses
    student_enrollments = Enrollment.query.filter_by(student_id=session['user_id']).all()
    for enrollment in student_enrollments:
        if has_time_conflict(course.time, enrollment.course.time):
            return jsonify({'error': f'Time conflict with {enrollment.course.course_name}'}), 400

    #create enrollment
    enrollment = Enrollment(student_id=session['user_id'], course_id=course_id)
    db.session.add(enrollment)
    db.session.commit()

    # Redirect for form submissions, JSON for API calls
    if request.is_json:
        return jsonify({'success': True, 'message': 'Enrolled successfully'}), 200
    else:
        return redirect(url_for('student_dashboard'))


@app.route('/api/unenroll', methods=['POST'])
def unenroll_from_course():
    """Unenroll a student from a course"""
    if 'user_id' not in session or session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 401

    # Handle both JSON and form data
    data = request.get_json() if request.is_json else request.form
    course_id = data.get('course_id')

    # Convert to int if it's a string
    try:
        course_id = int(course_id) if course_id else None
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid course ID'}), 400

    enrollment = Enrollment.query.filter_by(
        student_id=session['user_id'],
        course_id=course_id
    ).first()

    if not enrollment:
        return jsonify({'error': 'Not enrolled in this course'}), 404

    db.session.delete(enrollment)
    db.session.commit()

    # Redirect for form submissions, JSON for API calls
    if request.is_json:
        return jsonify({'success': True, 'message': 'Unenrolled successfully'}), 200
    else:
        return redirect(url_for('student_dashboard'))


@app.route('/api/update_grade', methods=['POST'])
def update_grade():
    """Update a student's grade (teachers only)"""
    if 'user_id' not in session or session.get('role') != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    enrollment_id = data.get('enrollment_id')
    new_grade = data.get('grade')

    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment:
        return jsonify({'error': 'Enrollment not found'}), 404

    #verify teacher owns this course
    if enrollment.course.teacher_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        enrollment.grade = float(new_grade)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Grade updated'}), 200
    except ValueError:
        return jsonify({'error': 'Invalid grade value'}), 400


if __name__ == '__main__':
    #create database tables
    with app.app_context():
        db.create_all()
        print("Database tables created!")

    app.run(debug=True, port=5001) #PORT LOCATION
