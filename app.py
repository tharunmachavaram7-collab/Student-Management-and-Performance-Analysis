# app.py
"""Flask application entry point for Student Performance Analysis System."""

from flask import Flask
from sqlalchemy import text
from extensions import db, login_manager

app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

from models.student import Student

@login_manager.user_loader
def load_user(user_id):
    return Student.query.get(int(user_id))

from routes import auth, admin
app.register_blueprint(auth.bp)
app.register_blueprint(admin.bp, url_prefix='/admin')


def init_db_and_admin():
    """Ensure database schema is up-to-date and Kowshika administrator exists."""
    db.create_all()

    # Safely migrate new columns if using existing SQLite db
    columns_to_check = [
        ("students", "role", "VARCHAR(20) DEFAULT 'student'"),
        ("assessments", "min_marks", "FLOAT DEFAULT 0"),
        ("assessments", "passing_marks", "FLOAT DEFAULT 40")
    ]
    for table, col, col_type in columns_to_check:
        try:
            db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))
            db.session.commit()
        except Exception:
            db.session.rollback()

    # Initialize single administrator account Kowshika
    admin_user = Student.query.filter(
        (Student.role == 'admin') | (Student.full_name == 'Kowshika')
    ).first()

    if not admin_user:
        admin_user = Student(
            full_name='Kowshika',
            roll_number='ADMIN_KOWSHIKA',
            student_id='ADMIN001',
            role='admin',
            is_admin=True,
            department='Administration',
            course='Executive',
            semester='N/A'
        )
        admin_user.set_password('VIP')
        db.session.add(admin_user)
        db.session.commit()
    else:
        admin_user.full_name = 'Kowshika'
        admin_user.role = 'admin'
        admin_user.is_admin = True
        # Ensure password is VIP
        if not admin_user.check_password('VIP'):
            admin_user.set_password('VIP')
        db.session.commit()


with app.app_context():
    init_db_and_admin()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

