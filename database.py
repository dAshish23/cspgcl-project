"""
Database access module for CSPGCL Management System
Supports SQLite (default) and MySQL via environment variables.
Enforces 3NF schema, foreign key constraints, and parameterized queries.
"""

import os
import sqlite3
from datetime import datetime

DB_FILE = os.environ.get("DB_FILE", os.path.join(os.path.dirname(__file__), "cspgcl.db"))
DB_TYPE = os.environ.get("DB_TYPE", "sqlite").lower()


def get_connection():
    """Returns a database connection with row factory configured."""
    if DB_TYPE == "sqlite":
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        # Enable foreign keys in SQLite
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    elif DB_TYPE == "mysql":
        import pymysql
        conn = pymysql.connect(
            host=os.environ.get("MYSQL_HOST", "localhost"),
            user=os.environ.get("MYSQL_USER", "root"),
            password=os.environ.get("MYSQL_PASSWORD", ""),
            database=os.environ.get("MYSQL_DB", "cspgcl_db"),
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )
        return conn
    else:
        raise ValueError(f"Unsupported DB_TYPE: {DB_TYPE}")


def init_database():
    """Initialize database tables according to Chapter IV 3NF specifications."""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = get_connection()
    try:
        if DB_TYPE == "sqlite":
            conn.executescript(schema_sql)
            conn.commit()
        else:
            # For MySQL, split statements
            cursor = conn.cursor()
            for stmt in schema_sql.split(";"):
                stmt = stmt.strip()
                if stmt:
                    cursor.execute(stmt)
            conn.commit()
    finally:
        conn.close()


def row_to_dict(row):
    """Convert SQLite Row or dict to standard python dictionary."""
    if row is None:
        return None
    if isinstance(row, dict):
        return row
    return {key: row[key] for key in row.keys()}


# ==============================================================================
# Coal Storage Operations (Table 4.1, Listing 4.2 & Listing 4.4)
# ==============================================================================

def get_coal_records(limit=100):
    """Retrieve coal storage entries ordered by recorded_on DESC, created_at DESC."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, quantity_mt, type, remarks, recorded_on, created_at, updated_at "
            "FROM coal_storage ORDER BY recorded_on DESC, id DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        return [row_to_dict(r) for r in rows]
    finally:
        conn.close()


def get_coal_by_id(coal_id):
    """Retrieve single coal storage entry."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM coal_storage WHERE id = ?", (coal_id,))
        row = cursor.fetchone()
        return row_to_dict(row)
    finally:
        conn.close()


def insert_coal(quantity_mt, coal_type, remarks, recorded_on):
    """Insert a new coal transaction record (IN or OUT)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO coal_storage (quantity_mt, type, remarks, recorded_on, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (float(quantity_mt), coal_type.upper(), remarks, recorded_on, now, now)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update_coal(coal_id, quantity_mt, coal_type, remarks, recorded_on):
    """Update existing coal transaction record."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "UPDATE coal_storage SET quantity_mt = ?, type = ?, remarks = ?, recorded_on = ?, updated_at = ? "
            "WHERE id = ?",
            (float(quantity_mt), coal_type.upper(), remarks, recorded_on, now, coal_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def delete_coal(coal_id):
    """Delete a coal transaction record."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM coal_storage WHERE id = ?", (coal_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def get_coal_summary():
    """
    Compute total incoming, outgoing, and net stock in Metric Tonnes (Listing 4.4).
    Net Stock = SUM(IN) - SUM(OUT)
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN type = 'IN' THEN quantity_mt ELSE 0 END), 0) AS total_in_mt,
                COALESCE(SUM(CASE WHEN type = 'OUT' THEN quantity_mt ELSE 0 END), 0) AS total_out_mt,
                COALESCE(SUM(CASE WHEN type = 'IN' THEN quantity_mt ELSE 0 END) -
                         SUM(CASE WHEN type = 'OUT' THEN quantity_mt ELSE 0 END), 0) AS net_stock_mt,
                COUNT(*) as total_transactions
            FROM coal_storage
        """)
        row = cursor.fetchone()
        return row_to_dict(row)
    finally:
        conn.close()


# ==============================================================================
# Diesel Storage Operations (Table 4.2 & Listing 4.2)
# ==============================================================================

def get_diesel_records(limit=100):
    """Retrieve diesel storage entries ordered by recorded_on DESC, id DESC."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, quantity_litres, type, remarks, recorded_on, created_at, updated_at "
            "FROM diesel_storage ORDER BY recorded_on DESC, id DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        return [row_to_dict(r) for r in rows]
    finally:
        conn.close()


