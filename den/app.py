import os
from flask import Flask, jsonify, render_template, request
from db import connection
import chk_access

app = Flask(__name__)

ADMIN_PASSWORD = os.getenv("DEN_ADMIN_PASSWORD", "Pratham@2007")


@app.route("/", methods=["GET"])
def index():
    # Serves the main student kiosk
    return render_template("temp.html")

@app.route("/admin", methods=["GET"])
def admin_page():
    # Serves the dedicated admin dashboard
    return render_template("admin.html")


@app.route("/check_entry", methods=["POST"])
def check_entry():
    data = request.get_json(silent=True) or {}
    roll_number = (data.get("roll_number") or "").strip()

    if not roll_number:
        return jsonify({
            "status": "ERROR",
            "message": "Please enter a roll number.",
            "reason": "Missing input"
        }), 400

    if not connection.is_connected():
        connection.reconnect(attempts=3, delay=2)

    cursor = connection.cursor(buffered=True)
    try:
        student = chk_access.get_student(cursor, roll_number)
        if not student:
            return jsonify({
                "status": "DENIED",
                "message": "ACCESS DENIED",
                "reason": "Student not found"
            })

        roll_no, name, department_id = student

        # 1. Check if the student is currently checked in
        active_session = chk_access.get_active_session(cursor, roll_no)
        if active_session:
            return jsonify({
                "status": "ACTIVE_SESSION",
                "message": "ACTIVE SESSION FOUND",
                "student_name": name,
                "roll_no": roll_no,
                "activity": active_session["label"],
                "minutes_left": active_session["minutes_left"],
                "start_time": active_session["start_time"]
            })

        # 2. Check timetable lecture clash
        clash = chk_access.get_clashing_lecture(cursor, department_id)
        if clash:
            subject = clash[0]
            status = "DENIED"
            message = "ACCESS DENIED"
            reason = f"You have {subject} right now"
            chk_access.log_entry(cursor, roll_no, status)
            connection.commit()
            return jsonify({
                "status": status,
                "message": message,
                "reason": reason
            })

        return jsonify({
            "status": "ALLOWED",
            "message": "ACCESS GRANTED",
            "reason": f"Welcome {name}",
            "student_name": name,
            "roll_no": roll_no
        })
    except Exception as exc:
        connection.rollback()
        return jsonify({
            "status": "ERROR",
            "message": "Database error",
            "reason": str(exc)
        }), 500
    finally:
        cursor.close()


@app.route("/select_action", methods=["POST"])
def select_action():
    data = request.get_json(silent=True) or {}
    roll_no = (data.get("roll_no") or "").strip()
    action_type = data.get("action_type")

    if not roll_no:
        return jsonify({"status": "ERROR", "message": "Roll number missing."}), 400

    if not connection.is_connected():
        connection.reconnect(attempts=3, delay=2)

    cursor = connection.cursor(buffered=True)
    try:
        if action_type == "ACTIVITY":
            activity_name = data.get("activity_name")
            success, msg = chk_access.check_and_occupy_activity(cursor, roll_no, activity_name)
            if not success:
                return jsonify({"status": "DENIED", "message": "CAPACITY FULL", "reason": msg}), 400

        elif action_type == "RENTAL":
            item = data.get("equipment_item")
            duration = int(data.get("duration", 1))
            success, msg = chk_access.record_equipment_rental(cursor, roll_no, item, duration)
        else:
            return jsonify({"status": "ERROR", "message": "Invalid choice."}), 400

        chk_access.log_entry(cursor, roll_no, "ALLOWED")
        connection.commit()

        return jsonify({"status": "ALLOWED", "message": "CHECK-IN COMPLETE", "reason": msg})
    except Exception as exc:
        connection.rollback()
        return jsonify({
            "status": "ERROR",
            "message": "Server error",
            "reason": str(exc)
        }), 500
    finally:
        cursor.close()


@app.route("/checkout", methods=["POST"])
def checkout():
    data = request.get_json(silent=True) or {}
    roll_no = (data.get("roll_no") or "").strip()

    if not roll_no:
        return jsonify({"status": "ERROR", "message": "Roll number missing."}), 400

    if not connection.is_connected():
        connection.reconnect(attempts=3, delay=2)

    cursor = connection.cursor(buffered=True)
    try:
        success, msg = chk_access.checkout_session(cursor, roll_no)
        if not success:
            return jsonify({"status": "ERROR", "message": msg}), 400

        chk_access.log_entry(cursor, roll_no, "CHECKOUT")
        connection.commit()
        return jsonify({"status": "OK", "message": "CHECKED OUT", "reason": msg})
    except Exception as exc:
        connection.rollback()
        return jsonify({"status": "ERROR", "message": "Server error", "reason": str(exc)}), 500
    finally:
        cursor.close()


