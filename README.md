Starbucks Management System ☕
A robust, offline Desktop ERP application designed for managing cafe 
operations. Built with Python and CustomTkinter, it features a modern UI,
real-time table management, inventory tracking, and comprehensive reporting.

🚀 Key Features
1. Point of Sale (POS) & Floor Management
Visual Table Grid:

    🟢 Green: Table is Free.

    🔴 Red: Table is Occupied.

Smart Order Logic:

    Place Order: Creates a ticket and marks the table as Occupied. Adding 
    more items to an Occupied table automatically updates the existing order
    ticket (Running Bill).
    
    Settle Bill: A dedicated button appears for occupied tables to finalize
    the payment and free the table for new customers.

Modes: Support for both Dine-in and Takeaway/Parcel.

2. Inventory Management

    Live Tracking: View current stock levels.

    Low Stock Alerts: Items below the reorder level are highlighted in red.

    Auto-Deduction: Selling a menu item automatically deducts the linked raw
    material (e.g., Selling a Coffee deducts Milk).

3. Menu Management

    Add new items with categories and prices.

    Link menu items to inventory ingredients for automated stock keeping.

    Delete obsolete menu items.

4. HR & Staff Management

    Employee Database: Add new staff with salary details.

    Attendance: Mark Daily Attendance (Present, Absent, Half-Day).

    Management: Delete employee records (Cascade delete removes their
    attendance history).

5. Analytics & Reporting

    Data Viewer: View reports directly within the application in a clean,
    centered table format.

    Reports Available:
        Daily Sales
        Monthly Sales

    Today's Attendance: 
        Export: One-click export to CSV for Excel analysis.

🛠️ Tech Stack

    Frontend/GUI: Python customtkinter (Modern Tkinter wrapper).
    Backend Logic: Python 3.x (Object-Oriented structure).
    Database: MySQL (Relational Data & Persistence).
    Data Processing: pandas (For report generation and CSV export).
    Security: hashlib (SHA256 password hashing for admin/staff).

⚙️ Installation & Setup
    Prerequisites
    Python 3.10+ installed.
    MySQL Server installed and running (e.g., via XAMPP or MySQL Workbench).

Step 1: Install Dependencies
Run the following command in your terminal to install required Python
libraries:
pip install customtkinter mysql-connector-python pandas openpyxl

Step 2: Database Setup
    Open your MySQL Client (Workbench/HeidiSQL/CLI).
    Run the provided schema.sql script (generated in previous steps).
    This creates the database starbucks_db.
    It creates tables: users, inventory, menu, cafe_tables, employees, attendance, orders, order_details.
    It inserts a default Admin user.

Step 3: Configuration
    Open main.py and locate the DB_CONFIG section at the top. Update the
    credentials to match your local MySQL setup:
    DB_CONFIG = {
    'host': 'localhost',
    'database': 'starbucks_db',
    'user': 'root',      # Change to your MySQL username
    'password': '852456' # Change to your MySQL password
    }

Step 4: Run the Application
    python main.py

📖 User Guide
    Login
        Default Username: admin
        Default Password: admin123 (Note: Passwords in DB are hashed).

Handling a Table Order
    Go to POS & Billing.
        Click on a Green (Free) table (e.g., Table 1).
        Select items from the dropdown, enter Quantity, and click Add.
        Click "PLACE ORDER".
        Result: 
        Table 1 turns Red, Inventory is deducted, Order Ticket is created.

Adding more items: 
    Click Table 1 (Red), add items, click "ADD TO ORDER".
    Result: 
        Items are added to the same ticket. Total is updated.
    Customer Leaves: 
        Click Table 1, then click the "SETTLE BILL / FREE TABLE" button.
    Result: 
        Table turns Green, Transaction is finalized.

Theming
    The application is configured to run in Light Mode with a Green accent
    theme by default to match the brand identity.

📂 Project Structure

├── main.py           # The complete application source code
├── schema.sql        # Database creation script
├── requirements.txt  # List of dependencies
└── README.md         # Project documentation
