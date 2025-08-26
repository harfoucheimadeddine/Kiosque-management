# models.py (fixed with subtotal handling and explicit get_item)
import sqlite3
from datetime import datetime
from contextlib import contextmanager

DB_PATH = "store.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        # Settings table
        c.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY,
                shop_name TEXT NOT NULL DEFAULT 'متجري',
                contact TEXT,
                location TEXT,
                currency TEXT DEFAULT 'د.ج'
            )
        """)
        # Categories table
        c.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            )
        """)
        # Items table (with purchase_price column)
        c.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category_id INTEGER,
                barcode TEXT UNIQUE,
                price REAL NOT NULL DEFAULT 0,
                purchase_price REAL DEFAULT 0,
                stock_count REAL DEFAULT 0,
                photo_path TEXT,
                add_date TEXT,
                FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE SET NULL
            )
        """)
        # Sales table (with total_purchase_price column)
        c.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY,
                datetime TEXT NOT NULL,
                total_price REAL NOT NULL,
                total_purchase_price REAL NOT NULL DEFAULT 0
            )
        """)
        # Sale Details table (with subtotal and purchase_price_each columns)
        c.execute("""
            CREATE TABLE IF NOT EXISTS sale_details (
                id INTEGER PRIMARY KEY,
                sale_id INTEGER NOT NULL,
                item_id INTEGER,
                quantity REAL NOT NULL,
                price_each REAL NOT NULL,
                purchase_price_each REAL DEFAULT 0,
                subtotal REAL NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales (id) ON DELETE CASCADE,
                FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE SET NULL
            )
        """)

        # Create indexes if they don't exist
        c.execute("CREATE INDEX IF NOT EXISTS idx_items_barcode ON items(barcode)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_items_category_id ON items(category_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_sales_datetime ON sales(datetime)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_sale_details_sale_id ON sale_details(sale_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_sale_details_item_id ON sale_details(item_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_items_purchase_price ON items(purchase_price)") # Index for purchase price
        c.execute("CREATE INDEX IF NOT EXISTS idx_sales_total_purchase_price ON sales(total_purchase_price)") # Index for sales total purchase price
        c.execute("CREATE INDEX IF NOT EXISTS idx_sale_details_purchase_price_each ON sale_details(purchase_price_each)") # Index for sale details purchase price
        c.execute("CREATE INDEX IF NOT EXISTS idx_sale_details_subtotal ON sale_details(subtotal)") # Index for subtotal

        conn.commit()

        # Seed data if new DB
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM categories")
        if cur.fetchone()[0] == 0:
            print("Seeding initial data...")
            cur.execute("INSERT OR IGNORE INTO categories(name) VALUES (?)", ("غير مصنّف",))
            for cat in ["مواد غذائية", "مشروبات", "منظفات", "أدوات منزلية", "قرطاسية"]:
                cur.execute("INSERT OR IGNORE INTO categories(name) VALUES (?)", (cat,))
            conn.commit()
            print("Initial data seeded.")

def get_settings():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM settings WHERE id = 1")
        settings = c.fetchone()
        if settings:
            return dict(settings)
        return None

def save_settings(shop_name, contact, location, currency):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO settings (id, shop_name, contact, location, currency)
            VALUES (1, ?, ?, ?, ?)
        """, (shop_name, contact, location, currency))
        conn.commit()

def add_category(name):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO categories(name) VALUES (?)", (name,))
        conn.commit()

def get_categories():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM categories ORDER BY name")
        return [dict(row) for row in c.fetchall()]

def get_category_by_name(name):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM categories WHERE name = ?", (name,))
        cat = c.fetchone()
        return dict(cat) if cat else None

def add_item(name, category_id, barcode, price, stock_count, photo_path, purchase_price=0):
    with get_db() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO items(name, category_id, barcode, price, stock_count, photo_path, add_date, purchase_price) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (name, category_id, barcode, price, stock_count, photo_path, datetime.now().isoformat(), purchase_price)
        )
        conn.commit()

def update_item(item_id, name, category_id, barcode, price, stock_count, photo_path, purchase_price=0):
    with get_db() as conn:
        c = conn.cursor()
        c.execute(
            "UPDATE items SET name=?, category_id=?, barcode=?, price=?, stock_count=?, photo_path=?, purchase_price=? WHERE id=?",
            (name, category_id, barcode, price, stock_count, photo_path, purchase_price, item_id)
        )
        conn.commit()

def delete_item(item_id):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM items WHERE id=?", (item_id,))
        conn.commit()

def get_items():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT i.*, c.name as category_name 
            FROM items i 
            LEFT JOIN categories c ON i.category_id = c.id
            ORDER BY i.name
        """)
        return [dict(row) for row in c.fetchall()]

def get_item_by_barcode(barcode):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT i.*, c.name as category_name 
            FROM items i 
            LEFT JOIN categories c ON i.category_id = c.id 
            WHERE i.barcode = ?
        """, (barcode,))
        item = c.fetchone()
        return dict(item) if item else None

# NEW: Explicit get_item function returning a dictionary
def get_item(item_id):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT i.*, c.name as category_name 
            FROM items i 
            LEFT JOIN categories c ON i.category_id = c.id 
            WHERE i.id = ?
        """, (item_id,))
        item = c.fetchone()
        return dict(item) if item else None

