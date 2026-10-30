-- ====================================================================
-- CSPGCL Management System - Database Schema
-- Chhattisgarh State Power Generation Company Limited (CSPGCL), Korba
-- Vocational Training Project: Storage & Employee Management System
-- Normalized to Third Normal Form (3NF)
-- ====================================================================

-- 1. Employees Master Table (Table 4.3)
CREATE TABLE IF NOT EXISTS employees (
    emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    designation VARCHAR(100),
    department VARCHAR(100),
    contact_number VARCHAR(15),
    date_of_joining DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Attendance Dependent Table (Table 4.4, FK -> employees)
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_id INTEGER NOT NULL,
    check_in DATETIME NOT NULL,
    check_out DATETIME,
    status VARCHAR(20) DEFAULT 'Present',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE
);

-- 3. Coal Storage Inventory Table (Table 4.1)
CREATE TABLE IF NOT EXISTS coal_storage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quantity_mt DECIMAL(10,2) NOT NULL,
    type VARCHAR(20) NOT NULL, -- 'IN' or 'OUT'
    remarks VARCHAR(255),
    recorded_on DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 4. Diesel Storage Inventory Table (Table 4.2)
CREATE TABLE IF NOT EXISTS diesel_storage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quantity_litres DECIMAL(10,2) NOT NULL,
    type VARCHAR(20) NOT NULL, -- 'IN' or 'OUT'
    remarks VARCHAR(255),
    recorded_on DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Triggers for SQLite automatic updated_at timestamping
CREATE TRIGGER IF NOT EXISTS trg_coal_storage_updated_at
AFTER UPDATE ON coal_storage
FOR EACH ROW
BEGIN
    UPDATE coal_storage SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_diesel_storage_updated_at
AFTER UPDATE ON diesel_storage
FOR EACH ROW
BEGIN
    UPDATE diesel_storage SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

