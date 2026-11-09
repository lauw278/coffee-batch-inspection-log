import os
from datetime import date

import psycopg
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)
@app.get("/")
def index():
    return render_template("index.html")
# Read the database connection from environment variables
DATABASE_URL = os.environ.get("DATABASE_URL")

# Allowed quality statuses
ALLOWED_STATUSES = {"Passed", "Needs Review", "Failed"}


# Connect to PostgreSQL
def get_db_connection():
    return psycopg.connect(DATABASE_URL)


# Create the database table
def init_db():
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS coffee_batches (
                id SERIAL PRIMARY KEY,
                batch_code VARCHAR(30) UNIQUE NOT NULL,
                coffee_origin VARCHAR(120) NOT NULL,
                processing_method VARCHAR(80) NOT NULL,
                inspection_date DATE NOT NULL,
                quality_status VARCHAR(30) NOT NULL,
                notes TEXT DEFAULT '',
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)


# Check application and database health
@app.get("/health")
def health():
    try:
        with get_db_connection() as conn:
            conn.execute("SELECT 1")

        return jsonify({
            "status": "healthy",
            "database": "connected"
        }), 200

    except Exception:
        app.logger.exception("Health check failed")
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected"
        }), 503


# Retrieve all coffee inspection records
@app.get("/api/batches")
def get_batches():
    try:
        with get_db_connection() as conn:
            rows = conn.execute("""
                SELECT id, batch_code, coffee_origin,
                       processing_method, inspection_date,
                       quality_status, notes, created_at
                FROM coffee_batches
                ORDER BY id DESC
            """).fetchall()

        batches = [
            {
                "id": row[0],
                "batch_code": row[1],
                "coffee_origin": row[2],
                "processing_method": row[3],
                "inspection_date": row[4].isoformat(),
                "quality_status": row[5],
                "notes": row[6],
                "created_at": row[7].isoformat()
            }
            for row in rows
        ]

        return jsonify(batches), 200

    except Exception:
        app.logger.exception("Could not retrieve batches")
        return jsonify({"error": "Could not retrieve records"}), 500


# Register a new coffee inspection record
@app.post("/api/batches")
def create_batch():
    data = request.get_json(silent=True) or {}

    required_fields = [
        "batch_code",
        "coffee_origin",
        "processing_method",
        "inspection_date",
        "quality_status"
    ]

    for field in required_fields:
        if not isinstance(data.get(field), str) or not data[field].strip():
            return jsonify({
                "error": f"{field} is required"
            }), 400

    batch_code = data["batch_code"].strip()
    coffee_origin = data["coffee_origin"].strip()
    processing_method = data["processing_method"].strip()
    inspection_date = data["inspection_date"].strip()
    quality_status = data["quality_status"].strip()
    notes = data.get("notes", "")

    if len(batch_code) > 30:
        return jsonify({"error": "Batch code is too long"}), 400

    if len(coffee_origin) > 120:
        return jsonify({"error": "Coffee origin is too long"}), 400

    if len(processing_method) > 80:
        return jsonify({"error": "Processing method is too long"}), 400

    if quality_status not in ALLOWED_STATUSES:
        return jsonify({"error": "Invalid quality status"}), 400

    if not isinstance(notes, str):
        return jsonify({"error": "Notes must be text"}), 400

    if len(notes) > 1000:
        return jsonify({"error": "Notes are too long"}), 400

    try:
        date.fromisoformat(inspection_date)
    except ValueError:
        return jsonify({
            "error": "Inspection date must use YYYY-MM-DD format"
        }), 400

    try:
        with get_db_connection() as conn:
            row = conn.execute("""
                INSERT INTO coffee_batches (
                    batch_code,
                    coffee_origin,
                    processing_method,
                    inspection_date,
                    quality_status,
                    notes
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                batch_code,
                coffee_origin,
                processing_method,
                inspection_date,
                quality_status,
                notes.strip()
            )).fetchone()

        return jsonify({
            "message": "Coffee inspection record created",
            "id": row[0],
            "batch_code": batch_code
        }), 201

    except psycopg.errors.UniqueViolation:
        return jsonify({
            "error": "This batch code already exists"
        }), 409

    except Exception:
        app.logger.exception("Could not create batch")
        return jsonify({"error": "Could not create record"}), 500


# Initialize the database when the application starts
init_db()
# Update an existing coffee inspection record
@app.put("/api/batches/<int:batch_id>")
def update_batch(batch_id):
    data = request.get_json(silent=True) or {}

    required_fields = [
        "batch_code",
        "coffee_origin",
        "processing_method",
        "inspection_date",
        "quality_status"
    ]

    for field in required_fields:
        if not isinstance(data.get(field), str) or not data[field].strip():
            return jsonify({"error": f"{field} is required"}), 400

    batch_code = data["batch_code"].strip()
    coffee_origin = data["coffee_origin"].strip()
    processing_method = data["processing_method"].strip()
    inspection_date = data["inspection_date"].strip()
    quality_status = data["quality_status"].strip()
    notes = data.get("notes", "")

    if len(batch_code) > 30 or len(coffee_origin) > 120:
        return jsonify({"error": "Input is too long"}), 400

    if len(processing_method) > 80:
        return jsonify({"error": "Processing method is too long"}), 400

    if quality_status not in ALLOWED_STATUSES:
        return jsonify({"error": "Invalid quality status"}), 400

    if not isinstance(notes, str) or len(notes) > 1000:
        return jsonify({"error": "Invalid notes"}), 400

    try:
        date.fromisoformat(inspection_date)
    except ValueError:
        return jsonify({"error": "Invalid inspection date"}), 400

    try:
        with get_db_connection() as conn:
            row = conn.execute("""
                UPDATE coffee_batches
                SET batch_code = %s,
                    coffee_origin = %s,
                    processing_method = %s,
                    inspection_date = %s,
                    quality_status = %s,
                    notes = %s
                WHERE id = %s
                RETURNING id
            """, (
                batch_code,
                coffee_origin,
                processing_method,
                inspection_date,
                quality_status,
                notes.strip(),
                batch_id
            )).fetchone()

        if row is None:
            return jsonify({"error": "Batch not found"}), 404

        return jsonify({"message": "Record updated"}), 200

    except psycopg.errors.UniqueViolation:
        return jsonify({"error": "Batch code already exists"}), 409

    except Exception:
        app.logger.exception("Could not update batch")
        return jsonify({"error": "Could not update record"}), 500


# Delete an existing coffee inspection record
@app.delete("/api/batches/<int:batch_id>")
def delete_batch(batch_id):
    try:
        with get_db_connection() as conn:
            row = conn.execute("""
                DELETE FROM coffee_batches
                WHERE id = %s
                RETURNING id
            """, (batch_id,)).fetchone()

        if row is None:
            return jsonify({"error": "Batch not found"}), 404

        return jsonify({"message": "Record deleted"}), 200

    except Exception:
        app.logger.exception("Could not delete batch")
        return jsonify({"error": "Could not delete record"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
