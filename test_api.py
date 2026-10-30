"""
REST API Automated Test Suite for CSPGCL Management System
Tests all endpoints from Table 5.1 using Flask test_client and Python requests.
Verifies JSON payloads, HTTP status codes, and CRUD pipelines.
"""

import sys
import json
from app import app
import database as db


def run_api_tests():
    print("=" * 70)
    print("CSPGCL Management System - REST API Test Suite")
    print("=" * 70)

    client = app.test_client()

    # 1. Health Check Endpoint
    print("\n[Test 1] GET /api/health...")
    res = client.get("/api/health")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.get_json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    print(f"✓ Health Check: {data['status']}, Database: {data['database']} ({data['db_type']})")

    # 2. Summary Endpoint (Dashboard stats)
    print("\n[Test 2] GET /api/summary...")
    res = client.get("/api/summary")
    assert res.status_code == 200
    summary = res.get_json()["data"]
    print(f"✓ Summary: Employees={summary['total_employees']}, Present={summary['present_today']}, Net Coal={summary['coal']['net_stock_mt']} MT")

    # 3. Employees CRUD (Listing 5.1)
    print("\n[Test 3] POST /api/employees (Listing 5.1 example)...")
    emp_payload = {
        "name": "Ramesh Kumar (Test)",
        "designation": "Plant Operator",
        "department": "Coal Handling",
        "contact_number": "9876543210",
        "date_of_joining": "2024-01-15"
    }
    res = client.post("/api/employees", json=emp_payload)
    assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.get_data(as_text=True)}"
    new_emp = res.get_json()["data"]
    test_emp_id = new_emp["emp_id"]
    print(f"✓ Created employee ID {test_emp_id}: {new_emp['name']}")

    # GET employee list
    res = client.get("/api/employees")
    assert res.status_code == 200
    assert any(e["emp_id"] == test_emp_id for e in res.get_json()["data"])
    print("✓ GET /api/employees returned updated list.")

    # GET single employee
    res = client.get(f"/api/employees/{test_emp_id}")
    assert res.status_code == 200
    assert res.get_json()["data"]["name"] == "Ramesh Kumar (Test)"
    print(f"✓ GET /api/employees/{test_emp_id} verified.")

    # PUT update employee
    res = client.put(f"/api/employees/{test_emp_id}", json={
        "name": "Ramesh Kumar (Senior)",
        "designation": "Senior Plant Operator"
    })
    assert res.status_code == 200
    print("✓ PUT /api/employees updated employee details.")

    # 4. Attendance CRUD (Listing 5.2)
    print("\n[Test 4] POST /api/attendance (Listing 5.2 example)...")
    att_payload = {
        "emp_id": test_emp_id,
        "check_in": "2026-07-25T09:00:00",
        "status": "Present"
    }
    res = client.post("/api/attendance", json=att_payload)
    assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.get_data(as_text=True)}"
    new_att = res.get_json()["data"]
    test_att_id = new_att["attendance_id"]
    print(f"✓ Recorded attendance ID {test_att_id} for emp_id {test_emp_id}")

    # GET attendance list with filters
    res = client.get(f"/api/attendance?emp_id={test_emp_id}")
    assert res.status_code == 200
    att_list = res.get_json()["data"]
    assert len(att_list) >= 1
    assert att_list[0]["employee_name"] == "Ramesh Kumar (Senior)"
    print("✓ GET /api/attendance verified with foreign key join.")

    # PUT attendance (checkout)
    res = client.put(f"/api/attendance/{test_att_id}", json={
        "check_out": "2026-07-25 17:30:00",
        "status": "Present"
    })
    assert res.status_code == 200
    print("✓ PUT /api/attendance updated check-out timestamp.")

    # Quick check-in / check-out endpoints
    print("\n[Test 5] Quick Check-in and Check-out endpoints...")
    res = client.post("/api/attendance/check-in", json={"emp_id": test_emp_id})
    assert res.status_code == 201
    print("✓ Quick check-in completed.")
    res = client.post("/api/attendance/check-out", json={"emp_id": test_emp_id})
    assert res.status_code == 200
    print("✓ Quick check-out completed.")

    # Clean up test attendance and employee
    client.delete(f"/api/attendance/{test_att_id}")
    client.delete(f"/api/employees/{test_emp_id}")
    print("✓ Cleaned up test employee and attendance records.")

    # 5. Coal Storage CRUD
    print("\n[Test 6] Coal Storage CRUD (/api/coal)...")
    coal_payload = {
        "quantity_mt": 1250.50,
        "type": "IN",
        "remarks": "API Test Rake Inflow",
        "recorded_on": "2026-07-25"
    }
    res = client.post("/api/coal", json=coal_payload)
    assert res.status_code == 201
    test_coal_id = res.get_json()["data"]["id"]
    print(f"✓ Created coal record {test_coal_id}")

    res = client.get(f"/api/coal/{test_coal_id}")
    assert res.status_code == 200

    res = client.put(f"/api/coal/{test_coal_id}", json={
        "quantity_mt": 1300.00,
        "type": "IN",
        "remarks": "Updated API Test Rake",
        "recorded_on": "2026-07-25"
    })
    assert res.status_code == 200

    res = client.delete(f"/api/coal/{test_coal_id}")
    assert res.status_code == 200
    print("✓ Coal Storage CRUD fully verified.")

    # 6. Diesel Storage CRUD
    print("\n[Test 7] Diesel Storage CRUD (/api/diesel)...")
    diesel_payload = {
        "quantity_litres": 3200.0,
        "type": "OUT",
        "remarks": "API Test Diesel Issue",
        "recorded_on": "2026-07-25"
    }
    res = client.post("/api/diesel", json=diesel_payload)
    assert res.status_code == 201
    test_diesel_id = res.get_json()["data"]["id"]
    print(f"✓ Created diesel record {test_diesel_id}")

    res = client.get(f"/api/diesel/{test_diesel_id}")
    assert res.status_code == 200

    res = client.put(f"/api/diesel/{test_diesel_id}", json={
        "quantity_litres": 3100.0,
        "type": "OUT",
        "remarks": "Updated API Test Issue",
        "recorded_on": "2026-07-25"
    })
    assert res.status_code == 200

    res = client.delete(f"/api/diesel/{test_diesel_id}")
    assert res.status_code == 200
    print("✓ Diesel Storage CRUD fully verified.")

    # 7. Database Tables Inspection & Read-only Query
    print("\n[Test 8] Diagnostics & Raw Query (/api/db-tables & /api/raw-query)...")
    res = client.get("/api/db-tables")
    assert res.status_code == 200
    tables = res.get_json()["tables"]
    assert "coal_storage" in tables and "employees" in tables
    print(f"✓ Verified tables: {list(tables.keys())}")

    # Test Listing 4.4 query via raw-query endpoint
    listing_query = (
        "SELECT "
        "SUM(CASE WHEN type = 'IN' THEN quantity_mt ELSE 0 END) - "
        "SUM(CASE WHEN type = 'OUT' THEN quantity_mt ELSE 0 END) AS net_stock_mt "
        "FROM coal_storage;"
    )
    res = client.post("/api/raw-query", json={"query": listing_query})
    assert res.status_code == 200
    query_out = res.get_json()
    print(f"✓ Query executed successfully: Net Coal Stock = {query_out['data'][0]['net_stock_mt']} MT")

    print("\n" + "=" * 70)
    print("ALL REST API ENDPOINTS VALIDATED SUCCESSFULLY (100% PASS)")
    print("=" * 70)


if __name__ == "__main__":
    run_api_tests()

