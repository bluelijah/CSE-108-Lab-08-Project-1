"""
Database initialization script for ACME University Enrollment System
This script creates sample users, courses, and enrollments matching the Excel data
"""

from app import app, db, User, Course, Enrollment

def init_database():
    """Initialize database with sample data from Excel file"""

    with app.app_context():
        #drop all tables and recreate them (fresh start)
        print("Dropping existing tables...")
        db.drop_all()

        print("Creating tables...")
        db.create_all()

        #create users (students, teachers, admin)
        print("Creating users...")

        #students - matching Excel data
        student1 = User(username='jsantos', full_name='Jose Santos', role='student')
        student1.set_password('password123')

        student2 = User(username='bbrown', full_name='Betty Brown', role='student')
        student2.set_password('password123')

        student3 = User(username='jstuart', full_name='John Stuart', role='student')
        student3.set_password('password123')

        student4 = User(username='lcheng', full_name='Li Cheng', role='student')
        student4.set_password('password123')

        student5 = User(username='nlittle', full_name='Nancy Little', role='student')
        student5.set_password('password123')

        student6 = User(username='mnorris', full_name='Mindy Norris', role='student')
        student6.set_password('password123')

        student7 = User(username='aranganath', full_name='Aditya Ranganath', role='student')
        student7.set_password('password123')

        student8 = User(username='ychen', full_name='Yi Wen Chen', role='student')
        student8.set_password('password123')

        #teachers
        teacher1 = User(username='ahepworth', full_name='Ammon Hepworth', role='teacher')
        teacher1.set_password('password123')

        teacher2 = User(username='swalker', full_name='Susan Walker', role='teacher')
        teacher2.set_password('password123')

        teacher3 = User(username='rjenkins', full_name='Ralph Jenkins', role='teacher')
        teacher3.set_password('password123')

        #admin
        admin = User(username='admin', full_name='System Administrator', role='admin')
        admin.set_password('admin123')

        #add all users to session
        db.session.add_all([
            student1, student2, student3, student4, student5, student6, student7, student8,
            teacher1, teacher2, teacher3, admin
        ])
        db.session.commit()

        #create courses - matching Excel data
        print("Creating courses...")

        course1 = Course(
            course_name='Math 101',
            teacher_id=teacher3.id,
            time='MWF 10:00-10:50 AM',
            capacity=8
        )

        course2 = Course(
            course_name='Physics 121',
            teacher_id=teacher2.id,
            time='TR 11:00-11:50 AM',
            capacity=10
        )

        course3 = Course(
            course_name='CS 106',
            teacher_id=teacher1.id,
            time='MWF 2:00-2:50 PM',
            capacity=10
        )

        course4 = Course(
            course_name='CS 162',
            teacher_id=teacher1.id,
            time='TR 3:00-3:50 PM',
            capacity=4
        )

        db.session.add_all([course1, course2, course3, course4])
        db.session.commit()

        #create enrollments - matching Excel data exactly
        print("Creating enrollments...")

        # Math 101 enrollments
        e1 = Enrollment(student_id=student1.id, course_id=course1.id, grade=92.0)  # Jose Santos
        e2 = Enrollment(student_id=student2.id, course_id=course1.id, grade=65.0)  # Betty Brown
        e3 = Enrollment(student_id=student3.id, course_id=course1.id, grade=86.0)  # John Stuart
        e4 = Enrollment(student_id=student4.id, course_id=course1.id, grade=77.0)  # Li Cheng

        # Physics 121 enrollments
        e5 = Enrollment(student_id=student5.id, course_id=course2.id, grade=53.0)  # Nancy Little
        e6 = Enrollment(student_id=student4.id, course_id=course2.id, grade=85.0)  # Li Cheng
        e7 = Enrollment(student_id=student6.id, course_id=course2.id, grade=94.0)  # Mindy Norris
        e8 = Enrollment(student_id=student3.id, course_id=course2.id, grade=91.0)  # John Stuart
        e9 = Enrollment(student_id=student2.id, course_id=course2.id, grade=88.0)  # Betty Brown

        # CS 106 enrollments
        e10 = Enrollment(student_id=student7.id, course_id=course3.id, grade=93.0)  # Aditya Ranganath
        e11 = Enrollment(student_id=student8.id, course_id=course3.id, grade=85.0)  # Yi Wen Chen
        e12 = Enrollment(student_id=student5.id, course_id=course3.id, grade=57.0)  # Nancy Little
        e13 = Enrollment(student_id=student6.id, course_id=course3.id, grade=68.0)  # Mindy Norris

        # CS 162 enrollments (at capacity 4/4)
        e14 = Enrollment(student_id=student7.id, course_id=course4.id, grade=99.0)  # Aditya Ranganath
        e15 = Enrollment(student_id=student5.id, course_id=course4.id, grade=87.0)  # Nancy Little
        e16 = Enrollment(student_id=student8.id, course_id=course4.id, grade=92.0)  # Yi Wen Chen
        e17 = Enrollment(student_id=student3.id, course_id=course4.id, grade=67.0)  # John Stuart

        db.session.add_all([
            e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
            e11, e12, e13, e14, e15, e16, e17
        ])
        db.session.commit()

        print("\n" + "="*60)
        print("Database initialized successfully!")
        print("="*60)
        print("\n📊 Data loaded from: Enrollment example data for Lab8-1.xlsx")
        print("\nSample login credentials:\n")
        print("STUDENTS:")
        print("  Username: jsantos    | Password: password123 (Jose Santos)")
        print("  Username: bbrown     | Password: password123 (Betty Brown)")
        print("  Username: jstuart    | Password: password123 (John Stuart)")
        print("  Username: lcheng     | Password: password123 (Li Cheng)")
        print("  Username: nlittle    | Password: password123 (Nancy Little)")
        print("  Username: mnorris    | Password: password123 (Mindy Norris)")
        print("  Username: aranganath | Password: password123 (Aditya Ranganath)")
        print("  Username: ychen      | Password: password123 (Yi Wen Chen)")
        print("\nTEACHERS:")
        print("  Username: ahepworth  | Password: password123 (Ammon Hepworth)")
        print("  Username: swalker    | Password: password123 (Susan Walker)")
        print("  Username: rjenkins   | Password: password123 (Ralph Jenkins)")
        print("\nADMIN:")
        print("  Username: admin      | Password: admin123")
        print("\nCOURSE ENROLLMENTS:")
        print("  Math 101:     4/8 students")
        print("  Physics 121:  5/10 students")
        print("  CS 106:       4/10 students")
        print("  CS 162:       4/4 students (FULL)")
        print("\nTo access admin panel, login as admin and navigate to /admin")
        print("="*60)

if __name__ == '__main__':
    init_database()
