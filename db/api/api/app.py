from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3, os
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db" / "enroll.db"
SCHEMA = Path(__file__).parent.parent / "db" / "schema.sql"
SEED = Path(__file__).parent.parent / "db" / "seed.sql"

app = Flask(__name__)
CORS(app)

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not DB_PATH.exists():
        conn = get_conn()
        with open(SCHEMA, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        with open(SEED, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()

@app.route("/employees", methods=["POST"])
def create_employee():
    data = request.get_json(force=True)
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    department = data.get("department", "").strip()
    start_date = data.get("start_date", "").strip()
    if not (name and email and department and start_date):
        return jsonify({"error": "name, email, department, start_date required"}), 400

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO employees(name,email,department,start_date,status)
        VALUES (?,?,?,?, 'ENROLLED')
    """, (name, email, department, start_date))
    conn.commit()
    eid = cur.lastrowid
    conn.close()
    return jsonify({"message": "created", "id": eid}), 201

@app.route("/employees", methods=["GET"])
def list_employees():
    conn = get_conn()
    rows = conn.execute("""
        SELECT id, name, email, department, start_date, status, created_at
        FROM employees
        ORDER BY created_at DESC
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/employees/status", methods=["POST"])
def update_status():
    data = request.get_json(force=True)
    emp_id = data.get("id")
    status = data.get("status", "").upper()
    if status not in ("ENROLLED","INACTIVE"):
        return jsonify({"error": "status must be ENROLLED or INACTIVE"}), 400
    if not emp_id:
        return jsonify({"error": "id required"}), 400

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE employees SET status=? WHERE id=?", (status, emp_id))
    if cur.rowcount == 0:
        conn.close()
        return jsonify({"error": "employee not found"}), 404
    conn.commit()
    conn.close()
    return jsonify({"message": "status updated"}), 200

@app.route("/")
def health():
    return jsonify({"service": "employee-enrollment-demo", "status": "ok"})

if __name__ == "__main__":
    os.makedirs(DB_PATH.parent, exist_ok=True)
    init_db()
    app.run(debug=True)
