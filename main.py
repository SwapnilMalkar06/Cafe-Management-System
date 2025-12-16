import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
import pandas as pd
import hashlib
import datetime
import os

# --- CONFIGURATION ---
ctk.set_appearance_mode("Light")      # Light Mode
ctk.set_default_color_theme("green")  # Starbucks Green

APP_NAME = "Starbucks Management System"
DB_CONFIG = {
    'host': 'localhost',
    'database': 'starbucks_db',
    'user': 'root',
    'password': '852456'
}

# --- BACKEND LOGIC ---

class DatabaseManager:
    def __init__(self):
        self.conn = None
        self.connect()

    def connect(self):
        try:
            self.conn = mysql.connector.connect(**DB_CONFIG)
            if self.conn.is_connected():
                print(f"Connected to {DB_CONFIG['database']}")
        except Error as e:
            print(f"Database connection warning: {e}")

    def get_connection(self):
        if self.conn is None or not self.conn.is_connected():
            try:
                self.conn = mysql.connector.connect(**DB_CONFIG)
            except Error as e:
                messagebox.showerror("Database Error", f"Could not connect to database:\n{e}")
                return None
        return self.conn

    def execute_query(self, query, params=None):
        conn = self.get_connection()
        if not conn: return None
        cursor = conn.cursor()
        try:
            cursor.execute(query, params or ())
            conn.commit()
            return cursor
        except Error as e:
            messagebox.showerror("Query Error", f"Error executing query:\n{e}")
            return None

    def fetch_all(self, query, params=None):
        conn = self.get_connection()
        if not conn: return []
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        except Error as e:
            messagebox.showerror("Fetch Error", f"Error fetching data:\n{e}")
            return []

    def fetch_one(self, query, params=None):
        conn = self.get_connection()
        if not conn: return None
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchone()
        except Error as e:
            messagebox.showerror("Fetch Error", f"Error fetching data:\n{e}")
            return None

db = DatabaseManager()

# --- UTILS ---

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- UI MODULES ---

