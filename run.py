"""
CSPGCL Management System Launcher
Direct Website Link: http://localhost:5000/
Starts the web service on localhost:5000 as documented in Chapter 5.1.3 & Chapter 6.
"""

import sys
import os
import webbrowser
import threading
import time

# ==============================================================================
# DIRECT WEBSITE LINK
# Click or visit: http://localhost:5000/
# ==============================================================================
WEBSITE_URL = "http://localhost:5000/"

# Check python version
if sys.version_info < (3, 8):
    print("Error: Python 3.8+ is required to run this project.")
    sys.exit(1)

from app import app
from database import init_database, DB_FILE


def open_browser():
    """Wait for server to start, then automatically open the direct link in your default browser."""
    time.sleep(1.2)
    print(f"\nOpening direct link: {WEBSITE_URL} in your browser...")
    webbrowser.open(WEBSITE_URL)


if __name__ == "__main__":
    if not os.path.exists(DB_FILE):
        print("Database not found. Running initialization and seeding...")
        from init_db import seed_database
        seed_database()

    port = 5000

    print("\n" + "=" * 70)
    print("  CSPGCL MANAGEMENT SYSTEM")
    print("  Chhattisgarh State Power Generation Company Limited, Korba East")
    print("=" * 70)
    print(f"  👉 DIRECT WEBSITE LINK : http://localhost:5000/")
    print(f"  👉 API Health Endpoint : http://localhost:5000/api/health")
    print(f"  👉 Plant Summary API   : http://localhost:5000/api/summary")
    print("=" * 70 + "\n")

    # Automatically launch the direct link in browser
    threading.Thread(target=open_browser, daemon=True).start()

    app.run(host="0.0.0.0", port=port, debug=False)