def get_diesel_by_id(diesel_id):
    """Retrieve single diesel storage entry."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM diesel_storage WHERE id = ?", (diesel_id,))
        row = cursor.fetchone()
        return row_to_dict(row)
    finally:
        conn.close()


def insert_diesel(quantity_litres, diesel_type, remarks, recorded_on):
    """Insert a new diesel transaction record (IN or OUT)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO diesel_storage (quantity_litres, type, remarks, recorded_on, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (float(quantity_litres), diesel_type.upper(), remarks, recorded_on, now, now)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update_diesel(diesel_id, quantity_litres, diesel_type, remarks, recorded_on):
    """Update existing diesel transaction record."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "UPDATE diesel_storage SET quantity_litres = ?, type = ?, remarks = ?, recorded_on = ?, updated_at = ? "
            "WHERE id = ?",
            (float(quantity_litres), diesel_type.upper(), remarks, recorded_on, now, diesel_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def delete_diesel(diesel_id):
    """Delete a diesel transaction record."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM diesel_storage WHERE id = ?", (diesel_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def get_diesel_summary():
    """
    Compute total incoming, outgoing, and net stock in Litres.
    Net Stock = SUM(IN) - SUM(OUT)
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN type = 'IN' THEN quantity_litres ELSE 0 END), 0) AS total_in_litres,
                COALESCE(SUM(CASE WHEN type = 'OUT' THEN quantity_litres ELSE 0 END), 0) AS total_out_litres,
                COALESCE(SUM(CASE WHEN type = 'IN' THEN quantity_litres ELSE 0 END) -
                         SUM(CASE WHEN type = 'OUT' THEN quantity_litres ELSE 0 END), 0) AS net_stock_litres,
                COUNT(*) as total_transactions
            FROM diesel_storage
        """)
        row = cursor.fetchone()
        return row_to_dict(row)
    finally:
        conn.close()


# ==============================================================================
# Employees Operations (Table 4.3 & Listing 4.1)
# ==============================================================================

def get_employees():
    """Retrieve all employee records."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT emp_id, name, designation, department, contact_number, date_of_joining, created_at "
            "FROM employees ORDER BY emp_id ASC"
        )
        rows = cursor.fetchall()
        return [row_to_dict(r) for r in rows]
    finally:
        conn.close()


def get_employee_by_id(emp_id):
    """Retrieve single employee by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT emp_id, name, designation, department, contact_number, date_of_joining, created_at "
            "FROM employees WHERE emp_id = ?",
            (emp_id,)
        )
        row = cursor.fetchone()
        return row_to_dict(row)
    finally:
        conn.close()


