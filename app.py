import os
from flask import Flask, jsonify, render_template, request
from db import connection
import chk_access

app = Flask(__name__)

# Admin password for viewing the entry log. Reads from an env var if set,
# otherwise falls back to the value you gave.
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

    cursor = connection.cursor()
    try:
        student = chk_access.get_student(cursor, roll_number)

        if not student:
            return jsonify({
                "status": "DENIED",
                "message": "ACCESS DENIED",
                "reason": "Student not found"
            })

        roll_no, name, department_id = student
        clash = chk_access.get_clashing_lecture(cursor, department_id)

        if clash:
            subject = clash[0]
            status = "DENIED"
            message = "ACCESS DENIED"
            reason = f"You have {subject} right now"
        else:
            status = "ALLOWED"
            message = "ACCESS GRANTED"
            reason = f"Welcome {name}"

        chk_access.log_entry(cursor, roll_no, status)
        connection.commit()

        return jsonify({
            "status": status,
            "message": message,
            "reason": reason
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


@app.route("/admin/logs", methods=["POST"])
def admin_logs():
    data = request.get_json(silent=True) or {}
    password = data.get("password") or ""

    if password != ADMIN_PASSWORD:
        return jsonify({
            "status": "ERROR",
            "message": "Incorrect password"
        }), 401

    if not connection.is_connected():
        connection.reconnect(attempts=3, delay=2)

    cursor = connection.cursor()
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
    except Exception as exc:
        return jsonify({
            "status": "ERROR",
            "message": "Database error",
            "reason": str(exc)
        }), 500
    finally:
        cursor.close()


if __name__ == "__main__":
    app.run(debug=True)
