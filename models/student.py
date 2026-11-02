# models/student.py
"""Student and related model definitions."""

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db


class Student(UserMixin, db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    roll_number = db.Column(db.String(30), unique=True, nullable=False)
    role = db.Column(db.String(20), default='student', nullable=False)  # 'admin' or 'student'
    age = db.Column(db.Integer, nullable=True)
    dob = db.Column(db.Date, nullable=True)
    class_name = db.Column("class", db.String(20), nullable=True)
    semester = db.Column(db.String(20), nullable=True)
    course = db.Column(db.String(80), nullable=True)
    branch = db.Column(db.String(80), nullable=True)
    department = db.Column(db.String(80), nullable=True)
    graduation_year = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    mobile_number = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    student_id = db.Column(db.String(30), unique=True, nullable=True)
    entered_cgpa = db.Column(db.Float, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    # Relationships
    marks = db.relationship('Mark', backref='student', lazy=True, cascade='all, delete-orphan')
    attendance_records = db.relationship('Attendance', backref='student', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"<Student {self.full_name} ({self.roll_number}) [{self.role}]>"


class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    credits = db.Column(db.Integer, nullable=False, default=3)
    department = db.Column(db.String(80), nullable=True)
    semester = db.Column(db.String(20), nullable=True)

    marks = db.relationship('Mark', backref='subject', lazy=True, cascade='all, delete-orphan')
    attendance_records = db.relationship('Attendance', backref='subject', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Subject {self.code} - {self.name}>"


class Assessment(db.Model):
    __tablename__ = "assessments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    assessment_type = db.Column(db.String(50), nullable=False)  # midterm, final, quiz, assignment
    max_marks = db.Column(db.Float, nullable=False, default=100)
    min_marks = db.Column(db.Float, nullable=True, default=0)
    passing_marks = db.Column(db.Float, nullable=True, default=40)
    weightage = db.Column(db.Float, nullable=False, default=100)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    subject = db.relationship('Subject', backref='assessments')

    marks = db.relationship('Mark', backref='assessment', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Assessment {self.name} ({self.assessment_type})>"


class Mark(db.Model):
    __tablename__ = "marks"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    marks_obtained = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Mark Student:{self.student_id} Subject:{self.subject_id} Marks:{self.marks_obtained}>"


class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False, default='present')  # present, absent, late

    def __repr__(self):
        return f"<Attendance Student:{self.student_id} Date:{self.date} Status:{self.status}>"