def insert_employee(name, designation=None, department=None, contact_number=None, date_of_joining=None):
    """Insert a new employee."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO employees (name, designation, department, contact_number, date_of_joining, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (name.strip(), designation, department, contact_number, date_of_joining, now)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update_employee(emp_id, name, designation=None, department=None, contact_number=None, date_of_joining=None):
    """Update employee details."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE employees SET name = ?, designation = ?, department = ?, contact_number = ?, date_of_joining = ? "
            "WHERE emp_id = ?",
            (name.strip(), designation, department, contact_number, date_of_joining, emp_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def delete_employee(emp_id):
    """Delete employee by ID (cascades to attendance)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM employees WHERE emp_id = ?", (emp_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


# ==============================================================================
# Attendance Operations (Table 4.4, Listing 4.1 & Listing 4.3)
# ==============================================================================

def get_attendance_records(emp_id=None, date=None, status=None, limit=200):
    """
    Retrieve attendance records joined with employee details (Listing 4.3).
    SELECT e.name, e.department, a.check_in, a.check_out, a.status
    FROM attendance a JOIN employees e ON a.emp_id = e.emp_id ...
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = (
            "SELECT a.attendance_id, a.emp_id, a.check_in, a.check_out, a.status, a.created_at, "
            "e.name as employee_name, e.designation, e.department "
            "FROM attendance a "
            "JOIN employees e ON a.emp_id = e.emp_id "
            "WHERE 1=1 "
        )
        params = []
        if emp_id:
            query += " AND a.emp_id = ?"
            params.append(emp_id)
        if date:
            query += " AND DATE(a.check_in) = ?"
            params.append(date)
        if status:
            query += " AND a.status = ?"
            params.append(status)

        query += " ORDER BY a.check_in DESC, a.attendance_id DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [row_to_dict(r) for r in rows]
    finally:
        conn.close()


def get_attendance_by_id(attendance_id):
    """Retrieve single attendance record by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT a.*, e.name as employee_name, e.designation, e.department "
            "FROM attendance a "
            "JOIN employees e ON a.emp_id = e.emp_id "
            "WHERE a.attendance_id = ?",
            (attendance_id,)
        )
        row = cursor.fetchone()
        return row_to_dict(row)
    finally:
        conn.close()


def insert_attendance(emp_id, check_in, check_out=None, status="Present"):
    """Insert new attendance entry."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO attendance (emp_id, check_in, check_out, status, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (emp_id, check_in, check_out, status or "Present", now)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update_attendance(attendance_id, check_in=None, check_out=None, status=None):
    """Update attendance entry (e.g., set checkout time or modify status)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Fetch current record first
        cursor.execute("SELECT * FROM attendance WHERE attendance_id = ?", (attendance_id,))
        cur = cursor.fetchone()
        if not cur:
            return False

        new_check_in = check_in if check_in is not None else cur["check_in"]
        new_check_out = check_out if check_out is not None else cur["check_out"]
        new_status = status if status is not None else cur["status"]

        cursor.execute(
            "UPDATE attendance SET check_in = ?, check_out = ?, status = ? WHERE attendance_id = ?",
            (new_check_in, new_check_out, new_status, attendance_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def delete_attendance(attendance_id):
    """Delete attendance record."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM attendance WHERE attendance_id = ?", (attendance_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def quick_check_in(emp_id):
    """Records instant check-in for an employee at current time."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return insert_attendance(emp_id=emp_id, check_in=now_str, check_out=None, status="Present")


def quick_check_out(emp_id):
    """Finds the most recent open check-in today for this employee and sets check_out to now."""
    today = datetime.now().strftime("%Y-%m-%d")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT attendance_id FROM attendance "
            "WHERE emp_id = ? AND DATE(check_in) = ? AND check_out IS NULL "
            "ORDER BY check_in DESC LIMIT 1",
            (emp_id, today)
        )
        row = cursor.fetchone()
        if row:
            att_id = row["attendance_id"]
            cursor.execute("UPDATE attendance SET check_out = ? WHERE attendance_id = ?", (now_str, att_id))
            conn.commit()
            return att_id
        return None
    finally:
        conn.close()


# ==============================================================================
# Dashboard Summary & System Health
# ==============================================================================

def get_dashboard_summary():
    """Compile comprehensive stats for Home Dashboard (Fig 6.1)."""
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Employees count
        cursor.execute("SELECT COUNT(*) as count FROM employees")
        total_employees = cursor.fetchone()["count"]

        # Today's attendance
        cursor.execute("SELECT COUNT(DISTINCT emp_id) as count FROM attendance WHERE DATE(check_in) = ?", (today,))
        present_today = cursor.fetchone()["count"]

        # Active clocked-in right now (check_out IS NULL)
        cursor.execute("SELECT COUNT(*) as count FROM attendance WHERE DATE(check_in) = ? AND check_out IS NULL", (today,))
        active_on_duty = cursor.fetchone()["count"]

        # Coal summary
        cursor.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN type = 'IN' THEN quantity_mt ELSE 0 END), 0) AS total_in_mt,
                COALESCE(SUM(CASE WHEN type = 'OUT' THEN quantity_mt ELSE 0 END), 0) AS total_out_mt,
                COALESCE(SUM(CASE WHEN type = 'IN' THEN quantity_mt ELSE 0 END) -
                         SUM(CASE WHEN type = 'OUT' THEN quantity_mt ELSE 0 END), 0) AS net_stock_mt,
                COUNT(*) as tx_count
            FROM coal_storage
        """)
        coal_stat = row_to_dict(cursor.fetchone())

        # Diesel summary
        cursor.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN type = 'IN' THEN quantity_litres ELSE 0 END), 0) AS total_in_litres,
                COALESCE(SUM(CASE WHEN type = 'OUT' THEN quantity_litres ELSE 0 END), 0) AS total_out_litres,
                COALESCE(SUM(CASE WHEN type = 'IN' THEN quantity_litres ELSE 0 END) -
                         SUM(CASE WHEN type = 'OUT' THEN quantity_litres ELSE 0 END), 0) AS net_stock_litres,
                COUNT(*) as tx_count
            FROM diesel_storage
        """)
        diesel_stat = row_to_dict(cursor.fetchone())

        return {
            "total_employees": total_employees,
            "present_today": present_today,
            "active_on_duty": active_on_duty,
            "coal": coal_stat,
            "diesel": diesel_stat,
            "system_date": today
        }
    finally:
        conn.close()


def check_db_health():
    """Verify database connection and integrity."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 AS ok")
        row = cursor.fetchone()
        return bool(row and row["ok"] == 1)
    except Exception:
        return False
    finally:
        conn.close()

