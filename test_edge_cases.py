"""
Comprehensive Edge Case Testing for ACME University Enrollment System
Tests all required functionality and edge cases from Lab 8 requirements
"""

import requests
import json

BASE_URL = "http://localhost:5001"

class TestSession:
    """Helper class to maintain session cookies"""
    def __init__(self):
        self.session = requests.Session()
        self.cookies = {}

    def login(self, username, password):
        """Login and store session"""
        response = self.session.post(
            f"{BASE_URL}/login",
            data={"username": username, "password": password},
            allow_redirects=False
        )
        return response

    def get(self, path):
        """GET request with session"""
        return self.session.get(f"{BASE_URL}{path}")

    def post(self, path, data):
        """POST request with session"""
        return self.session.post(
            f"{BASE_URL}{path}",
            json=data,
            headers={"Content-Type": "application/json"}
        )

    def logout(self):
        """Logout"""
        return self.session.get(f"{BASE_URL}/logout")


def print_test(test_name):
    """Print test header"""
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print(f"{'='*70}")


def print_result(passed, message):
    """Print test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status}: {message}")
    return passed


def test_student_login():
    """Test 1: Student can log in"""
    print_test("Student Login")
    session = TestSession()
    response = session.login("cnorris", "password123")

    passed = response.status_code in [200, 302]
    print_result(passed, f"Student login - Status: {response.status_code}")
    return passed


def test_invalid_login():
    """Test 2: Invalid credentials are rejected"""
    print_test("Invalid Login Credentials")
    session = TestSession()

    # Wrong password
    response = session.login("cnorris", "wrongpassword")
    passed1 = response.status_code in [200, 401]
    print_result(passed1, f"Wrong password rejected - Status: {response.status_code}")

    # Non-existent user
    response = session.login("nonexistent", "password")
    passed2 = response.status_code in [200, 401]
    print_result(passed2, f"Non-existent user rejected - Status: {response.status_code}")

    return passed1 and passed2


def test_student_view_courses():
    """Test 3: Student can see their enrolled courses"""
    print_test("Student View Enrolled Courses")
    session = TestSession()
    session.login("cnorris", "password123")

    response = session.get("/student/dashboard")
    passed = response.status_code == 200 and "Physics 121" in response.text
    print_result(passed, f"Can view enrolled courses - Status: {response.status_code}")

    # Verify sees enrollment count
    passed2 = "Students" in response.text or "Enrolled" in response.text
    print_result(passed2, "Can see enrollment counts")

    return passed and passed2


def test_student_enroll_available_course():
    """Test 4: Student can enroll in available course (not at capacity)"""
    print_test("Student Enroll in Available Course")
    session = TestSession()
    session.login("msherman", "password123")

    # Try to enroll in Physics 121 (has capacity)
    response = session.post("/api/enroll", {"course_id": 1})
    passed = response.status_code == 200

    try:
        data = response.json()
        success = data.get("success", False)
        print_result(passed and success, f"Enrolled in available course - {data}")
    except:
        print_result(passed, f"Enrolled - Status: {response.status_code}")

    return passed


def test_student_cannot_enroll_full_course():
    """Test 5: Student cannot enroll in full course"""
    print_test("Student Cannot Enroll in Full Course")
    session = TestSession()
    session.login("cnorris", "password123")

    # CS 162 is full (4/4 capacity)
    response = session.post("/api/enroll", {"course_id": 4})

    try:
        data = response.json()
        is_error = "error" in data or not data.get("success", True)
        print_result(is_error, f"Full course enrollment blocked - {data}")
        return is_error
    except:
        passed = response.status_code in [400, 403]
        print_result(passed, f"Full course blocked - Status: {response.status_code}")
        return passed


def test_student_cannot_double_enroll():
    """Test 6: Student cannot enroll in same course twice"""
    print_test("Student Cannot Double Enroll")
    session = TestSession()
    session.login("cnorris", "password123")

    # Try to enroll in Physics 121 (already enrolled)
    response = session.post("/api/enroll", {"course_id": 1})

    try:
        data = response.json()
        is_error = "error" in data or not data.get("success", True)
        print_result(is_error, f"Double enrollment blocked - {data}")
        return is_error
    except:
        passed = response.status_code == 400
        print_result(passed, f"Double enrollment blocked - Status: {response.status_code}")
        return passed


def test_student_drop_course():
    """Test 7: Student can drop a course"""
    print_test("Student Drop Course")
    session = TestSession()
    session.login("cnorris", "password123")

    # Drop CS 106
    response = session.post("/api/unenroll", {"course_id": 2})

    try:
        data = response.json()
        success = data.get("success", False)
        print_result(success, f"Course dropped successfully - {data}")
        return success
    except:
        passed = response.status_code == 200
        print_result(passed, f"Course dropped - Status: {response.status_code}")
        return passed


def test_teacher_login():
    """Test 8: Teacher can log in"""
    print_test("Teacher Login")
    session = TestSession()
    response = session.login("ahepworth", "password123")

    passed = response.status_code in [200, 302]
    print_result(passed, f"Teacher login - Status: {response.status_code}")
    return passed


def test_teacher_view_courses():
    """Test 9: Teacher can see their courses"""
    print_test("Teacher View Their Courses")
    session = TestSession()
    session.login("ahepworth", "password123")

    response = session.get("/teacher/dashboard")
    passed = response.status_code == 200 and "CS 106" in response.text
    print_result(passed, "Can view assigned courses")

    # Check if CS 162 is also visible
    passed2 = "CS 162" in response.text
    print_result(passed2, "All teacher's courses visible")

    return passed and passed2


def test_teacher_view_enrolled_students():
    """Test 10: Teacher can see students in their courses"""
    print_test("Teacher View Enrolled Students")
    session = TestSession()
    session.login("ahepworth", "password123")

    # View CS 162 course details
    response = session.get("/teacher/course/4")
    passed = response.status_code == 200
    print_result(passed, f"Can view course details - Status: {response.status_code}")

    # Check if students are listed
    has_students = "Aditya Ranganath" in response.text
    print_result(has_students, "Can see enrolled students")

    return passed and has_students


def test_teacher_update_grade():
    """Test 11: Teacher can update student grade"""
    print_test("Teacher Update Grade")
    session = TestSession()
    session.login("ahepworth", "password123")

    # Update grade for enrollment_id 10 (Aditya in CS 162)
    response = session.post("/api/update_grade", {
        "enrollment_id": 10,
        "grade": 95.5
    })

    try:
        data = response.json()
        success = data.get("success", False)
        print_result(success, f"Grade updated - {data}")
        return success
    except:
        passed = response.status_code == 200
        print_result(passed, f"Grade updated - Status: {response.status_code}")
        return passed


def test_teacher_invalid_grade():
    """Test 12: Teacher cannot set invalid grade"""
    print_test("Teacher Invalid Grade Values")
    session = TestSession()
    session.login("ahepworth", "password123")

    # Try invalid grade (non-numeric)
    response = session.post("/api/update_grade", {
        "enrollment_id": 10,
        "grade": "abc"
    })

    is_error = response.status_code == 400
    print_result(is_error, f"Non-numeric grade rejected - Status: {response.status_code}")

    return is_error


def test_teacher_cannot_edit_other_course():
    """Test 13: Teacher cannot edit grades for courses they don't teach"""
    print_test("Teacher Cannot Edit Other Teacher's Grades")
    session = TestSession()
    session.login("ahepworth", "password123")

    # Try to update grade in Physics 121 (taught by Susan Walker)
    # Enrollment ID 1 is Chuck in Physics 121
    response = session.post("/api/update_grade", {
        "enrollment_id": 1,
        "grade": 100
    })

    is_forbidden = response.status_code in [403, 401]
    print_result(is_forbidden, f"Cross-teacher grade edit blocked - Status: {response.status_code}")

    return is_forbidden


