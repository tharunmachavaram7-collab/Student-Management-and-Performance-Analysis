"""Automated verification of the separate Admin System and 9 tests."""

import requests

BASE = "http://127.0.0.1:5000"

print("=" * 60)
print("STARTING COMPLETE VERIFICATION OF ADMIN & STUDENT SYSTEM")
print("=" * 60)

# -------------------------------------------------------------
# Setup: Register a student for testing
# -------------------------------------------------------------
s_setup = requests.Session()
reg_data = {
    'full_name': 'Rohit Varma',
    'roll_number': '23CS101',
    'age': '20',
    'dob': '2004-06-15',
    'gender': 'Male',
    'mobile_number': '9123456780',
    'email': 'rohit@example.com',
    'class_name': '3rd Year',
    'semester': '5th',
    'course': 'B.Tech',
    'branch': 'CSE',
    'department': 'Computer Science',
    'graduation_year': '2026',
    'entered_cgpa': '8.20',
    'password': 'StudentPass123'
}
s_setup.post(f"{BASE}/register", data=reg_data)

# Register student 2 for ranking test
reg_data2 = {
    'full_name': 'Sneha Rao',
    'roll_number': '23CS102',
    'age': '20',
    'dob': '2004-09-10',
    'gender': 'Female',
    'mobile_number': '9123456781',
    'email': 'sneha@example.com',
    'class_name': '3rd Year',
    'semester': '5th',
    'course': 'B.Tech',
    'branch': 'CSE',
    'department': 'Computer Science',
    'graduation_year': '2026',
    'entered_cgpa': '9.10',
    'password': 'StudentPass123'
}
s_setup.post(f"{BASE}/register", data=reg_data2)

# -------------------------------------------------------------
# TEST 1: Login as Kowshika / VIP on /admin/login
# Expected: Admin Dashboard
# -------------------------------------------------------------
admin_session = requests.Session()
r1 = admin_session.post(f"{BASE}/admin/login", data={'name': 'Kowshika', 'password': 'VIP'}, allow_redirects=True)
test1_pass = r1.status_code == 200 and 'admin/dashboard' in r1.url and 'ADMIN DASHBOARD' in r1.text and 'Kowshika' in r1.text
print(f"TEST 1 (Admin Login: Kowshika + VIP -> Admin Dashboard): {'PASS' if test1_pass else 'FAIL'} [HTTP {r1.status_code}, URL: {r1.url}]")

# -------------------------------------------------------------
# TEST 2: Login as registered student on /login
# Expected: Student Dashboard (NOT Admin Dashboard)
# -------------------------------------------------------------
student_session = requests.Session()
r2 = student_session.post(f"{BASE}/login", data={'identifier': '23CS101', 'password': 'StudentPass123'}, allow_redirects=True)
test2_pass = r2.status_code == 200 and 'dashboard' in r2.url and 'admin' not in r2.url and 'STUDENT DASHBOARD' in r2.text
print(f"TEST 2 (Student Login: 23CS101 -> Student Dashboard): {'PASS' if test2_pass else 'FAIL'} [HTTP {r2.status_code}, URL: {r2.url}]")

# -------------------------------------------------------------
# TEST 3: While logged in as a student, manually open /admin
# Expected: Access Denied / redirect to Student Dashboard
# -------------------------------------------------------------
r3 = student_session.get(f"{BASE}/admin", allow_redirects=True)
test3_pass = 'dashboard' in r3.url and ('Access Denied' in r3.text or 'access denied' in r3.text.lower())
print(f"TEST 3 (Student visits /admin -> Access Denied): {'PASS' if test3_pass else 'FAIL'} [URL: {r3.url}]")

# -------------------------------------------------------------
# TEST 4: Student visits /admin/students, /admin/subjects, /admin/marks, /admin/attendance
# Expected: Access Denied for all admin routes
# -------------------------------------------------------------
admin_routes = ['students', 'subjects', 'assessments', 'marks', 'attendance', 'class-analysis']
test4_pass = True
for route in admin_routes:
    r_check = student_session.get(f"{BASE}/admin/{route}", allow_redirects=True)
    if not ('dashboard' in r_check.url and ('Access Denied' in r_check.text or 'access denied' in r_check.text.lower())):
        test4_pass = False
