import requests

base = 'http://127.0.0.1:5000'
s = requests.Session()

# 1) GET login page
r = s.get(f'{base}/login')
print(f'GET /login => {r.status_code}')

# 2) Register a test user
r = s.post(f'{base}/register', data={
    'full_name': 'Test Student',
    'age': '20',
    'dob': '2005-06-15',
    'class_name': '3rd Year',
    'semester': '5th',
    'course': 'B.Tech',
    'branch': 'CSE',
    'department': 'Computer Science',
    'graduation_year': '2027',
    'gender': 'Male',
    'mobile_number': '9876543210',
    'email': 'test@example.com',
    'student_id': 'STU001',
    'roll_number': 'R001',
    'entered_cgpa': '8.5',
    'password': 'password123',
}, allow_redirects=False)
loc = r.headers.get("Location", "")
print(f'POST /register => {r.status_code} Location: {loc}')

# 3) Login
r = s.post(f'{base}/login', data={
    'identifier': 'STU001',
    'password': 'password123',
}, allow_redirects=True)
print(f'POST /login => {r.status_code} URL: {r.url}')

# 4) Student dashboard
r = s.get(f'{base}/dashboard')
print(f'GET /dashboard => {r.status_code}')
assert r.status_code == 200, f'Dashboard FAILED with {r.status_code}'

# 5) Admin dashboard
r = s.get(f'{base}/admin/dashboard')
print(f'GET /admin/dashboard => {r.status_code}')
assert r.status_code == 200, f'Admin dashboard FAILED with {r.status_code}'

print()
print('=== ALL PAGES WORKING - NO 500 ERRORS ===')