def search_items_by_name(name_query):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT i.*, c.name as category_name 
            FROM items i 
            LEFT JOIN categories c ON i.category_id = c.id 
            WHERE i.name LIKE ?
            ORDER BY i.name
        """, (f"%{name_query}%",))
        return [dict(row) for row in c.fetchall()]

def add_sale(total_price, total_purchase_price, sale_datetime=None):
    with get_db() as conn:
        c = conn.cursor()
        if sale_datetime is None:
            sale_datetime = datetime.now().isoformat()
        c.execute(
            "INSERT INTO sales(datetime, total_price, total_purchase_price) VALUES (?, ?, ?)",
            (sale_datetime, total_price, total_purchase_price)
        )
        conn.commit()
        return c.lastrowid

def add_sale_detail(sale_id, item_id, quantity, price_each, purchase_price_each):
    with get_db() as conn:
        c = conn.cursor()
        subtotal = quantity * price_each
        c.execute(
            "INSERT INTO sale_details(sale_id, item_id, quantity, price_each, purchase_price_each, subtotal) VALUES (?, ?, ?, ?, ?, ?)",
            (sale_id, item_id, quantity, price_each, purchase_price_each, subtotal)
        )
        
        # Deduct from stock_count
        c.execute("UPDATE items SET stock_count = stock_count - ? WHERE id = ?", (quantity, item_id))
        conn.commit()

def get_sales():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM sales ORDER BY datetime DESC")
        return [dict(row) for row in c.fetchall()]

def get_sale_details(sale_id):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT sd.*, i.name as item_name, i.barcode as item_barcode
            FROM sale_details sd
            JOIN items i ON sd.item_id = i.id
            WHERE sd.sale_id = ?
            ORDER BY i.name
        """, (sale_id,))
        return [dict(row) for row in c.fetchall()]

def delete_sale(sale_id):
    with get_db() as conn:
        c = conn.cursor()
        # First, get details to return items to stock
        c.execute("SELECT item_id, quantity FROM sale_details WHERE sale_id = ?", (sale_id,))
        details = c.fetchall()
        for detail in details:
            c.execute("UPDATE items SET stock_count = stock_count + ? WHERE id = ?", (detail["quantity"], detail["item_id"]))
        
        # Then delete the sale and its details (ON DELETE CASCADE handles sale_details)
        c.execute("DELETE FROM sales WHERE id = ?", (sale_id,))
        conn.commit()

def delete_sale_detail(detail_id):
    with get_db() as conn:
        c = conn.cursor()
        # Get detail to return item to stock
        c.execute("SELECT item_id, quantity FROM sale_details WHERE id=?", (detail_id,))
        detail = c.fetchone()
        
        if detail:
            # Return quantity to stock
            c.execute("UPDATE items SET stock_count = stock_count + ? WHERE id = ?", (detail["quantity"], detail["item_id"]))
            # Delete the detail
            c.execute("DELETE FROM sale_details WHERE id=?", (detail_id,))
            conn.commit()

def update_sale_detail(detail_id, quantity, price_each):
    with get_db() as conn:
        c = conn.cursor()
        
        # Get current detail to calculate stock difference
        c.execute("SELECT item_id, quantity FROM sale_details WHERE id=? ", (detail_id,))
        old_detail = c.fetchone()
        
        if old_detail:
            # Calculate quantity difference
            quantity_diff = old_detail["quantity"] - quantity # If new qty is less, diff is positive (stock increases)
            
            # Update stock
            c.execute("UPDATE items SET stock_count = stock_count + ? WHERE id = ?", 
                     (quantity_diff, old_detail["item_id"]))
        
        # Update sale detail
        subtotal = quantity * price_each
        c.execute(
            "UPDATE sale_details SET quantity=?, price_each=?, subtotal=? WHERE id=?",
            (quantity, price_each, subtotal, detail_id)
        )
        
        # Update parent sale's total_price and total_purchase_price
        c.execute("SELECT sale_id FROM sale_details WHERE id=?", (detail_id,))
        sale_id = c.fetchone()["sale_id"]
        
        c.execute("SELECT SUM(subtotal) FROM sale_details WHERE sale_id=?", (sale_id,))
        new_total_price = c.fetchone()[0] or 0.0

        c.execute("SELECT SUM(quantity * purchase_price_each) FROM sale_details WHERE sale_id=?", (sale_id,))
        new_total_purchase_price = c.fetchone()[0] or 0.0

        c.execute("UPDATE sales SET total_price=?, total_purchase_price=? WHERE id=?", 
                  (new_total_price, new_total_purchase_price, sale_id))
        
        conn.commit()


def get_sales_total():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT COALESCE(SUM(total_price), 0) as total FROM sales")
        result = c.fetchone()
        return result["total"] if result else 0

def get_sales_summary_today():
    with get_db() as conn:
        c = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        c.execute("SELECT COALESCE(SUM(total_price), 0) as total FROM sales WHERE datetime LIKE ?", (f"{today}%",))
        result = c.fetchone()
        return result["total"] if result else 0

def get_latest_sale():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM sales ORDER BY datetime DESC LIMIT 1")
        sale = c.fetchone()
        return dict(sale) if sale else None

def get_revenue_and_profit_all_time():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT COALESCE(SUM(total_price), 0) as total_revenue, COALESCE(SUM(total_price - total_purchase_price), 0) as total_profit FROM sales")
        result = c.fetchone()
        return dict(result) if result else {"total_revenue": 0, "total_profit": 0}

def get_revenue_and_profit_today():
    with get_db() as conn:
        c = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        c.execute("SELECT COALESCE(SUM(total_price), 0) as total_revenue, COALESCE(SUM(total_price - total_purchase_price), 0) as total_profit FROM sales WHERE datetime LIKE ?", (f"{today}%",))
        result = c.fetchone()
        return dict(result) if result else {"total_revenue": 0, "total_profit": 0}
