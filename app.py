"""
CSPGCL Management System - Flask REST API Backend & Web Application
Chhattisgarh State Power Generation Company Limited (CSPGCL), Korba
Vocational Training Project

Exposes resource-oriented RESTful API endpoints (Chapter V, Table 5.1)
and serves the responsive web interface.
"""

import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template

import database as db

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


# ==============================================================================
# Web Interface Route
# ==============================================================================

@app.route("/")
def index():
    """Renders the main single-page application dashboard."""
    return render_template("index.html")


# ==============================================================================
# Health Check Endpoint (Table 5.1)
# ==============================================================================

@app.route("/api/health", methods=["GET"])
def health_check():
    """
    GET /api/health
    Returns system status, active database engine, and timestamp.
    """
    is_db_ok = db.check_db_health()
    status_code = 200 if is_db_ok else 500
    return jsonify({
        "status": "healthy" if is_db_ok else "unhealthy",
        "database": "connected" if is_db_ok else "disconnected",
        "db_type": db.DB_TYPE,
        "organization": "Chhattisgarh State Power Generation Company Limited (CSPGCL)",
        "plant": "Korba East Thermal Power Station",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }), status_code


# ==============================================================================
# Overall Dashboard Summary
# ==============================================================================

@app.route("/api/summary", methods=["GET"])
def get_summary():
    """
    GET /api/summary
    Returns key aggregated statistics for dashboard cards and charts (Fig 6.1).
    """
    try:
        data = db.get_dashboard_summary()
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==============================================================================
# Coal Storage Endpoints (Table 5.1)
# ==============================================================================

