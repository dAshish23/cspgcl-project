# CSPGCL Management System
### Storage & Employee Management System
**Chhattisgarh State Power Generation Company Limited (CSPGCL), Korba East Thermal Power Station**  
*Vocational Training Based Project Report Submitted to Chhattisgarh Swami Vivekanand Technical University (CSVTU), Bhilai*

---

## 📋 Academic & Project Details
- **Candidate Name:** Ashish Kumar Dahariya
- **Degree:** Bachelor of Technology (Honors) in Artificial Intelligence / Data Science (CSE)
- **Semester:** 4th Semester Vocational Training
- **Roll Number:** 300012724015
- **Enrollment Number:** CE3605
- **Institution:** Department of Computer Science & Engineering, University Teaching Department, CSVTU, Bhilai (C.G.)
- **Industry Partner:** Chhattisgarh State Power Generation Company Limited (CSPGCL), Korba East (KETPS / DSPM TPS)

---

## 🌟 Project Overview
The **CSPGCL Storage & Employee Management System** is a full-stack web application designed to digitize the manual tracking of:
1. **Thermal Coal Inventory:** Tracking bulk train rake receipts from SECL (Gevra/Dipka mines) and daily boiler pulverizer mill consumption (in Metric Tonnes - MT).
2. **High Speed Diesel (HSD) Inventory:** Tracking tanker receipts from oil depots and fuel issues for boiler warm start-up secondary oil firing, emergency diesel generators (DG sets), and heavy coal yard machinery (in Litres).
3. **Employee Master Records:** Centralized repository of plant personnel across departments (Coal Handling, Boiler Operation, Turbine Maintenance, Electrical, C&I, Safety, etc.).
4. **Shift Attendance Tracking:** Check-in and check-out logs with foreign key constraints, status flags (Present / Absent / Half-Day), and automated timestamps.

The application follows a **Three-Tier Architecture**:
- **Database Layer:** Relational database (`SQLite` default for local zero-config execution; `MySQL` production ready via environment variables), normalized to **Third Normal Form (3NF)**.
- **Backend API Layer:** Resource-oriented **Python Flask REST API** delivering JSON responses with parameterized queries for security.
- **Frontend Layer:** Responsive **HTML5, CSS3, and Vanilla JavaScript** single-page interface with tabbed views, instant live search, CSV export, and print reports.

---

## 🗄️ Database Design (Chapter IV - 3NF Normalized)

### 1. `employees` (Table 4.3 & Listing 4.1)
| Field | Data Type | Constraint | Description |
|---|---|---|---|
| `emp_id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique employee identifier |
| `name` | VARCHAR(100) | NOT NULL | Full name of employee |
| `designation` | VARCHAR(100) | NULL | Job title (e.g. Plant Operator, JE, SE) |
| `department` | VARCHAR(100) | NULL | Station department |
| `contact_number` | VARCHAR(15) | NULL | Phone contact |
| `date_of_joining` | DATE | NULL | Date joined service |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | System timestamp |

### 2. `attendance` (Table 4.4 & Listing 4.1)
| Field | Data Type | Constraint | Description |
|---|---|---|---|
| `attendance_id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique attendance record ID |
| `emp_id` | INTEGER | FOREIGN KEY REFERENCES employees(emp_id) ON DELETE CASCADE | Linked employee |
| `check_in` | DATETIME | NOT NULL | Shift arrival timestamp |
| `check_out` | DATETIME | NULL | Shift departure timestamp |
| `status` | VARCHAR(20) | DEFAULT 'Present' | Status: Present, Absent, Half-Day |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | System timestamp |

### 3. `coal_storage` (Table 4.1 & Listing 4.2)
| Field | Data Type | Constraint | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Transaction ID |
| `quantity_mt` | DECIMAL(10,2) | NOT NULL | Quantity in Metric Tonnes (MT) |
| `type` | VARCHAR(20) | NOT NULL | 'IN' (Receipt) or 'OUT' (Feed) |
| `remarks` | VARCHAR(255) | NULL | Origin, siding or boiler unit details |
| `recorded_on` | DATE | NOT NULL | Operational date |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | System timestamp |
| `updated_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Modification timestamp |

### 4. `diesel_storage` (Table 4.2 & Listing 4.2)
| Field | Data Type | Constraint | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Transaction ID |
| `quantity_litres` | DECIMAL(10,2) | NOT NULL | Quantity in Litres |
| `type` | VARCHAR(20) | NOT NULL | 'IN' (Delivery) or 'OUT' (Consumed) |
| `remarks` | VARCHAR(255) | NULL | Storage tank or machinery details |
| `recorded_on` | DATE | NOT NULL | Operational date |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | System timestamp |
| `updated_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Modification timestamp |

