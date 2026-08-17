from datetime import datetime


def get_student(cursor, roll_number):
    """Look up a student by roll number. Returns (roll_no, name, department_id) or None."""
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


def get_all_logs(cursor):
    """Fetch every entry log, newest first, joined with the student's name."""
    cursor.execute(
        """
        SELECT den_entry_log.id,
               den_entry_log.roll_no,
               student.name,
               den_entry_log.status,
               den_entry_log.entry_time
        FROM den_entry_log
        LEFT JOIN student ON den_entry_log.roll_no = student.roll_no
        ORDER BY den_entry_log.entry_time DESC
        """
    )
    return cursor.fetchall()