def test_admin_login():
    """Test 14: Admin can log in"""
    print_test("Admin Login")
    session = TestSession()
    response = session.login("admin", "admin123")

    passed = response.status_code in [200, 302]
    print_result(passed, f"Admin login - Status: {response.status_code}")
    return passed


def test_admin_access():
    """Test 15: Admin can access admin panel"""
    print_test("Admin Panel Access")
    session = TestSession()
    session.login("admin", "admin123")

    response = session.get("/admin")
    passed = response.status_code == 200 and "Admin" in response.text
    print_result(passed, f"Admin panel accessible - Status: {response.status_code}")

    return passed


def test_student_cannot_access_admin():
    """Test 16: Student cannot access admin panel"""
    print_test("Student Cannot Access Admin Panel")
    session = TestSession()
    session.login("cnorris", "password123")

    response = session.get("/admin")
    is_blocked = response.status_code in [302, 403, 401]
    print_result(is_blocked, f"Student blocked from admin - Status: {response.status_code}")

    return is_blocked


def test_unauthorized_api_access():
    """Test 17: Unauthorized users cannot use API endpoints"""
    print_test("Unauthorized API Access Blocked")
    session = TestSession()

    # Try to enroll without login
    response = session.post("/api/enroll", {"course_id": 1})
    blocked1 = response.status_code in [401, 302]
    print_result(blocked1, f"Enroll blocked without auth - Status: {response.status_code}")

    # Try to update grade without login
    response = session.post("/api/update_grade", {"enrollment_id": 1, "grade": 100})
    blocked2 = response.status_code in [401, 302]
    print_result(blocked2, f"Grade update blocked without auth - Status: {response.status_code}")

    return blocked1 and blocked2


