from flask import Flask, jsonify, render_template, request
from db import connection
import chk_access

app = Flask(__name__)


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


if __name__ == "__main__":
    app.run(debug=True)
