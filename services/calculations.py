# services/calculations.py
"""Utility functions for calculating student statistics.
The dashboard uses :func:`get_overall_stats` to obtain a dictionary of values
that are rendered in the template.  The function is deliberately lightweight –
it only accesses the ``Student`` model and does not depend on any other
application modules, avoiding circular‑import problems.
"""

from models.student import Student

def get_overall_stats(student_id: int) -> dict:
    """Return a dict with the primary stats for the given student.

    * ``entered_cgpa`` – optional CGPA entered at registration.
    * ``overall_cgpa`` – falls back to ``entered_cgpa`` when no semester
      marks are stored.
    * ``overall_percentage`` – derived from the CGPA (10‑point scale → %).
    * Additional placeholders (semester, course, etc.) are included for the
      UI.
    """
    student = Student.query.get(student_id)
    if not student:
        return {}

    stats = {
        "full_name": student.full_name,
        "student_id": student.student_id,
        "roll_number": student.roll_number or "N/A",
        "entered_cgpa": student.entered_cgpa,
        "overall_cgpa": None,
        "overall_percentage": None,
    }

    if student.entered_cgpa is not None:
        stats["overall_cgpa"] = student.entered_cgpa
        # Approximate % assuming a 10‑point CGPA scale
        stats["overall_percentage"] = round(student.entered_cgpa * 10, 2)

    # Placeholder values for other dashboard cards – real calculations would
    # aggregate marks, attendance, etc.
    stats.update({
        "current_semester": student.semester,
        "course": student.course,
        "branch": student.branch,
        "department": student.department,
        "graduation_year": student.graduation_year,
        "attendance_percent": 0,
        "subjects_count": 0,
    })
    return stats

