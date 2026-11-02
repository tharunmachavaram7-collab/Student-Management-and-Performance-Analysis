# routes/auth.py
"""Authentication routes — register, login, student dashboard, rankings, vip, logout."""

from datetime import datetime
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, session, current_app)
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models.student import Student, Attendance, Mark, Subject

bp = Blueprint('auth', __name__)


# ─── helpers ────────────────────────────────────────────────────────────────

def get_grade(cgpa):
    if cgpa is None:
        return 'N/A'
    if cgpa >= 9:
        return 'A+'
    if cgpa >= 8:
        return 'A'
    if cgpa >= 7:
        return 'B+'
    if cgpa >= 6:
        return 'B'
    if cgpa >= 5:
        return 'C'
    return 'D'


# ─── index ──────────────────────────────────────────────────────────────────

@bp.route('/')
def index():
    if current_user.is_authenticated:
        if getattr(current_user, 'role', None) == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('auth.dashboard'))
    return redirect(url_for('auth.login'))


# ─── register ───────────────────────────────────────────────────────────────

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        roll_number = data.get('roll_number', '').strip()

        # Validate roll_number uniqueness
        if not roll_number:
            flash('Roll Number is required.', 'danger')
            return render_template('register.html')

        existing = Student.query.filter_by(roll_number=roll_number).first()
        if existing:
            flash('Roll number already exists. Please use a different roll number.', 'danger')
            return render_template('register.html')

        try:
            cgpa_raw = data.get('entered_cgpa', '').strip()
            cgpa_val = None
            if cgpa_raw:
                cgpa_val = float(cgpa_raw)
                if not (0 <= cgpa_val <= 10):
                    flash('CGPA must be between 0 and 10.', 'danger')
                    return render_template('register.html')

            dob_raw = data.get('dob', '').strip()
            dob_val = datetime.strptime(dob_raw, '%Y-%m-%d').date() if dob_raw else None

            age_raw = data.get('age', '').strip()
            age_val = int(age_raw) if age_raw else None

            grad_raw = data.get('graduation_year', '').strip()
            grad_val = int(grad_raw) if grad_raw else None

            # Auto-generate student_id if not provided
            student_id_raw = data.get('student_id', '').strip()
            if not student_id_raw:
                import uuid
                student_id_raw = 'STU' + str(uuid.uuid4().hex[:7].upper())

            # Registered users are always role='student'
            student = Student(
                full_name=data.get('full_name', '').strip(),
                roll_number=roll_number,
                role='student',
                is_admin=False,
                age=age_val,
                dob=dob_val,
                class_name=data.get('class_name', '').strip() or None,
                semester=data.get('semester', '').strip() or None,
                course=data.get('course', '').strip() or None,
                branch=data.get('branch', '').strip() or None,
                department=data.get('department', '').strip() or None,
                graduation_year=grad_val,
                gender=data.get('gender', '').strip() or None,
                mobile_number=data.get('mobile_number', '').strip() or None,
                email=data.get('email', '').strip() or None,
                student_id=student_id_raw,
                entered_cgpa=cgpa_val,
            )
            student.set_password(data.get('password', ''))
            db.session.add(student)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {e}', 'danger')

    return render_template('register.html')