def test_student_cannot_access_teacher_pages():
    """Test 18: Role-based access control"""
    print_test("Student Cannot Access Teacher Pages")
    session = TestSession()
    session.login("cnorris", "password123")

    response = session.get("/teacher/dashboard")
    is_blocked = response.status_code in [302, 403, 401]
    print_result(is_blocked, f"Student blocked from teacher dashboard - Status: {response.status_code}")

    return is_blocked


def test_logout():
    """Test 19: Logout functionality"""
    print_test("Logout Functionality")
    session = TestSession()
    session.login("cnorris", "password123")

    # Access dashboard (should work)
    response1 = session.get("/student/dashboard")
    logged_in = response1.status_code == 200

    # Logout
    session.logout()

    # Try to access dashboard (should redirect)
    response2 = session.get("/student/dashboard")
    logged_out = response2.status_code in [302, 401]

    print_result(logged_in and logged_out, f"Logout works correctly")

    return logged_in and logged_out


def test_capacity_enforcement():
    """Test 20: Course capacity is enforced correctly"""
    print_test("Course Capacity Enforcement")
    session = TestSession()
    session.login("jstuart", "password123")

    # View available courses - CS 162 should show as full
    response = session.get("/student/dashboard")

    # Try to enroll in full course
    enroll_response = session.post("/api/enroll", {"course_id": 4})

    try:
        data = enroll_response.json()
        is_blocked = "error" in data or "full" in data.get("error", "").lower()
        print_result(is_blocked, f"Full course enrollment prevented - {data}")
        return is_blocked
    except:
        is_blocked = enroll_response.status_code in [400, 403]
        print_result(is_blocked, f"Capacity enforced - Status: {enroll_response.status_code}")
        return is_blocked


def run_all_tests():
    """Run all edge case tests"""
    print("\n" + "="*70)
    print("ACME UNIVERSITY ENROLLMENT SYSTEM - COMPREHENSIVE EDGE CASE TESTING")
    print("="*70)

    results = []

    # Authentication Tests
    results.append(("Student Login", test_student_login()))
    results.append(("Invalid Login", test_invalid_login()))
    results.append(("Teacher Login", test_teacher_login()))
    results.append(("Admin Login", test_admin_login()))
    results.append(("Logout", test_logout()))

    # Student Functionality Tests
    results.append(("Student View Courses", test_student_view_courses()))
    results.append(("Student Enroll Available", test_student_enroll_available_course()))
    results.append(("Student Cannot Enroll Full", test_student_cannot_enroll_full_course()))
    results.append(("Student Cannot Double Enroll", test_student_cannot_double_enroll()))
    results.append(("Student Drop Course", test_student_drop_course()))
    results.append(("Capacity Enforcement", test_capacity_enforcement()))

    # Teacher Functionality Tests
    results.append(("Teacher View Courses", test_teacher_view_courses()))
    results.append(("Teacher View Students", test_teacher_view_enrolled_students()))
    results.append(("Teacher Update Grade", test_teacher_update_grade()))
    results.append(("Teacher Invalid Grade", test_teacher_invalid_grade()))
    results.append(("Teacher Cross-Course Block", test_teacher_cannot_edit_other_course()))

    # Admin Tests
    results.append(("Admin Access", test_admin_access()))

    # Security Tests
    results.append(("Student No Admin Access", test_student_cannot_access_admin()))
    results.append(("Student No Teacher Access", test_student_cannot_access_teacher_pages()))
    results.append(("Unauthorized API Block", test_unauthorized_api_access()))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\n{'='*70}")
    print(f"TOTAL: {passed}/{total} tests passed ({100*passed//total}%)")
    print(f"{'='*70}\n")

    return passed == total


if __name__ == "__main__":
    try:
        all_passed = run_all_tests()
        exit(0 if all_passed else 1)
    except Exception as e:
        print(f"\n✗ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
