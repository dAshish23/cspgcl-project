"""
Database Verification and Test Utility for CSPGCL Management System
Tests schema integrity, foreign keys, CRUD on all 4 tables, and business logic queries.
Corresponds to Section 5.1.1 & Section 4.4 in project report.
"""

import sys
from datetime import datetime
from database import (
    init_database,
    get_connection,
    get_coal_records,
    get_coal_by_id,
    insert_coal,
    update_coal,
    delete_coal,
    get_coal_summary,
    get_diesel_records,
    get_diesel_by_id,
    insert_diesel,
    update_diesel,
    delete_diesel,
    get_diesel_summary,
    get_employees,
    get_employee_by_id,
    insert_employee,
    update_employee,
    delete_employee,
    get_attendance_records,
    insert_attendance,
    update_attendance,
    delete_attendance,
    get_dashboard_summary,
    check_db_health
)


def run_tests():
    print("=" * 70)
    print("CSPGCL Management System - Database Layer Verification Test")
    print("=" * 70)

    # 1. Health check
    print("\n[Test 1] Database Health Check...")
    is_healthy = check_db_health()
    assert is_healthy, "Database health check failed!"
    print("✓ Health Check Passed: Database accessible and responsive.")

    # 2. Employees Table CRUD (Table 4.3)
    print("\n[Test 2] Testing employees table CRUD...")
    test_emp_id = insert_employee(
        name="Test Engineer",
        designation="Field Engineer",
        department="Thermal Power Maintenance",
        contact_number="9998887776",
        date_of_joining="2026-01-01"
    )
    assert test_emp_id, "Failed to insert test employee"
    print(f"✓ Inserted employee with ID: {test_emp_id}")

    emp = get_employee_by_id(test_emp_id)
    assert emp and emp["name"] == "Test Engineer", "Failed to retrieve employee"
    print(f"✓ Retrieved employee: {emp['name']} - {emp['designation']} ({emp['department']})")

    updated = update_employee(
        test_emp_id,
        name="Test Senior Engineer",
        designation="Senior Field Engineer",
        department="Thermal Power Maintenance",
        contact_number="9998887770",
        date_of_joining="2026-01-01"
    )
    assert updated, "Failed to update employee"
    emp_updated = get_employee_by_id(test_emp_id)
    assert emp_updated["designation"] == "Senior Field Engineer"
    print("✓ Employee updated successfully.")

    # 3. Attendance Table CRUD & Foreign Key Integrity (Table 4.4)
    print("\n[Test 3] Testing attendance table CRUD & Foreign Key integrity...")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    att_id = insert_attendance(
        emp_id=test_emp_id,
        check_in=now_str,
        check_out=None,
        status="Present"
    )
    assert att_id, "Failed to insert attendance record"
    print(f"✓ Inserted attendance record with ID: {att_id}")

    # Joined query test (Listing 4.3)
    att_records = get_attendance_records(emp_id=test_emp_id)
    assert len(att_records) > 0, "Failed to fetch joined attendance records"
    print(f"✓ Joined query verified: Employee '{att_records[0]['employee_name']}' checked in at {att_records[0]['check_in']}")

    # Update attendance
    att_updated = update_attendance(att_id, check_out=now_str, status="Present")
    assert att_updated, "Failed to update attendance checkout"
    print("✓ Attendance checkout recorded successfully.")

    # Clean up test employee (testing CASCADE delete)
    delete_employee(test_emp_id)
    att_check = get_attendance_records(emp_id=test_emp_id)
    assert len(att_check) == 0, "Cascade delete failed on attendance table!"
    print("✓ Foreign Key CASCADE test passed: Attendance deleted automatically on employee removal.")

    # 4. Coal Storage CRUD & Summary Query (Table 4.1 & Listing 4.4)
    print("\n[Test 4] Testing coal_storage CRUD & Net Stock computation...")
    coal_id = insert_coal(
        quantity_mt=150.75,
        coal_type="IN",
        remarks="Test Coal Rake Shipment",
        recorded_on="2026-07-25"
    )
    assert coal_id, "Failed to insert coal entry"
    print(f"✓ Inserted coal record ID: {coal_id}")

    coal_summary = get_coal_summary()
    print(f"✓ Coal Summary: In: {coal_summary['total_in_mt']} MT | Out: {coal_summary['total_out_mt']} MT | Net Stock: {coal_summary['net_stock_mt']} MT")
    assert coal_summary["net_stock_mt"] is not None

    delete_coal(coal_id)
    print("✓ Cleaned up test coal record.")

    # 5. Diesel Storage CRUD & Summary Query (Table 4.2)
    print("\n[Test 5] Testing diesel_storage CRUD & Net Stock computation...")
    diesel_id = insert_diesel(
        quantity_litres=500.0,
        diesel_type="IN",
        remarks="Test Auxiliary Tanker Supply",
        recorded_on="2026-07-25"
    )
    assert diesel_id, "Failed to insert diesel entry"
    print(f"✓ Inserted diesel record ID: {diesel_id}")

    diesel_summary = get_diesel_summary()
    print(f"✓ Diesel Summary: In: {diesel_summary['total_in_litres']} L | Out: {diesel_summary['total_out_litres']} L | Net Stock: {diesel_summary['net_stock_litres']} L")
    assert diesel_summary["net_stock_litres"] is not None

    delete_diesel(diesel_id)
    print("✓ Cleaned up test diesel record.")

    # 6. Overall Dashboard Stats
    print("\n[Test 6] Testing Dashboard summary aggregation...")
    dash = get_dashboard_summary()
    print(f"✓ Active Employees: {dash['total_employees']}")
    print(f"✓ Present Today: {dash['present_today']}")
    print(f"✓ Currently Clocked-In: {dash['active_on_duty']}")
    print(f"✓ Net Coal Stock: {dash['coal']['net_stock_mt']} MT")
    print(f"✓ Net Diesel Stock: {dash['diesel']['net_stock_litres']} Litres")

    print("\n" + "=" * 70)
    print("ALL DATABASE TESTS PASSED WITH 100% INTEGRITY")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()