@app.route("/api/coal", methods=["GET", "POST"])
def coal_collection():
    """
    GET /api/coal: Retrieve coal inventory log + net stock summary
    POST /api/coal: Add coal stock transaction (IN/OUT)
    """
    if request.method == "GET":
        try:
            records = db.get_coal_records()
            summary = db.get_coal_summary()
            return jsonify({
                "success": True,
                "summary": summary,
                "count": len(records),
                "data": records
            }), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    elif request.method == "POST":
        payload = request.get_json(silent=True) or {}
        quantity_mt = payload.get("quantity_mt")
        coal_type = payload.get("type", "").strip().upper()
        remarks = payload.get("remarks", "").strip()
        recorded_on = payload.get("recorded_on", datetime.now().strftime("%Y-%m-%d"))

        # Validation
        if quantity_mt is None:
            return jsonify({"success": False, "error": "Field 'quantity_mt' is required."}), 400
        try:
            qty_float = float(quantity_mt)
            if qty_float <= 0:
                return jsonify({"success": False, "error": "'quantity_mt' must be greater than zero."}), 400
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "'quantity_mt' must be a valid numeric value."}), 400

        if coal_type not in ["IN", "OUT"]:
            return jsonify({"success": False, "error": "Field 'type' must be either 'IN' or 'OUT'."}), 400

        try:
            new_id = db.insert_coal(qty_float, coal_type, remarks, recorded_on)
            new_record = db.get_coal_by_id(new_id)
            return jsonify({
                "success": True,
                "message": "Coal storage record created successfully.",
                "data": new_record
            }), 201
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/coal/<int:coal_id>", methods=["GET", "PUT", "DELETE"])
def coal_item(coal_id):
    """
    GET /api/coal/<id>: Fetch specific coal entry
    PUT /api/coal/<id>: Update coal entry
    DELETE /api/coal/<id>: Delete coal entry
    """
    existing = db.get_coal_by_id(coal_id)
    if not existing:
        return jsonify({"success": False, "error": f"Coal record with ID {coal_id} not found."}), 404

    if request.method == "GET":
        return jsonify({"success": True, "data": existing}), 200

    elif request.method == "PUT":
        payload = request.get_json(silent=True) or {}
        quantity_mt = payload.get("quantity_mt", existing["quantity_mt"])
        coal_type = payload.get("type", existing["type"]).strip().upper()
        remarks = payload.get("remarks", existing["remarks"])
        recorded_on = payload.get("recorded_on", existing["recorded_on"])

        try:
            qty_float = float(quantity_mt)
            if qty_float <= 0:
                return jsonify({"success": False, "error": "'quantity_mt' must be positive."}), 400
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Invalid quantity."}), 400

        if coal_type not in ["IN", "OUT"]:
            return jsonify({"success": False, "error": "Type must be 'IN' or 'OUT'."}), 400

        try:
            db.update_coal(coal_id, qty_float, coal_type, remarks, recorded_on)
            updated = db.get_coal_by_id(coal_id)
            return jsonify({"success": True, "message": "Coal record updated successfully.", "data": updated}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    elif request.method == "DELETE":
        try:
            db.delete_coal(coal_id)
            return jsonify({"success": True, "message": f"Coal record {coal_id} deleted successfully."}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500


# ==============================================================================
# Diesel Storage Endpoints (Table 5.1)
# ==============================================================================

@app.route("/api/diesel", methods=["GET", "POST"])
def diesel_collection():
    """
    GET /api/diesel: Retrieve diesel inventory log + net stock summary
    POST /api/diesel: Add diesel stock transaction (IN/OUT)
    """
    if request.method == "GET":
        try:
            records = db.get_diesel_records()
            summary = db.get_diesel_summary()
            return jsonify({
                "success": True,
                "summary": summary,
                "count": len(records),
                "data": records
            }), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    elif request.method == "POST":
        payload = request.get_json(silent=True) or {}
        quantity_litres = payload.get("quantity_litres")
        diesel_type = payload.get("type", "").strip().upper()
        remarks = payload.get("remarks", "").strip()
        recorded_on = payload.get("recorded_on", datetime.now().strftime("%Y-%m-%d"))

        # Validation
        if quantity_litres is None:
            return jsonify({"success": False, "error": "Field 'quantity_litres' is required."}), 400
        try:
            qty_float = float(quantity_litres)
            if qty_float <= 0:
                return jsonify({"success": False, "error": "'quantity_litres' must be greater than zero."}), 400
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "'quantity_litres' must be a valid numeric value."}), 400

        if diesel_type not in ["IN", "OUT"]:
            return jsonify({"success": False, "error": "Field 'type' must be either 'IN' or 'OUT'."}), 400

        try:
            new_id = db.insert_diesel(qty_float, diesel_type, remarks, recorded_on)
            new_record = db.get_diesel_by_id(new_id)
            return jsonify({
                "success": True,
                "message": "Diesel storage record created successfully.",
                "data": new_record
            }), 201
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/diesel/<int:diesel_id>", methods=["GET", "PUT", "DELETE"])
def diesel_item(diesel_id):
    """
    GET /api/diesel/<id>: Fetch specific diesel entry
    PUT /api/diesel/<id>: Update diesel entry
    DELETE /api/diesel/<id>: Delete diesel entry
    """
    existing = db.get_diesel_by_id(diesel_id)
    if not existing:
        return jsonify({"success": False, "error": f"Diesel record with ID {diesel_id} not found."}), 404

    if request.method == "GET":
        return jsonify({"success": True, "data": existing}), 200

    elif request.method == "PUT":
        payload = request.get_json(silent=True) or {}
        quantity_litres = payload.get("quantity_litres", existing["quantity_litres"])
        diesel_type = payload.get("type", existing["type"]).strip().upper()
        remarks = payload.get("remarks", existing["remarks"])
        recorded_on = payload.get("recorded_on", existing["recorded_on"])

        try:
            qty_float = float(quantity_litres)
            if qty_float <= 0:
                return jsonify({"success": False, "error": "'quantity_litres' must be positive."}), 400
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Invalid quantity."}), 400

        if diesel_type not in ["IN", "OUT"]:
            return jsonify({"success": False, "error": "Type must be 'IN' or 'OUT'."}), 400

        try:
            db.update_diesel(diesel_id, qty_float, diesel_type, remarks, recorded_on)
            updated = db.get_diesel_by_id(diesel_id)
            return jsonify({"success": True, "message": "Diesel record updated successfully.", "data": updated}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    elif request.method == "DELETE":
        try:
            db.delete_diesel(diesel_id)
            return jsonify({"success": True, "message": f"Diesel record {diesel_id} deleted successfully."}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500


# ==============================================================================
# Employees Endpoints (Table 5.1 & Listing 5.1)
# ==============================================================================

@app.route("/api/employees", methods=["GET", "POST"])
def employees_collection():
    """
    GET /api/employees: List all employees
    POST /api/employees: Register a new employee (Listing 5.1)
    """
    if request.method == "GET":
        try:
            records = db.get_employees()
            return jsonify({"success": True, "count": len(records), "data": records}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    elif request.method == "POST":
        payload = request.get_json(silent=True) or {}
        name = payload.get("name", "").strip()
        designation = payload.get("designation", "").strip() or None
        department = payload.get("department", "").strip() or None
        contact_number = payload.get("contact_number", "").strip() or None
        date_of_joining = payload.get("date_of_joining", "").strip() or None

        if not name:
            return jsonify({"success": False, "error": "Field 'name' is required."}), 400

        try:
            new_id = db.insert_employee(name, designation, department, contact_number, date_of_joining)
            new_employee = db.get_employee_by_id(new_id)
            return jsonify({
                "success": True,
                "message": "Employee registered successfully.",
                "data": new_employee
            }), 201
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/employees/<int:emp_id>", methods=["GET", "PUT", "DELETE"])
def employee_item(emp_id):
    """
    GET /api/employees/<id>: Fetch single employee + attendance history
    PUT /api/employees/<id>: Update employee details
    DELETE /api/employees/<id>: Remove employee (cascade deletes attendance)
    """
    existing = db.get_employee_by_id(emp_id)
    if not existing:
        return jsonify({"success": False, "error": f"Employee ID {emp_id} not found."}), 404

    if request.method == "GET":
        history = db.get_attendance_records(emp_id=emp_id, limit=50)
        return jsonify({
            "success": True,
            "data": existing,
            "attendance_history": history
        }), 200

    elif request.method == "PUT":
        payload = request.get_json(silent=True) or {}
        name = payload.get("name", existing["name"]).strip()
        designation = payload.get("designation", existing["designation"])
        department = payload.get("department", existing["department"])
        contact_number = payload.get("contact_number", existing["contact_number"])
        date_of_joining = payload.get("date_of_joining", existing["date_of_joining"])

        if not name:
            return jsonify({"success": False, "error": "Field 'name' cannot be empty."}), 400

        try:
            db.update_employee(emp_id, name, designation, department, contact_number, date_of_joining)
            updated = db.get_employee_by_id(emp_id)
            return jsonify({"success": True, "message": "Employee updated successfully.", "data": updated}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    elif request.method == "DELETE":
        try:
            db.delete_employee(emp_id)
            return jsonify({"success": True, "message": f"Employee {emp_id} deleted successfully."}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500


# ==============================================================================
# Attendance Endpoints (Table 5.1 & Listing 5.2)
# ==============================================================================

@app.route("/api/attendance", methods=["GET", "POST"])
def attendance_collection():
    """
    GET /api/attendance: List attendance records joined with employees.
                         Supports query params: ?emp_id=1&date=YYYY-MM-DD&status=Present
    POST /api/attendance: Record attendance check-in/out (Listing 5.2)
    """
    if request.method == "GET":
        try:
            emp_id = request.args.get("emp_id", type=int)
            date = request.args.get("date", type=str)
            status = request.args.get("status", type=str)
            limit = request.args.get("limit", default=200, type=int)

            records = db.get_attendance_records(emp_id=emp_id, date=date, status=status, limit=limit)
            return jsonify({"success": True, "count": len(records), "data": records}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    elif request.method == "POST":
        payload = request.get_json(silent=True) or {}
        emp_id = payload.get("emp_id")
        check_in = payload.get("check_in")
        check_out = payload.get("check_out")
        status = payload.get("status", "Present")

        if not emp_id:
            return jsonify({"success": False, "error": "Field 'emp_id' is required."}), 400

        # Validate employee existence
        if not db.get_employee_by_id(emp_id):
            return jsonify({"success": False, "error": f"Employee with emp_id={emp_id} does not exist."}), 404

        if not check_in:
            check_in = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Format ISO strings if needed (e.g. 2026-07-25T09:00:00 -> 2026-07-25 09:00:00)
        if isinstance(check_in, str):
            check_in = check_in.replace("T", " ")
        if isinstance(check_out, str):
            check_out = check_out.replace("T", " ")

        try:
            new_id = db.insert_attendance(emp_id, check_in, check_out, status)
            new_rec = db.get_attendance_by_id(new_id)
            return jsonify({
                "success": True,
                "message": "Attendance record created successfully.",
                "data": new_rec
            }), 201
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/attendance/<int:att_id>", methods=["GET", "PUT", "DELETE"])
def attendance_item(att_id):
    """
    GET /api/attendance/<id>: Fetch specific attendance record
    PUT /api/attendance/<id>: Update attendance record (check_out, status, check_in)
    DELETE /api/attendance/<id>: Delete attendance record
    """
    existing = db.get_attendance_by_id(att_id)
    if not existing:
        return jsonify({"success": False, "error": f"Attendance record {att_id} not found."}), 404

    if request.method == "GET":
        return jsonify({"success": True, "data": existing}), 200

    elif request.method == "PUT":
        payload = request.get_json(silent=True) or {}
        check_in = payload.get("check_in")
        check_out = payload.get("check_out")
        status = payload.get("status")

        if isinstance(check_in, str):
            check_in = check_in.replace("T", " ")
        if isinstance(check_out, str):
            check_out = check_out.replace("T", " ")

        try:
            db.update_attendance(att_id, check_in=check_in, check_out=check_out, status=status)
            updated = db.get_attendance_by_id(att_id)
            return jsonify({"success": True, "message": "Attendance record updated successfully.", "data": updated}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    elif request.method == "DELETE":
        try:
            db.delete_attendance(att_id)
            return jsonify({"success": True, "message": f"Attendance record {att_id} deleted successfully."}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/attendance/check-in", methods=["POST"])
def quick_checkin_route():
    """Quick one-click check-in helper endpoint."""
    payload = request.get_json(silent=True) or {}
    emp_id = payload.get("emp_id")
    if not emp_id:
        return jsonify({"success": False, "error": "emp_id is required."}), 400
    if not db.get_employee_by_id(emp_id):
        return jsonify({"success": False, "error": f"Employee {emp_id} does not exist."}), 404

    try:
        att_id = db.quick_check_in(emp_id)
        record = db.get_attendance_by_id(att_id)
        return jsonify({"success": True, "message": "Clocked in successfully.", "data": record}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/attendance/check-out", methods=["POST"])
def quick_checkout_route():
    """Quick one-click check-out helper endpoint."""
    payload = request.get_json(silent=True) or {}
    emp_id = payload.get("emp_id")
    if not emp_id:
        return jsonify({"success": False, "error": "emp_id is required."}), 400

    try:
        att_id = db.quick_check_out(emp_id)
        if not att_id:
            return jsonify({"success": False, "error": "No open check-in found today for this employee."}), 404
        record = db.get_attendance_by_id(att_id)
        return jsonify({"success": True, "message": "Clocked out successfully.", "data": record}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==============================================================================
# Diagnostics & SQL Query Viewer (Corresponds to Fig 6.6 & Fig 6.8)
# ==============================================================================

@app.route("/api/db-tables", methods=["GET"])
def db_tables_info():
    """Returns database schema information and row counts (Fig 6.6)."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        tables = ["coal_storage", "diesel_storage", "employees", "attendance"]
        details = {}
        for t in tables:
            cursor.execute(f"SELECT COUNT(*) as count FROM {t}")
            cnt = cursor.fetchone()["count"]
            cursor.execute(f"PRAGMA table_info({t})")
            columns = [db.row_to_dict(col) for col in cursor.fetchall()]
            details[t] = {
                "row_count": cnt,
                "columns": columns
            }
        return jsonify({"success": True, "tables": details}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()


@app.route("/api/raw-query", methods=["POST"])
def execute_readonly_query():
    """
    Safely executes read-only SQL queries to reproduce Fig 6.8 'Database Query Output'.
    Only SELECT statements are permitted.
    """
    payload = request.get_json(silent=True) or {}
    query = payload.get("query", "").strip()

    if not query:
        return jsonify({"success": False, "error": "Query parameter cannot be empty."}), 400

    if not query.lower().startswith("select"):
        return jsonify({"success": False, "error": "Only SELECT queries are allowed in this utility."}), 403

    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        dict_rows = [db.row_to_dict(r) for r in rows]
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        return jsonify({
            "success": True,
            "query": query,
            "columns": columns,
            "row_count": len(dict_rows),
            "data": dict_rows
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
    finally:
        conn.close()


if __name__ == "__main__":
    # Ensure database is initialized before starting server
    if not os.path.exists(db.DB_FILE):
        print("Database file not found. Initializing...")
        from init_db import seed_database
        seed_database()

    port = int(os.environ.get("PORT", 5000))
    print(f"Starting CSPGCL Management System on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)