print(f"TEST 4 (Student blocked from all /admin/* routes): {'PASS' if test4_pass else 'FAIL'}")

# -------------------------------------------------------------
# TEST 5: Logout and try to access an admin page (/admin/dashboard)
# Expected: Redirect to Admin Login (/admin/login)
# -------------------------------------------------------------
guest_session = requests.Session()
r5 = guest_session.get(f"{BASE}/admin/dashboard", allow_redirects=True)
test5_pass = 'admin/login' in r5.url and r5.status_code == 200
print(f"TEST 5 (Logged-out user visits /admin/dashboard -> Redirect to /admin/login): {'PASS' if test5_pass else 'FAIL'} [URL: {r5.url}]")

# -------------------------------------------------------------
# TEST 6: Login with incorrect Admin password on /admin/login
# Expected: Invalid administrator credentials
# -------------------------------------------------------------
r6 = guest_session.post(f"{BASE}/admin/login", data={'name': 'Kowshika', 'password': 'WRONGPASSWORD'}, allow_redirects=True)
test6_pass = 'Invalid administrator credentials' in r6.text and 'admin/dashboard' not in r6.url
print(f"TEST 6 (Wrong Admin Password -> 'Invalid administrator credentials'): {'PASS' if test6_pass else 'FAIL'}")

# -------------------------------------------------------------
# TEST 7: Login with normal student credentials on /admin/login
# Expected: Access denied
# -------------------------------------------------------------
r7 = guest_session.post(f"{BASE}/admin/login", data={'name': '23CS101', 'password': 'StudentPass123'}, allow_redirects=True)
test7_pass = ('Access denied' in r7.text or 'access denied' in r7.text.lower()) and 'admin/dashboard' not in r7.url
print(f"TEST 7 (Student on Admin Login -> 'Access denied'): {'PASS' if test7_pass else 'FAIL'}")

# -------------------------------------------------------------
# TEST 8: Update student information in profile
# Expected: Database updated and reflected immediately
# -------------------------------------------------------------
r8_edit = student_session.post(f"{BASE}/edit-profile", data={
    'full_name': 'Rohit K. Varma',
    'age': '21',
    'dob': '2004-06-15',
    'gender': 'Male',
    'mobile_number': '9123456780',
    'email': 'rohit.k@example.com',
    'class_name': 'Final Year',
    'semester': '6th',
    'course': 'B.Tech',
    'branch': 'CSE',
    'department': 'Computer Science',
    'graduation_year': '2026',
    'entered_cgpa': '8.40'
}, allow_redirects=True)
test8_pass = 'Rohit K. Varma' in r8_edit.text and '8.4' in r8_edit.text and 'Final Year' in r8_edit.text
print(f"TEST 8 (Edit profile updates DB and displays immediately): {'PASS' if test8_pass else 'FAIL'}")

# -------------------------------------------------------------
# TEST 9: Change student CGPA and verify ranking updates
# Expected: Database updated and ranking updates automatically
# -------------------------------------------------------------
# Sneha currently has 9.10. Rohit was 8.40 (Rank 2).
# Let's change Rohit's CGPA to 9.50 -> Rohit must become Rank 1!
student_session.post(f"{BASE}/edit-profile", data={
    'full_name': 'Rohit K. Varma',
    'age': '21',
    'dob': '2004-06-15',
    'gender': 'Male',
    'mobile_number': '9123456780',
    'email': 'rohit.k@example.com',
    'class_name': 'Final Year',
    'semester': '6th',
    'course': 'B.Tech',
    'branch': 'CSE',
    'department': 'Computer Science',
    'graduation_year': '2026',
    'entered_cgpa': '9.50'
}, allow_redirects=True)

r9_rankings = student_session.get(f"{BASE}/rankings")
test9_pass = '#1' in r9_rankings.text and '9.5' in r9_rankings.text
print(f"TEST 9 (CGPA update to 9.50 -> Rank 1 auto-updates): {'PASS' if test9_pass else 'FAIL'}")

print("=" * 60)
all_tests = [test1_pass, test2_pass, test3_pass, test4_pass, test5_pass, test6_pass, test7_pass, test8_pass, test9_pass]
print(f"FINAL RESULT: {sum(all_tests)}/9 TESTS PASSED")
print("=" * 60)
