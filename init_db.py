"""
Database Seeder & Initializer for CSPGCL Management System
Populates initial schema and representative operational datasets for CSPGCL Korba.
"""

import os
from datetime import datetime, timedelta
from database import init_database, get_connection


def seed_database():
    print("Initializing database schema...")
    init_database()

    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Check if already seeded
        cursor.execute("SELECT COUNT(*) as count FROM employees")
        row = cursor.fetchone()
        if row and row["count"] > 0:
            print("Database already contains records. Skipping seed.")
            return

        print("Seeding initial employees data (CSPGCL Korba East Station)...")
        sample_employees = [
            ("Ramesh Kumar", "Plant Operator", "Coal Handling", "9876543210", "2024-01-15"),
            ("Sunita Sahu", "Junior Engineer", "Control & Instrumentation", "9876543211", "2023-08-10"),
            ("Rajesh Verma", "Superintending Engineer", "Boiler Operation", "9876543212", "2020-03-01"),
            ("Priya Dewangan", "Assistant Engineer", "Electrical Department", "9876543213", "2022-11-20"),
            ("Manoj Patel", "Technician", "Turbine Maintenance", "9876543214", "2021-06-14"),
            ("Amit Tiwari", "Stores Officer", "Stores & Procurement", "9876543215", "2021-09-05"),
            ("Geeta Yadav", "Quality Inspector", "Quality Assurance", "9876543216", "2023-02-18"),
            ("Vikash Sharma", "Safety Officer", "Safety and Environment", "9876543217", "2022-04-12")
        ]

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for emp in sample_employees:
            cursor.execute(
                "INSERT INTO employees (name, designation, department, contact_number, date_of_joining, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (emp[0], emp[1], emp[2], emp[3], emp[4], now)
            )

        print("Seeding coal storage records (Metric Tonnes)...")
        base_date = datetime.now()
        sample_coal = [
            (3500.00, "IN", "Rake delivery from SECL Gevra siding via Indian Railways", (base_date - timedelta(days=6)).strftime("%Y-%m-%d")),
            (850.50, "OUT", "Daily boiler bunker feed - Unit #1 (210MW)", (base_date - timedelta(days=5)).strftime("%Y-%m-%d")),
            (920.00, "OUT", "Daily boiler bunker feed - Unit #2 (210MW)", (base_date - timedelta(days=4)).strftime("%Y-%m-%d")),
            (4200.00, "IN", "Bulk rake delivery - Dipka Open Cast Mines stock", (base_date - timedelta(days=3)).strftime("%Y-%m-%d")),
            (1150.00, "OUT", "Pulverizer mill supply - Continuous generation load", (base_date - timedelta(days=2)).strftime("%Y-%m-%d")),
            (2800.00, "IN", "Strategic reserve transfer to intermediate yard B", (base_date - timedelta(days=1)).strftime("%Y-%m-%d")),
            (780.25, "OUT", "Unit #3 pulverizer feed - Morning peak grid demand", base_date.strftime("%Y-%m-%d"))
        ]

        for coal in sample_coal:
            cursor.execute(
                "INSERT INTO coal_storage (quantity_mt, type, remarks, recorded_on, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (coal[0], coal[1], coal[2], coal[3], now, now)
            )

        print("Seeding diesel storage records (Litres)...")
        sample_diesel = [
            (12000.00, "IN", "HSD Tanker consignment receipt from IOCL Korba Depot", (base_date - timedelta(days=6)).strftime("%Y-%m-%d")),
            (450.00, "OUT", "Emergency DG auxiliary black-start testing", (base_date - timedelta(days=5)).strftime("%Y-%m-%d")),
            (1250.00, "OUT", "Coal yard heavy earthmovers and bulldozers fueling", (base_date - timedelta(days=4)).strftime("%Y-%m-%d")),
            (15000.00, "IN", "High-capacity storage tank refill (Tank 02)", (base_date - timedelta(days=2)).strftime("%Y-%m-%d")),
            (2100.00, "OUT", "Boiler warm start-up secondary oil firing support", (base_date - timedelta(days=1)).strftime("%Y-%m-%d")),
            (380.00, "OUT", "Standby generator routine maintenance run", base_date.strftime("%Y-%m-%d"))
        ]

        for diesel in sample_diesel:
            cursor.execute(
                "INSERT INTO diesel_storage (quantity_litres, type, remarks, recorded_on, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (diesel[0], diesel[1], diesel[2], diesel[3], now, now)
            )

        print("Seeding employee attendance records...")
        today_str = base_date.strftime("%Y-%m-%d")
        yesterday_str = (base_date - timedelta(days=1)).strftime("%Y-%m-%d")
        day_before_str = (base_date - timedelta(days=2)).strftime("%Y-%m-%d")

        sample_attendance = [
            # Day before yesterday
            (1, f"{day_before_str} 08:55:00", f"{day_before_str} 17:15:00", "Present"),
            (2, f"{day_before_str} 09:00:00", f"{day_before_str} 17:30:00", "Present"),
            (3, f"{day_before_str} 09:10:00", f"{day_before_str} 17:20:00", "Present"),
            (4, f"{day_before_str} 08:45:00", f"{day_before_str} 13:00:00", "Half-Day"),
            # Yesterday
            (1, f"{yesterday_str} 09:02:00", f"{yesterday_str} 17:25:00", "Present"),
            (2, f"{yesterday_str} 08:58:00", f"{yesterday_str} 17:35:00", "Present"),
            (3, f"{yesterday_str} 09:15:00", f"{yesterday_str} 17:10:00", "Present"),
            (5, f"{yesterday_str} 09:00:00", f"{yesterday_str} 17:00:00", "Present"),
            (6, f"{yesterday_str} 09:30:00", f"{yesterday_str} 17:30:00", "Present"),
            # Today
            (1, f"{today_str} 09:00:00", f"{today_str} 17:00:00", "Present"),
            (2, f"{today_str} 08:45:00", None, "Present"), # Currently clocked in
            (3, f"{today_str} 09:12:00", None, "Present"), # Currently clocked in
            (4, f"{today_str} 08:50:00", None, "Present"), # Currently clocked in
            (5, f"{today_str} 09:05:00", f"{today_str} 13:10:00", "Half-Day"),
            (7, f"{today_str} 09:00:00", None, "Present"),
            (8, f"{today_str} 00:00:00", None, "Absent")
        ]

        for att in sample_attendance:
            cursor.execute(
                "INSERT INTO attendance (emp_id, check_in, check_out, status, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (att[0], att[1], att[2], att[3], now)
            )

        conn.commit()
        print("Database initialized and successfully seeded with CSPGCL data.")
    finally:
        conn.close()


if __name__ == "__main__":
    seed_database()

