import os
from flask import Flask, jsonify, render_template, request
from db import connection
import chk_access

app = Flask(__name__)

ADMIN_PASSWORD = os.getenv("DEN_ADMIN_PASSWORD", "Pratham@2007")


@app.route("/", methods=["GET"])
def index():
    return render_template("temp.html")


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


if __name__ == "__main__":
    app.run(debug=True)
