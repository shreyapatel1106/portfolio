from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_PATH = "/tmp/portfolio.db"  # Fixed for Render

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT,
            message TEXT NOT NULL,
            submitted_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/contact", methods=["POST"])
def contact():
    data    = request.get_json()
    name    = data.get("name", "").strip()
    email   = data.get("email", "").strip()
    subject = data.get("subject", "").strip()
    message = data.get("message", "").strip()

    if not name or not email or not message:
        return jsonify({
            "success": False,
            "error": "Name, email and message are required."
        }), 400

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO contacts (name, email, subject, message, submitted_at) VALUES (?,?,?,?,?)",
            (name, email, subject, message, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        return jsonify({
            "success": True,
            "message": "Message received! I'll get back to you soon."
        })
    except Exception as e:
        print(f"DB Error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/messages")
def messages():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, name, email, subject, message, submitted_at FROM contacts ORDER BY submitted_at DESC")
        rows = [
            {
                "id": r[0],
                "name": r[1],
                "email": r[2],
                "subject": r[3],
                "message": r[4],
                "submitted_at": r[5]
            }
            for r in c.fetchall()
        ]
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