---

## 🔌 REST API Endpoints (Chapter V, Table 5.1)

| Resource | HTTP Method | Endpoint | Description |
|---|---|---|---|
| **Health Check** | `GET` | `/api/health` | System status & database connectivity |
| **Dashboard** | `GET` | `/api/summary` | Real-time plant KPIs & stock totals |
| **Coal Storage** | `GET` | `/api/coal` | Retrieve all coal records + net balance |
| | `POST` | `/api/coal` | Add coal receipt or issue |
| | `GET` | `/api/coal/<id>` | Fetch specific coal entry |
| | `PUT` | `/api/coal/<id>` | Update coal entry |
| | `DELETE` | `/api/coal/<id>` | Delete coal entry |
| **Diesel Storage**| `GET` | `/api/diesel` | Retrieve all diesel records + net balance |
| | `POST` | `/api/diesel` | Add diesel tanker delivery or issue |
| | `GET` | `/api/diesel/<id>`| Fetch specific diesel entry |
| | `PUT` | `/api/diesel/<id>`| Update diesel entry |
| | `DELETE` | `/api/diesel/<id>`| Delete diesel entry |
| **Employees** | `GET` | `/api/employees` | List all employee records |
| | `POST` | `/api/employees` | Register new employee (Listing 5.1) |
| | `GET` | `/api/employees/<id>`| Employee details + attendance history |
| | `PUT` | `/api/employees/<id>`| Update employee details |
| | `DELETE` | `/api/employees/<id>`| Delete employee (cascades attendance) |
| **Attendance** | `GET` | `/api/attendance` | Joined records with filters (?date, ?emp_id) |
| | `POST` | `/api/attendance` | Record attendance (Listing 5.2) |
| | `GET` | `/api/attendance/<id>`| Get single attendance record |
| | `PUT` | `/api/attendance/<id>`| Update check-out timestamp or status |
| | `DELETE` | `/api/attendance/<id>`| Delete attendance entry |
| **Quick Punch** | `POST` | `/api/attendance/check-in` | One-click instant clock-in |
| | `POST` | `/api/attendance/check-out` | One-click instant clock-out |
| **Diagnostics** | `GET` | `/api/db-tables` | Database table schema inspection (Fig 6.6) |
| | `POST` | `/api/raw-query` | Safe read-only SQL query runner (Fig 6.8) |

---

## 🚀 Setup & Execution Instructions

### 1. Requirements
- Python 3.8 or higher
- Flask and Requests

### 2. Installation
```bash
pip install -r requirements.txt
```

### 3. Initialize Database & Seed Data
```bash
python init_db.py
```
*Creates the SQLite database (`cspgcl.db`) and seeds representative CSPGCL Korba thermal power operational data.*

### 4. Run the Verification Tests
```bash
# 1. Database layer verification (schema, 3NF, foreign keys, triggers)
python test_db.py

# 2. REST API endpoints verification (all HTTP methods, JSON responses)
python test_api.py
```

### 5. Launch the Web Application
```bash
python run.py
```
Open your web browser and navigate to:
**`http://localhost:5000`**

---

## 🖥️ Screen Reference Map (Chapter VI)

- **Fig 6.1: Home Dashboard** — Storage level gauges (CRSP buffer), net coal (MT) and diesel (L) stock indicators, workforce presence counts, quick punch actions, and recent transactions.
- **Fig 6.2: Coal Storage Management** — Real-time coal inventory balances, incoming/outgoing transaction log, filtering by type/date, and CSV export.
- **Fig 6.3: Diesel Storage Management** — Real-time HSD fuel reserves, tanker receipts, auxiliary boiler/generator issue logs, and CSV export.
- **Fig 6.4: Employee Management** — Personnel directory by department, search, registration modal, and employee attendance history view.
- **Fig 6.5: Attendance Check-in / Check-out Module** — Instant shift punch in/out buttons, date filters, status pills (Present/Absent/Half-Day), and checkout updates.
- **Fig 6.6: Database Tables in MySQL/SQLite** — Interactive schema and row count inspector in the Tools tab.
- **Fig 6.7: Sample REST API Response (JSON)** — Live interactive REST API explorer with status codes and formatted JSON response viewer.
- **Fig 6.8: Database Query Output** — Live SQL Query runner supporting Listing 4.3 (Joined attendance) and Listing 4.4 (Net Coal Stock calculation).
- **Fig 6.9: Attendance & Inventory Reports** — Official printable and PDF-exportable station reports for Coal Receipt & Stock Position (CRSP) and shift deployment.