# ─── login ──────────────────────────────────────────────────────────────────

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if getattr(current_user, 'role', None) == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')

        # Find user by roll_number, student_id, email, or mobile
        user = Student.query.filter(
            (Student.roll_number == identifier) |
            (Student.student_id == identifier) |
            (Student.email == identifier) |
            (Student.mobile_number == identifier) |
            (Student.full_name == identifier)
        ).first()

        if user and user.check_password(password):
            login_user(user)
            session['role'] = getattr(user, 'role', 'student')

            if user.role == 'admin':
                flash(f'Welcome Administrator {user.full_name}!', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash(f'Welcome back, {user.full_name}!', 'success')
                return redirect(url_for('auth.dashboard'))

        flash('Invalid credentials. Please try again.', 'danger')

    return render_template('login.html')


# ─── VIP access ─────────────────────────────────────────────────────────────

@bp.route('/vip-access', methods=['POST'])
def vip_access():
    key = request.form.get('vip_key', '').strip()
    if key == current_app.config['VIP_ACCESS_KEY']:
        session['vip_mode'] = True
        return redirect(url_for('auth.vip_dashboard'))
    flash('Invalid VIP key.', 'danger')
    return redirect(url_for('auth.login'))


@bp.route('/vip-dashboard')
def vip_dashboard():
    if not session.get('vip_mode') and not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    demo_students = [
        {'name': 'Arjun Sharma', 'roll': 'DEMO001', 'cgpa': 9.42, 'course': 'B.Tech', 'dept': 'CSE', 'rank': 1},
        {'name': 'Priya Patel', 'roll': 'DEMO002', 'cgpa': 9.12, 'course': 'B.Tech', 'dept': 'ECE', 'rank': 2},
        {'name': 'Rahul Singh', 'roll': 'DEMO003', 'cgpa': 8.91, 'course': 'B.Tech', 'dept': 'MECH', 'rank': 3},
        {'name': 'Ananya Reddy', 'roll': 'DEMO004', 'cgpa': 8.52, 'course': 'B.Tech', 'dept': 'CIVIL', 'rank': 4},
        {'name': 'Kiran Kumar', 'roll': 'DEMO005', 'cgpa': 8.21, 'course': 'B.Tech', 'dept': 'EEE', 'rank': 5},
    ]
    demo_subjects = [
        {'name': 'Data Structures', 'avg': 78, 'attendance': 85},
        {'name': 'Mathematics III', 'avg': 72, 'attendance': 90},
        {'name': 'Computer Networks', 'avg': 68, 'attendance': 82},
        {'name': 'Operating Systems', 'avg': 75, 'attendance': 88},
    ]
    return render_template('vip_dashboard.html', demo_students=demo_students, demo_subjects=demo_subjects)


# ─── student dashboard ──────────────────────────────────────────────────────

@bp.route('/dashboard')
@login_required
def dashboard():
    student = current_user

    # Compute rank with tie handling (only among students, not admin)
    all_with_cgpa = Student.query.filter(
        Student.role == 'student',
        Student.entered_cgpa.isnot(None)
    ).order_by(Student.entered_cgpa.desc()).all()

    rank = None
    total_ranked = len(all_with_cgpa)
    for i, s in enumerate(all_with_cgpa):
        if s.id == student.id:
            rank = i + 1
            # Walk back to handle ties (find first person with same CGPA)
            for j in range(i - 1, -1, -1):
                if all_with_cgpa[j].entered_cgpa == student.entered_cgpa:
                    rank = j + 1
                else:
                    break
            break

    # Attendance totals for THIS student
    total_att = Attendance.query.filter_by(student_id=student.id).count()
    present_att = Attendance.query.filter_by(student_id=student.id, status='present').count()
    att_pct = round(present_att / total_att * 100, 1) if total_att else 0

    # Marks for THIS student
    marks = Mark.query.filter_by(student_id=student.id).all()

    # Subject-wise attendance for THIS student
    subjects = Subject.query.all()
    subj_att = []
    for subj in subjects:
        t = Attendance.query.filter_by(student_id=student.id, subject_id=subj.id).count()
        p = Attendance.query.filter_by(student_id=student.id, subject_id=subj.id, status='present').count()
        if t > 0:
            subj_att.append({
                'subject': subj,
                'pct': round(p / t * 100, 1),
                'present': p,
                'total': t,
            })

    topper_cgpa = all_with_cgpa[0].entered_cgpa if all_with_cgpa else 0

    stats = {
        'student': student,
        'rank': rank,
        'total_ranked': total_ranked,
        'att_pct': att_pct,
        'marks': marks,
        'subj_att': subj_att,
        'subjects': subjects,
        'topper_cgpa': topper_cgpa,
        'gap_from_topper': round(topper_cgpa - (student.entered_cgpa or 0), 2) if student.entered_cgpa else None,
        'overall_percentage': round(student.entered_cgpa * 10, 2) if student.entered_cgpa else None,
        'grade': get_grade(student.entered_cgpa),
    }
    return render_template('dashboard.html', stats=stats)


# ─── edit profile ────────────────────────────────────────────────────────────

@bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    student = current_user
    if request.method == 'POST':
        try:
            cgpa = request.form.get('entered_cgpa', '').strip()
            if cgpa:
                cgpa_val = float(cgpa)
                if not (0 <= cgpa_val <= 10):
                    flash('CGPA must be between 0 and 10.', 'danger')
                    return render_template('edit_profile.html', student=student)
                student.entered_cgpa = cgpa_val
            else:
                student.entered_cgpa = None

            student.full_name = request.form.get('full_name', student.full_name or '').strip()

            age_raw = request.form.get('age', '').strip()
            student.age = int(age_raw) if age_raw else student.age

            dob_raw = request.form.get('dob', '').strip()
            if dob_raw:
                student.dob = datetime.strptime(dob_raw, '%Y-%m-%d').date()

            student.gender = request.form.get('gender', student.gender or '').strip() or None
            student.mobile_number = request.form.get('mobile_number', student.mobile_number or '').strip() or None
            student.email = request.form.get('email', '').strip() or None
            student.class_name = request.form.get('class_name', student.class_name or '').strip() or None
            student.semester = request.form.get('semester', student.semester or '').strip() or None
            student.course = request.form.get('course', student.course or '').strip() or None
            student.branch = request.form.get('branch', student.branch or '').strip() or None
            student.department = request.form.get('department', student.department or '').strip() or None

            grad_raw = request.form.get('graduation_year', '').strip()
            student.graduation_year = int(grad_raw) if grad_raw else student.graduation_year

            db.session.commit()
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('auth.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {e}', 'danger')

    return render_template('edit_profile.html', student=student)


# ─── rankings ────────────────────────────────────────────────────────────────

@bp.route('/rankings')
@login_required
def rankings():
    students = Student.query.filter(
        Student.role == 'student',
        Student.entered_cgpa.isnot(None)
    ).order_by(Student.entered_cgpa.desc()).all()

    # Dense rank with tie handling
    ranked = []
    current_rank = 1
    for i, s in enumerate(students):
        if i > 0 and s.entered_cgpa == students[i - 1].entered_cgpa:
            rank = ranked[-1]['rank']  # tie: same rank
        else:
            rank = current_rank
        ranked.append({
            'student': s,
            'rank': rank,
            'grade': get_grade(s.entered_cgpa)
        })
        current_rank += 1

    my_rank = next((r['rank'] for r in ranked if r['student'].id == current_user.id), None)
    return render_template('rankings.html', ranked=ranked, my_rank=my_rank)


# ─── logout ──────────────────────────────────────────────────────────────────

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('vip_mode', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

