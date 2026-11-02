"""Comprehensive test script for the Student Performance Analysis System."""
import requests
import sys

BASE = "http://127.0.0.1:5000"

results = []
session1 = requests.Session()
session2 = requests.Session()

def check(label, response, expected_status=200, expected_text=None):
    ok = response.status_code == expected_status
    if expected_text:
        ok = ok and expected_text.lower() in response.text.lower()
    status = "PASS" if ok else "FAIL"
    results.append((status, label, response.status_code, response.url))
    print(f"[{status}] {label}: HTTP {response.status_code} (expected {expected_status})")
    if not ok:
        print(f"       URL: {response.url}")
        if response.status_code >= 400:
            print(f"       Body snippet: {response.text[:300]}")
    return ok

# ─── 1. Register Student 1 ───────────────────────────────────────────────────
r = session1.post(f"{BASE}/register", data={
    'full_name': 'Arjun Sharma',
    'roll_number': 'TEST001',
    'age': '21',
    'dob': '2003-05-15',
    'gender': 'Male',
    'mobile_number': '9876543001',
    'email': 'arjun@test.com',
    'class_name': '3rd Year',
    'semester': '5',
    'course': 'B.Tech',
    'branch': 'Computer Science',
    'department': 'CSE',
    'graduation_year': '2025',
    'entered_cgpa': '8.5',
    'password': 'test1234',
}, allow_redirects=True)
check("Register Student 1 (TEST001)", r, 200)

# ─── 2. Register Student 2 ───────────────────────────────────────────────────
r = session2.post(f"{BASE}/register", data={
    'full_name': 'Priya Patel',
    'roll_number': 'TEST002',
    'age': '20',
    'dob': '2004-07-20',
    'gender': 'Female',
    'mobile_number': '9876543002',
    'email': 'priya@test.com',
    'class_name': '2nd Year',
    'semester': '3',
    'course': 'B.Tech',
    'branch': 'Electronics',
    'department': 'ECE',
    'graduation_year': '2026',
    'entered_cgpa': '9.1',
    'password': 'test1234',
}, allow_redirects=True)
check("Register Student 2 (TEST002)", r, 200)

# ─── 3. Duplicate Roll Number ─────────────────────────────────────────────────
r = session1.post(f"{BASE}/register", data={
    'full_name': 'Duplicate User',
    'roll_number': 'TEST001',  # same roll number
    'age': '22',
    'dob': '2002-01-01',
    'gender': 'Male',
    'mobile_number': '9999999001',
    'class_name': '4th Year',
    'semester': '7',
    'course': 'B.Tech',
    'branch': 'CSE',
    'department': 'CSE',
    'graduation_year': '2024',
    'password': 'test1234',
}, allow_redirects=True)
# Should return 200 with error message (not redirect to login)
check("Duplicate Roll Number (expect error page 200)", r, 200)
dup_ok = 'already registered' in r.text.lower() or 'roll number' in r.text.lower()
print(f"  -> Error message shown: {'YES' if dup_ok else 'NO (WARN)'}")

# ─── 4. Login with Roll Number ───────────────────────────────────────────────
r = session1.post(f"{BASE}/login", data={
    'identifier': 'TEST001',
    'password': 'test1234',
}, allow_redirects=True)
check("Login with Roll Number", r, 200)

# ─── 5. Dashboard ────────────────────────────────────────────────────────────
r = session1.get(f"{BASE}/dashboard", allow_redirects=True)
check("GET /dashboard", r, 200)

# ─── 6. Admin Dashboard ──────────────────────────────────────────────────────
r = session1.get(f"{BASE}/admin/dashboard", allow_redirects=True)
check("GET /admin/dashboard", r, 200)

# ─── 7. Rankings ─────────────────────────────────────────────────────────────
r = session1.get(f"{BASE}/rankings", allow_redirects=True)
check("GET /rankings", r, 200)

# ─── 8. Edit Profile (GET) ───────────────────────────────────────────────────
r = session1.get(f"{BASE}/edit-profile", allow_redirects=True)
check("GET /edit-profile", r, 200)

# ─── 9. VIP Dashboard via POST /vip-access ───────────────────────────────────
vip_session = requests.Session()
r = vip_session.post(f"{BASE}/vip-access", data={'vip_key': 'VIP'}, allow_redirects=True)
check("POST /vip-access (VIP key) -> /vip-dashboard", r, 200)

# ─── 10. Admin subpages ──────────────────────────────────────────────────────
for endpoint, label in [
    ("/admin/students",       "GET /admin/students"),
    ("/admin/subjects",       "GET /admin/subjects"),
    ("/admin/assessments",    "GET /admin/assessments"),
    ("/admin/marks",          "GET /admin/marks"),
    ("/admin/attendance",     "GET /admin/attendance"),
    ("/admin/class-analysis", "GET /admin/class-analysis"),
]:
    r = session1.get(f"{BASE}{endpoint}", allow_redirects=True)
    check(label, r, 200)

# ─── Summary ─────────────────────────────────────────────────────────────────
print("\n" + "="*60)
passed = sum(1 for s, *_ in results if s == "PASS")
total = len(results)
print(f"RESULTS: {passed}/{total} PASSED")
print("="*60)
for status, label, code, url in results:
    print(f"  [{status}] {label} → {code}")

sys.exit(0 if passed == total else 1)