@app.route("/admin/logs", methods=["POST"])
def admin_logs():
    data = request.get_json(silent=True) or {}
    password = data.get("password") or ""

    if password != ADMIN_PASSWORD:
        return jsonify({"status": "ERROR", "message": "Incorrect password"}), 401

    if not connection.is_connected():
        connection.reconnect(attempts=3, delay=2)

    cursor = connection.cursor(buffered=True)
    try:
        rows = chk_access.get_all_logs(cursor)
        logs = [
            {
                "id": row[0],
                "roll_no": row[1],
                "name": row[2] or "Unknown",
                "status": row[3],
                "entry_time": row[4].strftime("%Y-%m-%d %H:%M:%S") if row[4] else None
            }
            for row in rows
        ]
        return jsonify({"status": "OK", "logs": logs})
    finally:
        cursor.close()


@app.route("/admin/detailed_report", methods=["POST"])
def admin_detailed_report():
    data = request.get_json(silent=True) or {}
    password = data.get("password") or ""

    if password != ADMIN_PASSWORD:
        return jsonify({"status": "ERROR", "message": "Incorrect password"}), 401

    if not connection.is_connected():
        connection.reconnect(attempts=3, delay=2)

    cursor = connection.cursor(buffered=True)
    try:
        sessions_raw = chk_access.get_detailed_sessions(cursor)
        sessions = [{
            "roll_no": row[0],
            "name": row[1] or "Unknown",
            "action_type": row[2],
            "activity_name": row[3],
            "equipment_item": row[4],
            "start_time": row[5].strftime("%Y-%m-%d %H:%M:%S") if row[5] else None,
            "status": row[6]
        } for row in sessions_raw]

        monthly_raw = chk_access.get_monthly_visitors(cursor)
        monthly_stats = [{"month": row[0], "total_visits": row[1]} for row in monthly_raw]

        student_monthly_raw = chk_access.get_student_monthly_visits(cursor)
        student_monthly_stats = [{
            "roll_no": row[0],
            "name": row[1] or "Unknown",
            "month": row[2],
            "visits": row[3]
        } for row in student_monthly_raw]

        return jsonify({
            "status": "OK",
            "sessions": sessions,
            "monthly_stats": monthly_stats,
            "student_monthly_stats": student_monthly_stats
        })
    except Exception as exc:
        return jsonify({"status": "ERROR", "message": "Server error", "reason": str(exc)}), 500
    finally:
        cursor.close()


# ─── Timetable CRUD ────────────────────────────────────────────
@app.route("/admin/timetable", methods=["POST"])
def admin_timetable_list():
    data = request.get_json(silent=True) or {}
    if data.get("password") != ADMIN_PASSWORD:
        return jsonify({"status": "ERROR", "message": "Incorrect password"}), 401

    if not connection.is_connected():
        connection.reconnect(attempts=3, delay=2)

    cursor = connection.cursor(buffered=True)
    try:
        cursor.execute("SELECT id, department_id, day_of_week, start_time, end_time, subject FROM timetable ORDER BY department_id, day_of_week, start_time")
        entries = [{
            "id": r[0], "department_id": r[1], "day_of_week": r[2],
            "start_time": str(r[3]), "end_time": str(r[4]), "subject": r[5]
        } for r in cursor.fetchall()]
        return jsonify({"status": "OK", "entries": entries})
    finally:
        cursor.close()


@app.route("/admin/timetable/add", methods=["POST"])
def admin_timetable_add():
    data = request.get_json(silent=True) or {}
    if data.get("password") != ADMIN_PASSWORD:
        return jsonify({"status": "ERROR", "message": "Incorrect password"}), 401

    if not connection.is_connected():
        connection.reconnect(attempts=3, delay=2)

    cursor = connection.cursor(buffered=True)
    try:
        cursor.execute(
            "INSERT INTO timetable (department_id, day_of_week, start_time, end_time, subject) VALUES (%s, %s, %s, %s, %s)",
            (data["department_id"], data["day_of_week"], data["start_time"], data["end_time"], data["subject"])
        )
        connection.commit()
        return jsonify({"status": "OK", "message": "Timetable entry added successfully."})
    except Exception as exc:
        connection.rollback()
        return jsonify({"status": "ERROR", "message": str(exc)}), 500
    finally:
        cursor.close()


@app.route("/admin/timetable/delete", methods=["POST"])
def admin_timetable_delete():
    data = request.get_json(silent=True) or {}
    if data.get("password") != ADMIN_PASSWORD:
        return jsonify({"status": "ERROR", "message": "Incorrect password"}), 401

    if not connection.is_connected():
        connection.reconnect(attempts=3, delay=2)

    cursor = connection.cursor(buffered=True)
    try:
        cursor.execute("DELETE FROM timetable WHERE id = %s", (data["id"],))
        connection.commit()
        return jsonify({"status": "OK", "message": "Timetable entry deleted."})
    except Exception as exc:
        connection.rollback()
        return jsonify({"status": "ERROR", "message": str(exc)}), 500
    finally:
        cursor.close()