class LoginUI(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(self, text=APP_NAME, font=("Roboto", 24, "bold"), text_color="#00704A").pack(pady=20, padx=40)
        ctk.CTkLabel(self, text="Staff Login", font=("Roboto", 16)).pack(pady=5)

        self.entry_user = ctk.CTkEntry(self, placeholder_text="Username", width=250)
        self.entry_user.pack(pady=10, padx=20)
        
        self.entry_pass = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=250)
        self.entry_pass.pack(pady=10, padx=20)

        ctk.CTkButton(self, text="Login", command=self.attempt_login, fg_color="#00704A", hover_color="#004d33").pack(pady=20, fill="x", padx=20)

    def attempt_login(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()
        hashed_pw = hash_password(password)
        
        user = db.fetch_one("SELECT * FROM users WHERE username = %s AND password_hash = %s", (username, hashed_pw))
        
        if user:
            self.controller.current_user = user
            self.controller.show_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid Credentials")

class DashboardUI(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.pack(fill="both", expand=True)

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.sidebar, text="Starbucks\nOperations", font=("Roboto", 20, "bold"), text_color="#00704A").pack(pady=20)

        sections = [("POS & Billing", POSModule), ("Menu Management", MenuModule), 
                    ("Inventory", InventoryModule), ("HR & Staff", HRModule), 
                    ("Reports & Analytics", ReportsModule)]
        
        for name, module_class in sections:
            btn = ctk.CTkButton(self.sidebar, text=name, 
                                fg_color="transparent", border_width=2, text_color=("gray10", "gray10"),
                                command=lambda m=module_class: self.show_module(m))
            btn.pack(pady=10, padx=10, fill="x")

        ctk.CTkButton(self.sidebar, text="Logout", fg_color="transparent", border_width=1, border_color="red", text_color="red",
                      command=self.controller.logout).pack(side="bottom", pady=20, padx=10, fill="x")

        self.main_area = ctk.CTkFrame(self, corner_radius=0)
        self.main_area.pack(side="right", fill="both", expand=True)
        
        self.show_module(POSModule)

    def show_module(self, module_class):
        for widget in self.main_area.winfo_children():
            widget.destroy()
        module_class(self.main_area, self.controller).pack(fill="both", expand=True)

# --- FUNCTIONAL MODULES ---

class MenuModule(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        ctk.CTkLabel(form_frame, text="Add New Menu Item", font=("Roboto", 16, "bold"), text_color="#00704A").grid(row=0, column=0, columnspan=4, pady=10)

        ctk.CTkLabel(form_frame, text="Item Name:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.ent_name = ctk.CTkEntry(form_frame, width=200)
        self.ent_name.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(form_frame, text="Category:").grid(row=1, column=2, padx=10, pady=5, sticky="e")
        self.ent_category = ctk.CTkEntry(form_frame, width=150, placeholder_text="e.g. Coffee")
        self.ent_category.grid(row=1, column=3, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(form_frame, text="Price (₹):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.ent_price = ctk.CTkEntry(form_frame, width=100)
        self.ent_price.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(form_frame, text="Link Inventory:").grid(row=2, column=2, padx=10, pady=5, sticky="e")
        self.cbo_inv = ctk.CTkComboBox(form_frame, values=["None"], width=200)
        self.cbo_inv.grid(row=2, column=3, padx=10, pady=5, sticky="w")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=1, column=0, sticky="ew", padx=10)
        
        ctk.CTkButton(btn_frame, text="Add Menu Item", command=self.add_menu_item, fg_color="#00704A").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Delete Selected", command=self.delete_menu_item, fg_color="#B22222", hover_color="#8b0000").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Refresh List", command=self.load_data, fg_color="gray").pack(side="left", padx=5)

        cols = ("ID", "Name", "Category", "Price", "Linked Ingredient")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=15)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center") 
            if col == "Name": self.tree.column(col, width=200, anchor="center")
        
        self.tree.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        self.load_inventory_list()
        self.load_data()

    def load_inventory_list(self):
        items = db.fetch_all("SELECT item_id, item_name FROM inventory")
        self.inv_map = {f"{i['item_name']}": i['item_id'] for i in items}
        self.inv_map["None"] = None
        self.cbo_inv.configure(values=["None"] + list(self.inv_map.keys()))

    def add_menu_item(self):
        name = self.ent_name.get()
        cat = self.ent_category.get()
        price = self.ent_price.get()
        inv_name = self.cbo_inv.get()
        inv_id = self.inv_map.get(inv_name)

        if not name or not price:
            messagebox.showerror("Error", "Name and Price are required.")
            return

        try:
            db.execute_query(
                "INSERT INTO menu (item_name, category, price, linked_inventory_id) VALUES (%s, %s, %s, %s)",
                (name, cat, float(price), inv_id)
            )
            messagebox.showinfo("Success", "Item Added")
            self.load_data()
            self.ent_name.delete(0, 'end')
            self.ent_price.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def delete_menu_item(self):
        selected = self.tree.selection()
        if not selected: 
            messagebox.showwarning("Select Item", "Please select a menu item to delete.")
            return
        if not messagebox.askyesno("Confirm", "Delete this menu item?"): return
        try:
            item_id = self.tree.item(selected)['values'][0]
            db.execute_query("DELETE FROM menu WHERE menu_id = %s", (item_id,))
            self.load_data()
        except Exception as e:
             messagebox.showerror("Error", str(e))

    def load_data(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        query = """SELECT m.menu_id, m.item_name, m.category, m.price, i.item_name as inv_name 
                   FROM menu m LEFT JOIN inventory i ON m.linked_inventory_id = i.item_id"""
        rows = db.fetch_all(query)
        for r in rows:
            inv = r['inv_name'] if r['inv_name'] else "-"
            self.tree.insert("", "end", values=(r['menu_id'], r['item_name'], r['category'], r['price'], inv))

class POSModule(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.table_frame = ctk.CTkScrollableFrame(self, label_text="Floor Plan")
        self.table_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.billing_frame = ctk.CTkFrame(self)
        self.billing_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.selected_table_id = None
        self.selected_table_status = None
        self.order_items = []

        self.build_billing_ui()
        self.refresh_tables()

    def build_billing_ui(self):
        self.lbl_table = ctk.CTkLabel(self.billing_frame, text="Select a Table", font=("Roboto", 18, "bold"))
        self.lbl_table.pack(pady=10)

        self.var_order_type = ctk.StringVar(value="Dine-in")
        ctk.CTkSegmentedButton(self.billing_frame, values=["Dine-in", "Takeaway"], 
                               variable=self.var_order_type, command=self.toggle_mode).pack(pady=5)

        self.menu_combo = ctk.CTkComboBox(self.billing_frame, values=["Select Item"])
        self.menu_combo.pack(pady=5, padx=10, fill="x")
        self.load_menu_items()

        qty_frame = ctk.CTkFrame(self.billing_frame, fg_color="transparent")
        qty_frame.pack(pady=5)
        self.qty_entry = ctk.CTkEntry(qty_frame, placeholder_text="Qty", width=60)
        self.qty_entry.pack(side="left", padx=5)
        ctk.CTkButton(qty_frame, text="Add", width=80, command=self.add_item_to_cart).pack(side="left", padx=5)

        cols = ("Name", "Qty", "Price", "Total")
        self.cart_tree = ttk.Treeview(self.billing_frame, columns=cols, show="headings", height=10)
        for col in cols:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=60, anchor="center") 
        self.cart_tree.pack(pady=10, fill="both", expand=True)

        self.lbl_total = ctk.CTkLabel(self.billing_frame, text="Total: ₹0.00", font=("Roboto", 16, "bold"), text_color="#00704A")
        self.lbl_total.pack(pady=5)

        # BUTTONS - Logic controlled in select_table
        self.btn_place_order = ctk.CTkButton(self.billing_frame, text="PLACE ORDER (Print KOT)", fg_color="#00704A", hover_color="#004d33",
                      command=self.place_order)
        self.btn_place_order.pack(pady=5, fill="x", padx=10)

        self.btn_settle = ctk.CTkButton(self.billing_frame, text="SETTLE BILL / FREE TABLE", fg_color="#B22222", hover_color="#8b0000",
                      command=self.settle_table)
        self.btn_settle.pack(pady=5, fill="x", padx=10)
        self.btn_settle.pack_forget() # Hide initially

    def load_menu_items(self):
        items = db.fetch_all("SELECT * FROM menu")
        self.menu_map = {f"{i['item_name']} - ₹{i['price']}": i for i in items}
        self.menu_combo.configure(values=list(self.menu_map.keys()))

    def refresh_tables(self):
        for widget in self.table_frame.winfo_children(): widget.destroy()
        tables = db.fetch_all("SELECT * FROM cafe_tables")
        row, col = 0, 0
        for table in tables:
            color = "#00704A" if table['status'] == 'Free' else "#B22222"
            status_text = "FREE" if table['status'] == 'Free' else "OCCUPIED"
            btn = ctk.CTkButton(self.table_frame, text=f"{table['table_name']}\n{status_text}",
                                fg_color=color, height=80, width=80,
                                command=lambda t=table: self.select_table(t))
            btn.grid(row=row, column=col, padx=10, pady=10)
            col += 1
            if col > 2: col = 0; row += 1

    def select_table(self, table):
        self.selected_table_id = table['table_id']
        self.selected_table_status = table['status']
        self.lbl_table.configure(text=f"Billing: {table['table_name']} ({table['status']})")
        self.var_order_type.set("Dine-in")
        
        # UI Logic based on status
        if table['status'] == 'Occupied':
            self.btn_settle.pack(pady=5, fill="x", padx=10)
            self.btn_place_order.configure(text="ADD TO ORDER")
        else:
            self.btn_settle.pack_forget()
            self.btn_place_order.configure(text="PLACE ORDER (Start Table)")

    def toggle_mode(self, value):
        if value == "Takeaway":
            self.selected_table_id = None
            self.lbl_table.configure(text="Order: Takeaway")
            self.btn_settle.pack_forget()
            self.btn_place_order.configure(text="PLACE ORDER")
        else:
            self.lbl_table.configure(text="Select a Table")

    def add_item_to_cart(self):
        selection = self.menu_combo.get()
        if selection not in self.menu_map: return
        try: qty = int(self.qty_entry.get())
        except ValueError: messagebox.showerror("Error", "Invalid Quantity"); return

        item_data = self.menu_map[selection]
        subtotal = float(item_data['price']) * qty
        self.order_items.append({
            "menu_id": item_data['menu_id'], "name": item_data['item_name'],
            "qty": qty, "price": float(item_data['price']), "subtotal": subtotal,
            "inv_id": item_data['linked_inventory_id']
        })
        self.update_cart_ui()

    def update_cart_ui(self):
        for i in self.cart_tree.get_children(): self.cart_tree.delete(i)
        grand_total = 0
        for item in self.order_items:
            self.cart_tree.insert("", "end", values=(item['name'], item['qty'], item['price'], item['subtotal']))
            grand_total += item['subtotal']
        self.lbl_total.configure(text=f"Total: ₹{grand_total:.2f}")
        self.current_total = grand_total

    def place_order(self):
        if not self.order_items: return
        
        # --- NEW LOGIC START ---
        # 1. Determine if we are updating an existing active order for this table or creating a new one
        order_id = None
        is_new_order = True

        if self.selected_table_id:
            # Check DB to see if table is truly occupied
            table_info = db.fetch_one("SELECT status FROM cafe_tables WHERE table_id = %s", (self.selected_table_id,))
            if table_info and table_info['status'] == 'Occupied':
                # Fetch the latest active order ID for this table
                existing_order = db.fetch_one("SELECT order_id FROM orders WHERE table_id = %s ORDER BY order_id DESC LIMIT 1", (self.selected_table_id,))
                if existing_order:
                    order_id = existing_order['order_id']
                    is_new_order = False
        
        # 2. If it's a new order (Free table OR Takeaway), create the order record
        if is_new_order:
            query = "INSERT INTO orders (customer_name, table_id, order_type, total_amount, final_amount) VALUES (%s, %s, %s, %s, %s)"
            db_order_type = "Parcel" if self.var_order_type.get() == "Takeaway" else "Dine-in"
            # We initialize with 0, will update total at the end of this function
            cursor = db.execute_query(query, ("Walk-in", self.selected_table_id, db_order_type, 0, 0))
            if not cursor: return
            order_id = cursor.lastrowid
            
            # If it's a table order, mark table as Occupied
            if self.selected_table_id:
                db.execute_query("UPDATE cafe_tables SET status = 'Occupied' WHERE table_id = %s", (self.selected_table_id,))

        # 3. Add the items to order_details (Linked to order_id)
        for item in self.order_items:
            db.execute_query("INSERT INTO order_details (order_id, menu_id, quantity, price_at_sale, subtotal) VALUES (%s, %s, %s, %s, %s)", 
                             (order_id, item['menu_id'], item['qty'], item['price'], item['subtotal']))
            if item['inv_id']:
                db.execute_query("UPDATE inventory SET current_stock = current_stock - %s WHERE item_id = %s", (item['qty'], item['inv_id']))

        # 4. Recalculate the Grand Total for this Order ID (Sum of all previous items + new items)
        # We query the DB for the sum to ensure data consistency
        total_res = db.fetch_one("SELECT SUM(subtotal) as grand_total FROM order_details WHERE order_id = %s", (order_id,))
        new_grand_total = total_res['grand_total'] if total_res and total_res['grand_total'] else 0
        
        # Update the master order record
        db.execute_query("UPDATE orders SET total_amount = %s, final_amount = %s WHERE order_id = %s", 
                         (new_grand_total, new_grand_total, order_id))
        # --- NEW LOGIC END ---

        msg = f"Order Placed! Ticket ID: {order_id}" if is_new_order else f"Items Added to Order #{order_id}"
        messagebox.showinfo("Success", msg)
        
        self.order_items = []
        self.update_cart_ui()
        self.refresh_tables()

    def settle_table(self):
        if not self.selected_table_id: return
        
        # --- UPDATED SETTLE LOGIC ---
        # Fetch current total to show user
        existing_order = db.fetch_one("SELECT order_id, final_amount FROM orders WHERE table_id = %s ORDER BY order_id DESC LIMIT 1", (self.selected_table_id,))
        
        amount_msg = ""
        if existing_order:
             amount_msg = f"\nTotal Bill Amount: ₹{existing_order['final_amount']}"

        if not messagebox.askyesno("Confirm Settle", f"Are you sure the customer has paid?{amount_msg}\n\nThis will free the table."):
            return

        db.execute_query("UPDATE cafe_tables SET status = 'Free' WHERE table_id = %s", (self.selected_table_id,))
        messagebox.showinfo("Success", "Table is now Free.")
        self.refresh_tables()
        # Reset UI
        self.lbl_table.configure(text="Select a Table")
        self.btn_settle.pack_forget()
        self.selected_table_id = None

class InventoryModule(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        
        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(controls, text="Item Name").pack(side="left", padx=5)
        self.ent_name = ctk.CTkEntry(controls)
        self.ent_name.pack(side="left", padx=5)
        ctk.CTkLabel(controls, text="Unit").pack(side="left", padx=5)
        self.ent_unit = ctk.CTkEntry(controls, width=60)
        self.ent_unit.pack(side="left", padx=5)
        ctk.CTkLabel(controls, text="Qty").pack(side="left", padx=5)
        self.ent_qty = ctk.CTkEntry(controls, width=60)
        self.ent_qty.pack(side="left", padx=5)

        ctk.CTkButton(controls, text="Add Stock", command=self.add_stock, fg_color="#00704A").pack(side="left", padx=10)
        ctk.CTkButton(controls, text="Refresh", command=self.load_data).pack(side="left", padx=10)

        cols = ("ID", "Name", "Unit", "Stock", "Reorder Level")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center") 
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.load_data()

    def add_stock(self):
        try:
            name, unit, qty = self.ent_name.get(), self.ent_unit.get(), float(self.ent_qty.get())
            exists = db.fetch_one("SELECT item_id FROM inventory WHERE item_name = %s", (name,))
            if exists:
                db.execute_query("UPDATE inventory SET current_stock = current_stock + %s WHERE item_id = %s", (qty, exists['item_id']))
            else:
                db.execute_query("INSERT INTO inventory (item_name, unit, current_stock) VALUES (%s, %s, %s)", (name, unit, qty))
            self.load_data()
            messagebox.showinfo("Success", "Inventory Updated")
        except Exception as e: messagebox.showerror("Error", str(e))

    def load_data(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        items = db.fetch_all("SELECT * FROM inventory")
        for item in items:
            tags = ('low_stock',) if item['current_stock'] < item['reorder_level'] else ()
            self.tree.insert("", "end", values=(item['item_id'], item['item_name'], item['unit'], 
                                              item['current_stock'], item['reorder_level']), tags=tags)
        self.tree.tag_configure('low_stock', background='#ffcccc', foreground='black')

class HRModule(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True)
        self.tab_emp = self.tabview.add("Employees")
        self.tab_att = self.tabview.add("Attendance")
        
        # Employee Tab
        ctk.CTkLabel(self.tab_emp, text="Add New Partner (Employee)").pack(pady=5)
        self.ent_emp_name = ctk.CTkEntry(self.tab_emp, placeholder_text="Name")
        self.ent_emp_name.pack(pady=5)
        self.ent_emp_sal = ctk.CTkEntry(self.tab_emp, placeholder_text="Salary")
        self.ent_emp_sal.pack(pady=5)
        ctk.CTkButton(self.tab_emp, text="Add Employee", command=self.add_employee, fg_color="#00704A").pack(pady=10)
        ctk.CTkButton(self.tab_emp, text="Delete Selected Employee", command=self.delete_employee, fg_color="#B22222", hover_color="#8b0000").pack(pady=5)
        
        cols = ("ID", "Name", "Role", "Salary")
        self.emp_tree = ttk.Treeview(self.tab_emp, columns=cols, show="headings", height=8)
        for c in cols: 
            self.emp_tree.heading(c, text=c)
            self.emp_tree.column(c, anchor="center") 
        self.emp_tree.pack(fill="both", expand=True)

        # Attendance Tab
        self.emp_combo = ctk.CTkComboBox(self.tab_att, values=["Select Employee"])
        self.emp_combo.pack(pady=10)
        self.status_var = ctk.StringVar(value="Present")
        ctk.CTkSegmentedButton(self.tab_att, values=["Present", "Absent", "Half-Day"], variable=self.status_var).pack(pady=10)
        ctk.CTkButton(self.tab_att, text="Mark Today's Attendance", command=self.mark_attendance, fg_color="#00704A").pack(pady=10)
        
        self.load_employees()

    def add_employee(self):
        if self.ent_emp_name.get() and self.ent_emp_sal.get():
            db.execute_query("INSERT INTO employees (name, salary, role, joining_date) VALUES (%s, %s, 'Staff', CURDATE())", 
                             (self.ent_emp_name.get(), self.ent_emp_sal.get()))
            self.load_employees()

    def delete_employee(self):
        selected_item = self.emp_tree.selection()
        if not selected_item: return
        if not messagebox.askyesno("Confirm", "Delete this employee?"): return
        try:
            emp_id = self.emp_tree.item(selected_item)['values'][0]
            db.execute_query("DELETE FROM employees WHERE emp_id = %s", (emp_id,))
            self.load_employees()
            messagebox.showinfo("Success", "Deleted")
        except Exception as e: messagebox.showerror("Error", str(e))

    def load_employees(self):
        for i in self.emp_tree.get_children(): self.emp_tree.delete(i)
        emps = db.fetch_all("SELECT * FROM employees")
        combo_vals = []
        for e in emps:
            self.emp_tree.insert("", "end", values=(e['emp_id'], e['name'], e['role'], e['salary']))
            combo_vals.append(f"{e['emp_id']} - {e['name']}")
        self.emp_combo.configure(values=combo_vals)

    def mark_attendance(self):
        selection = self.emp_combo.get()
        if not selection or "Select" in selection: return
        try:
            db.execute_query("INSERT INTO attendance (emp_id, date, status) VALUES (%s, %s, %s)", 
                             (selection.split(" - ")[0], datetime.date.today(), self.status_var.get()))
            messagebox.showinfo("Success", "Attendance Marked")
        except: messagebox.showwarning("Warning", "Already marked for today.")

class ReportsModule(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.current_df = None
        self.current_report_name = "report"

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Control Bar
        control_frame = ctk.CTkFrame(self, fg_color="transparent")
        control_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(control_frame, text="Analytics Dashboard", font=("Roboto", 18, "bold")).pack(side="left", padx=10)
        
        ctk.CTkButton(control_frame, text="Daily Sales", command=self.show_daily_sales, fg_color="#00704A").pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text="Monthly Sales", command=self.show_monthly_sales, fg_color="#00704A").pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text="Today's Attendance", command=self.show_attendance, fg_color="#00704A").pack(side="left", padx=5)
        
        ctk.CTkButton(control_frame, text="Export CSV", command=self.export_csv, fg_color="gray").pack(side="right", padx=10)

        # Results Table Container (with border effect via frame)
        table_container = ctk.CTkFrame(self, border_width=2, border_color="#00704A")
        table_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(0, weight=1)

        # Treeview for Results
        self.tree = ttk.Treeview(table_container, show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        hsb = ttk.Scrollbar(table_container, orient="horizontal", command=self.tree.xview)
        hsb.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.lbl_status = ctk.CTkLabel(self, text="Select a report to view data.")
        self.lbl_status.grid(row=2, column=0, pady=5)

    def populate_tree(self, df):
        # Clear existing
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(df.columns)
        
        for col in df.columns:
            self.tree.heading(col, text=col)
            # Adjust column width and center content
            self.tree.column(col, width=120, anchor="center") 

        for _, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))

    def show_daily_sales(self):
        query = "SELECT order_id, customer_name, order_type, final_amount, order_date FROM orders WHERE DATE(order_date) = CURDATE()"
        self.run_report(query, "daily_sales")

    def show_monthly_sales(self):
        query = "SELECT order_id, customer_name, order_type, final_amount, order_date FROM orders WHERE MONTH(order_date) = MONTH(CURDATE()) AND YEAR(order_date) = YEAR(CURDATE())"
        self.run_report(query, "monthly_sales")

    def show_attendance(self):
        query = """
        SELECT a.date, e.name, a.status 
        FROM attendance a 
        JOIN employees e ON a.emp_id = e.emp_id 
        WHERE a.date = CURDATE()
        """
        self.run_report(query, "todays_attendance")

    def run_report(self, query, report_name):
        conn = db.get_connection()
        try:
            df = pd.read_sql(query, conn)
            if df.empty:
                self.lbl_status.configure(text=f"No data found for {report_name}.")
                self.tree.delete(*self.tree.get_children())
                self.current_df = None
                return
            
            self.populate_tree(df)
            self.current_df = df
            self.current_report_name = report_name
            self.lbl_status.configure(text=f"Showing {len(df)} records for {report_name}.")
        except Exception as e:
            messagebox.showerror("Report Error", str(e))

    def export_csv(self):
        if self.current_df is None:
            messagebox.showwarning("Export", "No data to export.")
            return
        
        filename = f"{APP_NAME.replace(' ', '_')}_{self.current_report_name}.csv"
        try:
            self.current_df.to_csv(filename, index=False)
            self.lbl_status.configure(text=f"Exported to {filename}")
            try: os.startfile(filename)
            except: os.system(f"open {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

# --- MAIN APP CONTAINER ---

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1100x700")
        self.setup_styles() 
        
        self.current_user = None
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        
        self.show_login()

    def setup_styles(self):
        # Configure Treeview Style
        style = ttk.Style()
        style.theme_use("clam") 
        
        # General Treeview style (Light Mode Optimized)
        style.configure("Treeview", 
                        background="#FFFFFF",   # White Background for Light Mode
                        foreground="black",     # Black text
                        fieldbackground="#FFFFFF", 
                        font=("Arial", 12), 
                        rowheight=30)       
        
        # Header style
        style.configure("Treeview.Heading", 
                        font=("Arial", 13, "bold"),
                        background="#00704A",   # Starbucks Green Header
                        foreground="white",
                        relief="flat")
        
        style.map("Treeview", background=[('selected', '#1f5e47')])

    def show_login(self):
        for widget in self.container.winfo_children(): widget.destroy()
        LoginUI(self.container, self).pack(fill="both", expand=True)

    def show_dashboard(self):
        for widget in self.container.winfo_children(): widget.destroy()
        DashboardUI(self.container, self).pack(fill="both", expand=True)

    def logout(self):
        self.current_user = None
        self.show_login()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()