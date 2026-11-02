# routes/admin.py
"""Admin blueprint — dashboard, login, students, subjects, assessments, marks, attendance, class analysis."""

from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models.student import Student, Subject, Assessment, Mark, Attendance
from extensions import db

bp = Blueprint('admin', __name__)


# ─── ACCESS CONTROL ─────────────────────────────────────────────────────────

@bp.before_request
def check_admin_access():
    """Enforce strict administrator authorization on all admin routes."""
    # Allow admin login page and static files
    if request.endpoint == 'admin.login':
        return None

    # Must be authenticated
    if not current_user.is_authenticated:
        flash('Please log in with administrator credentials.', 'warning')
        return redirect(url_for('admin.login'))

    # Must have admin role
    if getattr(current_user, 'role', None) != 'admin':
        flash('Access Denied: Administrator privileges required.', 'danger')
        return redirect(url_for('auth.dashboard'))


# ─── ADMIN AUTHENTICATION ───────────────────────────────────────────────────

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Separate administrator login page — only Kowshika + VIP."""
    if current_user.is_authenticated:
        if getattr(current_user, 'role', None) == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Access Denied: You are logged in as a student.', 'danger')
            return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        password = request.form.get('password', '')

        # Lookup user by full_name or roll_number
        user = Student.query.filter(
            (Student.full_name == name) | (Student.roll_number == name)
        ).first()

        if user:
            # Check if this is an admin account
            if getattr(user, 'role', None) != 'admin':
                flash('Access denied: Student accounts cannot access the administrator portal.', 'danger')
                return render_template('admin_login.html')

            # Verify password
            if user.check_password(password):
                login_user(user)
                session['role'] = 'admin'
                flash(f'Welcome, Administrator {user.full_name}!', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Invalid administrator credentials.', 'danger')
                return render_template('admin_login.html')
        else:
            flash('Invalid administrator credentials.', 'danger')
            return render_template('admin_login.html')

    return render_template('admin_login.html')


@bp.route('/logout')
@login_required
def logout():
    """Admin logout."""
    logout_user()
    session.pop('role', None)
    flash('Administrator logged out successfully.', 'info')
    return redirect(url_for('admin.login'))


@bp.route('/')
def index():
    return redirect(url_for('admin.dashboard'))


# ─── DASHBOARD ───────────────────────────────────────────────────────────────

@bp.route('/dashboard')
@login_required
def dashboard():
    # Only regular students in stats (exclude admin account)
    students = Student.query.filter_by(role='student').all()
    subjects = Subject.query.all()
    assessments = Assessment.query.all()
    total = len(students)

    cgpa_list = [s.entered_cgpa for s in students if s.entered_cgpa is not None]
    avg_cgpa = round(sum(cgpa_list) / len(cgpa_list), 2) if cgpa_list else 0
    highest_cgpa = max(cgpa_list) if cgpa_list else 0
    lowest_cgpa = min(cgpa_list) if cgpa_list else 0

    male_count = sum(1 for s in students if s.gender and s.gender.lower() in ('male', 'm'))
    female_count = sum(1 for s in students if s.gender and s.gender.lower() in ('female', 'f'))
    other_count = total - male_count - female_count

    dept_counts = {}
    for s in students:
        d = s.department or 'Unknown'
        dept_counts[d] = dept_counts.get(d, 0) + 1

    course_counts = {}
    for s in students:
        c = s.course or 'Unknown'
        course_counts[c] = course_counts.get(c, 0) + 1

    total_attendance = Attendance.query.count()
    present_count = Attendance.query.filter_by(status='present').count()
    avg_attendance = round((present_count / total_attendance * 100), 1) if total_attendance else 0

    recent_students = Student.query.filter_by(role='student').order_by(Student.id.desc()).limit(10).all()

    stats = {
        'total_students': total,
        'total_subjects': len(subjects),
        'total_assessments': len(assessments),
        'avg_cgpa': avg_cgpa,
        'highest_cgpa': highest_cgpa,
        'lowest_cgpa': lowest_cgpa,
        'male_count': male_count,
        'female_count': female_count,
        'other_count': other_count,
        'dept_counts': dept_counts,
        'course_counts': course_counts,
        'avg_attendance': avg_attendance,
        'admin_name': 'Kowshika'
    }

    return render_template('admin_dashboard.html',
                           students=recent_students,
                           all_students=students,
                           stats=stats)


# ─── STUDENTS MANAGEMENT ─────────────────────────────────────────────────────

@bp.route('/students')
@login_required
def students():
    all_students = Student.query.filter_by(role='student').order_by(Student.full_name).all()
    return render_template('admin_students.html', students=all_students)


@bp.route('/students/edit/<int:sid>', methods=['GET', 'POST'])
@login_required
def edit_student(sid):
    student = Student.query.get_or_404(sid)
    if student.role == 'admin':
        flash('Cannot edit master administrator from this screen.', 'warning')
        return redirect(url_for('admin.students'))

    if request.method == 'POST':
        try:
            # Admin can edit all student fields including roll number
            new_roll = request.form.get('roll_number', '').strip()
            if new_roll != student.roll_number:
                existing = Student.query.filter_by(roll_number=new_roll).first()
                if existing and existing.id != student.id:
                    flash(f'Roll number "{new_roll}" is already taken by another student.', 'danger')
                    return render_template('admin_student_edit.html', student=student)
                student.roll_number = new_roll

            student.full_name = request.form.get('full_name', '').strip()
            student.email = request.form.get('email', '').strip() or None
            student.mobile_number = request.form.get('mobile_number', '').strip() or None
            student.gender = request.form.get('gender', '').strip() or None
            student.class_name = request.form.get('class_name', '').strip() or None
            student.course = request.form.get('course', '').strip() or None
            student.branch = request.form.get('branch', '').strip() or None
            student.department = request.form.get('department', '').strip() or None
            student.semester = request.form.get('semester', '').strip() or None

            age_val = request.form.get('age', '').strip()
            student.age = int(age_val) if age_val else None

            grad_val = request.form.get('graduation_year', '').strip()
            student.graduation_year = int(grad_val) if grad_val else None

            cgpa_val = request.form.get('entered_cgpa', '').strip()
            if cgpa_val:
                c = float(cgpa_val)
                if 0 <= c <= 10:
                    student.entered_cgpa = c
                else:
                    flash('CGPA must be between 0 and 10.', 'danger')
                    return render_template('admin_student_edit.html', student=student)
            else:
                student.entered_cgpa = None

            dob_val = request.form.get('dob', '').strip()
            if dob_val:
                student.dob = datetime.strptime(dob_val, '%Y-%m-%d').date()

            db.session.commit()
            flash(f'Student "{student.full_name}" updated successfully.', 'success')
            return redirect(url_for('admin.students'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating student: {e}', 'danger')

    return render_template('admin_student_edit.html', student=student)


@bp.route('/students/delete/<int:sid>', methods=['POST'])
@login_required
def delete_student(sid):
    student = Student.query.get_or_404(sid)
    if student.role == 'admin':
        flash('Cannot delete administrator account.', 'danger')
        return redirect(url_for('admin.students'))
    name = student.full_name
    db.session.delete(student)
    db.session.commit()
    flash(f'Student {name} deleted.', 'success')
    return redirect(url_for('admin.students'))


# ─── SUBJECTS MANAGEMENT ─────────────────────────────────────────────────────

@bp.route('/subjects', methods=['GET', 'POST'])
@login_required
def subjects():
    if request.method == 'POST':
        try:
            code = request.form.get('code', '').strip().upper()
            existing = Subject.query.filter_by(code=code).first()
            if existing:
                flash(f'Subject with code "{code}" already exists.', 'danger')
                return redirect(url_for('admin.subjects'))

            subj = Subject(
                code=code,
                name=request.form['name'].strip(),
                credits=int(request.form.get('credits', 3)),
                department=request.form.get('department', '').strip(),
                semester=request.form.get('semester', '').strip(),
            )
            db.session.add(subj)
            db.session.commit()
            flash(f'Subject "{subj.name}" added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding subject: {e}', 'danger')
        return redirect(url_for('admin.subjects'))

    all_subjects = Subject.query.order_by(Subject.code).all()
    return render_template('admin_subjects.html', subjects=all_subjects)


@bp.route('/subjects/delete/<int:sid>', methods=['POST'])
@login_required
def delete_subject(sid):
    subj = Subject.query.get_or_404(sid)
    name = subj.name
    db.session.delete(subj)
    db.session.commit()
    flash(f'Subject "{name}" deleted.', 'success')
    return redirect(url_for('admin.subjects'))


# ─── ASSESSMENTS MANAGEMENT ──────────────────────────────────────────────────

@bp.route('/assessments', methods=['GET', 'POST'])
@login_required
def assessments():
    if request.method == 'POST':
        try:
            max_m = float(request.form.get('max_marks', 100))
            min_m = float(request.form.get('min_marks', 0))
            pass_m = float(request.form.get('passing_marks', 40))
            a = Assessment(
                name=request.form['name'].strip(),
                assessment_type=request.form['assessment_type'].strip(),
                max_marks=max_m,
                min_marks=min_m,
                passing_marks=pass_m,
                weightage=float(request.form.get('weightage', 100)),
                subject_id=int(request.form['subject_id']),
            )
            db.session.add(a)
            db.session.commit()
            flash(f'Assessment "{a.name}" configured successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding assessment: {e}', 'danger')
        return redirect(url_for('admin.assessments'))

    all_assessments = Assessment.query.all()
    all_subjects = Subject.query.order_by(Subject.name).all()
    return render_template('admin_assessments.html', assessments=all_assessments, subjects=all_subjects)


@bp.route('/assessments/delete/<int:aid>', methods=['POST'])
@login_required
def delete_assessment(aid):
    a = Assessment.query.get_or_404(aid)
    name = a.name
    db.session.delete(a)
    db.session.commit()
    flash(f'Assessment "{name}" deleted.', 'success')
    return redirect(url_for('admin.assessments'))


# ─── MARKS MANAGEMENT ────────────────────────────────────────────────────────

@bp.route('/marks', methods=['GET', 'POST'])
@login_required
def marks():
    if request.method == 'POST':
        try:
            student_id = int(request.form['student_id'])
            subject_id = int(request.form['subject_id'])
            assessment_id = int(request.form['assessment_id'])
            obtained = float(request.form['marks_obtained'])

            # Validate against assessment max marks
            assessment = Assessment.query.get(assessment_id)
            if assessment and obtained > assessment.max_marks:
                flash(f'Marks obtained ({obtained}) cannot exceed Max Marks ({assessment.max_marks}).', 'danger')
                return redirect(url_for('admin.marks'))

            m = Mark(
                student_id=student_id,
                subject_id=subject_id,
                assessment_id=assessment_id,
                marks_obtained=obtained,
            )
            db.session.add(m)
            db.session.commit()
            flash('Marks recorded successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error recording marks: {e}', 'danger')
        return redirect(url_for('admin.marks'))

    all_marks = Mark.query.order_by(Mark.id.desc()).all()
    all_students = Student.query.filter_by(role='student').order_by(Student.full_name).all()
    all_subjects = Subject.query.order_by(Subject.name).all()
    all_assessments = Assessment.query.all()
    return render_template('admin_marks.html', marks=all_marks,
                           students=all_students, subjects=all_subjects,
                           assessments=all_assessments)


@bp.route('/marks/delete/<int:mid>', methods=['POST'])
@login_required
def delete_mark(mid):
    m = Mark.query.get_or_404(mid)
    db.session.delete(m)
    db.session.commit()
    flash('Mark record deleted.', 'success')
    return redirect(url_for('admin.marks'))


# ─── ATTENDANCE MANAGEMENT ───────────────────────────────────────────────────

@bp.route('/attendance', methods=['GET', 'POST'])
@login_required
def attendance():
    if request.method == 'POST':
        try:
            att = Attendance(
                student_id=int(request.form['student_id']),
                subject_id=int(request.form['subject_id']),
                date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
                status=request.form.get('status', 'present'),
            )
            db.session.add(att)
            db.session.commit()
            flash('Attendance recorded successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error recording attendance: {e}', 'danger')
        return redirect(url_for('admin.attendance'))

    all_attendance = Attendance.query.order_by(Attendance.date.desc()).all()
    all_students = Student.query.filter_by(role='student').order_by(Student.full_name).all()
    all_subjects = Subject.query.order_by(Subject.name).all()
    return render_template('admin_attendance.html', attendance=all_attendance,
                           students=all_students, subjects=all_subjects)


@bp.route('/attendance/delete/<int:aid>', methods=['POST'])
@login_required
def delete_attendance(aid):
    a = Attendance.query.get_or_404(aid)
    db.session.delete(a)
    db.session.commit()
    flash('Attendance record deleted.', 'success')
    return redirect(url_for('admin.attendance'))


# ─── CLASS ANALYSIS & TOPPERS ────────────────────────────────────────────────

@bp.route('/class-analysis')
@login_required
def class_analysis():
    students = Student.query.filter_by(role='student').all()
    subjects = Subject.query.all()

    # Per-subject average marks and attendance
    subject_stats = []
    for subj in subjects:
        subj_marks = Mark.query.filter_by(subject_id=subj.id).all()
        if subj_marks:
            avg = round(sum(m.marks_obtained for m in subj_marks) / len(subj_marks), 2)
            highest = max(m.marks_obtained for m in subj_marks)
            lowest = min(m.marks_obtained for m in subj_marks)
        else:
            avg = highest = lowest = 0

        total_att = Attendance.query.filter_by(subject_id=subj.id).count()
        present_att = Attendance.query.filter_by(subject_id=subj.id, status='present').count()
        att_pct = round(present_att / total_att * 100, 1) if total_att else 0

        subject_stats.append({
            'subject': subj,
            'avg_marks': avg,
            'highest': highest,
            'lowest': lowest,
            'total_marks_entries': len(subj_marks),
            'attendance_pct': att_pct,
        })

    # CGPA distribution
    cgpa_ranges = {'9-10': 0, '8-9': 0, '7-8': 0, '6-7': 0, '5-6': 0, 'Below 5': 0}
    for s in students:
        if s.entered_cgpa is not None:
            if s.entered_cgpa >= 9:
                cgpa_ranges['9-10'] += 1
            elif s.entered_cgpa >= 8:
                cgpa_ranges['8-9'] += 1
            elif s.entered_cgpa >= 7:
                cgpa_ranges['7-8'] += 1
            elif s.entered_cgpa >= 6:
                cgpa_ranges['6-7'] += 1
            elif s.entered_cgpa >= 5:
                cgpa_ranges['5-6'] += 1
            else:
                cgpa_ranges['Below 5'] += 1

    # Top performers (toppers)
    top_students = sorted(
        [s for s in students if s.entered_cgpa is not None],
        key=lambda x: x.entered_cgpa, reverse=True
    )[:10]

    # Low performers
    low_students = sorted(
        [s for s in students if s.entered_cgpa is not None and s.entered_cgpa < 6.0],
        key=lambda x: x.entered_cgpa
    )[:10]

    return render_template('admin_class_analysis.html',
                           subject_stats=subject_stats,
                           cgpa_ranges=cgpa_ranges,
                           top_students=top_students,
                           low_students=low_students,
                           total_students=len(students),
                           total_subjects=len(subjects))

