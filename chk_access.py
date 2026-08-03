from datetime import datetime


def get_student(cursor, roll_number):
    cursor.execute(
        "SELECT roll_no, name, department_id FROM student WHERE roll_no = %s",
        (roll_number,)
    )
    return cursor.fetchone()


def get_clashing_lecture(cursor, department_id, now=None):
    """
    Check the timetable for this department to see if a lecture is running
    right now. Returns (subject, start_time, end_time) if there's a clash,
    otherwise None.
    """
    now = now or datetime.now()
    current_day = now.strftime("%A")   # e.g. "Monday"
    current_time = now.time().replace(microsecond=0)

    cursor.execute(
        """
        SELECT subject, start_time, end_time
        FROM timetable
        WHERE department_id = %s
          AND day_of_week = %s
          AND start_time <= %s
          AND end_time >= %s
        """,
        (department_id, current_day, current_time, current_time)
    )
    return cursor.fetchone()


def log_entry(cursor, roll_number, status):
    """Record an entry attempt in den_entry_log."""
    cursor.execute(
        "INSERT INTO den_entry_log (roll_no, status) VALUES (%s, %s)",
        (roll_number, status)
    )
