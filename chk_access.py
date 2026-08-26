from datetime import datetime, timedelta

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

def check_and_occupy_activity(cursor, roll_no, activity_name):
    """Verifies activity limit and creates an active session."""
    cursor.execute(
        "SELECT max_capacity, current_count FROM activity_limit WHERE activity_name = %s FOR UPDATE",
        (activity_name,)
    )
    row = cursor.fetchone()
    if not row:
        return False, "Activity not recognized."

    max_cap, current_count = row
    if current_count >= max_cap:
        return False, f"{activity_name} is currently full (Capacity: {max_cap})."

    # Increment count
    cursor.execute(
        "UPDATE activity_limit SET current_count = current_count + 1 WHERE activity_name = %s",
        (activity_name,)
    )

    # Log session
    cursor.execute(
        """
        INSERT INTO activity_session (roll_no, action_type, activity_name, status)
        VALUES (%s, 'ACTIVITY', %s, 'ACTIVE')
        """,
        (roll_no, activity_name)
    )
    return True, f"Slot confirmed for {activity_name} ({current_count + 1}/{max_cap})"

def record_equipment_rental(cursor, roll_no, item_name, duration):
    """Records an equipment rental session with selected duration."""
    cursor.execute(
        """
        INSERT INTO activity_session (roll_no, action_type, equipment_item, duration_hours, status)
        VALUES (%s, 'RENTAL', %s, %s, 'ACTIVE')
        """,
        (roll_no, item_name, duration)
    )
    return True, f"Rented {item_name} for {duration} Hour(s)."

def get_active_session(cursor, roll_no):
    """Fetches active session details and computes time left in minutes."""
    cursor.execute(
        """
        SELECT session_id, action_type, activity_name, equipment_item, duration_hours, start_time
        FROM activity_session
        WHERE roll_no = %s AND status = 'ACTIVE'
        ORDER BY start_time DESC
        LIMIT 1
        """,
        (roll_no,)
    )
    row = cursor.fetchone()
    if not row:
        return None

    session_id, action_type, activity_name, equipment_item, duration_hours, start_time = row
    
    # Default activity sessions to 1 hour if duration is None
    total_hours = duration_hours if duration_hours else 1
    end_time = start_time + timedelta(hours=total_hours)
    remaining_seconds = (end_time - datetime.now()).total_seconds()
    minutes_left = max(0, int(remaining_seconds // 60))

    label = activity_name if action_type == "ACTIVITY" else f"Rented: {equipment_item}"

    return {
        "session_id": session_id,
        "action_type": action_type,
        "activity_name": activity_name,
        "equipment_item": equipment_item,
        "label": label,
        "minutes_left": minutes_left,
        "start_time": start_time.strftime("%H:%M")
    }

def checkout_session(cursor, roll_no):
    """Marks the active session as COMPLETED and frees up capacity."""
    session = get_active_session(cursor, roll_no)
    if not session:
        return False, "No active session found."

    # Free up slot count if it was an activity
    if session["action_type"] == "ACTIVITY" and session["activity_name"]:
        cursor.execute(
            """
            UPDATE activity_limit
            SET current_count = GREATEST(0, current_count - 1)
            WHERE activity_name = %s
            """,
            (session["activity_name"],)
        )

    # Mark session completed
    cursor.execute(
        """
        UPDATE activity_session
        SET status = 'COMPLETED'
        WHERE session_id = %s
        """,
        (session["session_id"],)
    )
    return True, f"Successfully checked out from {session['label']}."


# ==========================================
# REPORTING QUERIES (New Features)
# ==========================================

def get_detailed_sessions(cursor):
    """Fetches details on what equipment/activity a student engaged with."""
    cursor.execute("""
        SELECT a.roll_no, s.name, a.action_type, a.activity_name, a.equipment_item, a.start_time, a.status
        FROM activity_session a
        LEFT JOIN student s ON a.roll_no = s.roll_no
        ORDER BY a.start_time DESC
    """)
    return cursor.fetchall()

def get_monthly_visitors(cursor):
    """Calculates total allowed entry log counts grouped by Month-Year."""
    cursor.execute("""
        SELECT DATE_FORMAT(entry_time, '%Y-%m') AS month, COUNT(id) AS total_visits
        FROM den_entry_log
        WHERE status = 'ALLOWED'
        GROUP BY month
        ORDER BY month DESC
    """)
    return cursor.fetchall()

def get_student_monthly_visits(cursor):
    """Calculates entry counts per individual student grouped by Month-Year."""
    cursor.execute("""
        SELECT s.roll_no, s.name, DATE_FORMAT(d.entry_time, '%Y-%m') AS month, COUNT(d.id) AS visits
        FROM den_entry_log d
        LEFT JOIN student s ON d.roll_no = s.roll_no
        WHERE d.status = 'ALLOWED'
        GROUP BY s.roll_no, s.name, month
        ORDER BY month DESC, visits DESC
    """)
    return cursor.fetchall()
