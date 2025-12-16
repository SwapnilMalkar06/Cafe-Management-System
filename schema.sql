-- Database Creation
CREATE DATABASE IF NOT EXISTS starbucks_db;
USE starbucks_db;

-- 1. Users Table (Admin and Staff)
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL, -- Store SHA256 Hash, not plain text
    role ENUM('Admin', 'Staff') NOT NULL DEFAULT 'Staff',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert a default admin user (Password: admin123)
-- The hash below corresponds to 'admin123'
INSERT IGNORE INTO users (username, password_hash, role) 
VALUES ('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Admin');

-- 2. Inventory Table
CREATE TABLE IF NOT EXISTS inventory (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    unit VARCHAR(20) NOT NULL, -- e.g., kg, liters, packs
    current_stock DECIMAL(10,2) DEFAULT 0.00,
    reorder_level DECIMAL(10,2) DEFAULT 10.00,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 3. Menu Table
CREATE TABLE IF NOT EXISTS menu (
    menu_id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    price DECIMAL(10,2) NOT NULL,
    linked_inventory_id INT, -- To deduct stock automatically
    FOREIGN KEY (linked_inventory_id) REFERENCES inventory(item_id) ON DELETE SET NULL
);

-- 4. Tables Management
CREATE TABLE IF NOT EXISTS cafe_tables (
    table_id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(20) UNIQUE NOT NULL,
    status ENUM('Free', 'Occupied') DEFAULT 'Free'
);

-- Seed some default tables
INSERT IGNORE INTO cafe_tables (table_name) VALUES 
('Table 1'), ('Table 2'), ('Table 3'), ('Table 4'), ('Table 5'), ('Table 6');

-- 5. Employees
CREATE TABLE IF NOT EXISTS employees (
    emp_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(50),
    salary DECIMAL(10,2),
    joining_date DATE
);

-- 6. Attendance
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id INT,
    date DATE,
    status ENUM('Present', 'Absent', 'Half-Day'),
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE,
    UNIQUE(emp_id, date) -- Prevent duplicate attendance for same day
);

-- 7. Orders (Master)
CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) DEFAULT 'Walk-in',
    table_id INT NULL, -- NULL if Parcel
    order_type ENUM('Dine-in', 'Parcel') NOT NULL,
    total_amount DECIMAL(10,2) DEFAULT 0.00,
    discount DECIMAL(10,2) DEFAULT 0,
    final_amount DECIMAL(10,2) DEFAULT 0.00,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (table_id) REFERENCES cafe_tables(table_id)
);

-- 8. Order Details (Line Items)
CREATE TABLE IF NOT EXISTS order_details (
    detail_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    menu_id INT,
    quantity INT,
    price_at_sale DECIMAL(10,2), -- Capture price at moment of sale in case menu changes
    subtotal DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (menu_id) REFERENCES menu(menu_id)
);