# ─── Students CRUD ─────────────────────────────────────────────
@app.route("/admin/students", methods=["POST"])
def admin_students_list():
    data = request.get_json(silent=True) or {}
    if data.get("password") != ADMIN_PASSWORD:
        return jsonify({"status": "ERROR", "message": "Incorrect password"}), 401

    if not connection.is_connected():
        connection.reconnect(attempts=3, delay=2)

    cursor = connection.cursor(buffered=True)
    try:
        cursor.execute("SELECT roll_no, name, department_id FROM student ORDER BY roll_no")
        students = [{"roll_no": r[0], "name": r[1], "department_id": r[2]} for r in cursor.fetchall()]
        return jsonify({"status": "OK", "students": students})
    finally:
        cursor.close()


@app.route("/admin/students/upsert", methods=["POST"])
def admin_students_upsert():
    data = request.get_json(silent=True) or {}
    if data.get("password") != ADMIN_PASSWORD:
        return jsonify({"status": "ERROR", "message": "Incorrect password"}), 401

    if not connection.is_connected():
        connection.reconnect(attempts=3, delay=2)

    cursor = connection.cursor(buffered=True)
    try:
        cursor.execute(
            "INSERT INTO student (roll_no, name, department_id) VALUES (%s, %s, %s) "
            "ON DUPLICATE KEY UPDATE name = VALUES(name), department_id = VALUES(department_id)",
            (data["roll_no"], data["name"], data["department_id"])
        )
        connection.commit()
        return jsonify({"status": "OK", "message": f"Student {data['roll_no']} saved."})
    except Exception as exc:
        connection.rollback()
        return jsonify({"status": "ERROR", "message": str(exc)}), 500
    finally:
        cursor.close()


@app.route("/admin/students/delete", methods=["POST"])
def admin_students_delete():
    data = request.get_json(silent=True) or {}
    if data.get("password") != ADMIN_PASSWORD:
        return jsonify({"status": "ERROR", "message": "Incorrect password"}), 401

    if not connection.is_connected():
        connection.reconnect(attempts=3, delay=2)

    cursor = connection.cursor(buffered=True)
    try:
        cursor.execute("DELETE FROM student WHERE roll_no = %s", (data["roll_no"],))
        connection.commit()
        return jsonify({"status": "OK", "message": f"Student {data['roll_no']} deleted."})
    except Exception as exc:
        connection.rollback()
        return jsonify({"status": "ERROR", "message": str(exc)}), 500
    finally:
        cursor.close()


# ─── Departments CRUD ──────────────────────────────────────────
@app.route("/admin/departments", methods=["POST"])
def admin_departments_list():
    data = request.get_json(silent=True) or {}
    if data.get("password") != ADMIN_PASSWORD:
        return jsonify({"status": "ERROR", "message": "Incorrect password"}), 401

    if not connection.is_connected():
        connection.reconnect(attempts=3, delay=2)

    cursor = connection.cursor(buffered=True)
    try:
        cursor.execute("SELECT department_id, department_name FROM department ORDER BY department_id")
        departments = [{"department_id": r[0], "department_name": r[1]} for r in cursor.fetchall()]
        return jsonify({"status": "OK", "departments": departments})
    finally:
        cursor.close()


@app.route("/admin/departments/add", methods=["POST"])
def admin_departments_add():
    data = request.get_json(silent=True) or {}
    if data.get("password") != ADMIN_PASSWORD:
        return jsonify({"status": "ERROR", "message": "Incorrect password"}), 401

    if not connection.is_connected():
        connection.reconnect(attempts=3, delay=2)

    cursor = connection.cursor(buffered=True)
    try:
        cursor.execute(
            "INSERT INTO department (department_name) VALUES (%s)",
            (data["department_name"],)
        )
        connection.commit()
        return jsonify({"status": "OK", "message": f"Department '{data['department_name']}' added."})
    except Exception as exc:
        connection.rollback()
        return jsonify({"status": "ERROR", "message": str(exc)}), 500
    finally:
        cursor.close()


@app.route("/admin/departments/delete", methods=["POST"])
def admin_departments_delete():
    data = request.get_json(silent=True) or {}
    if data.get("password") != ADMIN_PASSWORD:
        return jsonify({"status": "ERROR", "message": "Incorrect password"}), 401

    if not connection.is_connected():
        connection.reconnect(attempts=3, delay=2)

    cursor = connection.cursor(buffered=True)
    try:
        cursor.execute("DELETE FROM department WHERE department_id = %s", (data["department_id"],))
        connection.commit()
        return jsonify({"status": "OK", "message": "Department deleted."})
    except Exception as exc:
        connection.rollback()
        return jsonify({"status": "ERROR", "message": str(exc)}), 500
    finally:
        cursor.close()


if __name__ == "__main__":
    app.run(debug=True)

