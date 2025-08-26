# database.py (fixed with subtotal column in sale_details table and new purchase price columns)
import sqlite3
import os
import threading
from datetime import datetime

DB_NAME = "store.db"
_db_lock = threading.RLock()

def get_connection():
    """
    Get database connection with proper configuration and timeout handling.
    - timeout=10 sec: Prevents 'database is locked' errors during fast UI operations.
    - WAL mode: Better concurrency for read/write.
    """
    conn = sqlite3.connect(DB_NAME, timeout=30)  # Increased timeout for large datasets
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")       # Allows concurrent reads during writes
    conn.execute("PRAGMA synchronous = NORMAL;")     # Good balance of safety and performance
    conn.execute("PRAGMA cache_size = -10000;")      # 10MB cache for better performance
    conn.execute("PRAGMA temp_store = MEMORY;")      # Store temp tables in memory
    return conn

def _table_has_item_fk_cascade_on_sale_details(conn):
    """Check if sale_details table has CASCADE foreign key for items"""
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_key_list(sale_details)")
    fks = cur.fetchall()
    for fk in fks:
        if fk["table"] == "items" and fk["from"] == "item_id" and fk["on_delete"].lower() == "cascade":
            return True
    return False

def _table_has_column(conn, table_name, column_name):
    """Check if a table has a specific column"""
    cur = conn.cursor()
    try:
        cur.execute(f"PRAGMA table_info({table_name})")
        columns = cur.fetchall()
        for column in columns:
            if column['name'] == column_name:
                return True
        return False
    except:
        return False

def setup_database():
    """Setup database with all required tables and indexes"""
    must_seed = not os.path.exists(DB_NAME)
    conn = get_connection()
    cur = conn.cursor()

    # Settings table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY CHECK (id=1),
        shop_name TEXT NOT NULL,
        contact TEXT,
        location TEXT,
        currency TEXT NOT NULL
    );
    """)

    # Categories table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        created_at TEXT
    );
    """)

    # Items table with purchase_price
    cur.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category_id INTEGER,
        barcode TEXT UNIQUE,
        price REAL NOT NULL DEFAULT 0,
        stock_count REAL NOT NULL DEFAULT 0,
        photo_path TEXT,
        add_date TEXT,
        updated_at TEXT,
        purchase_price REAL NOT NULL DEFAULT 0,
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
    );
    """)

    # Sales table - Updated with total_purchase_price
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        datetime TEXT NOT NULL,
        total_price REAL NOT NULL DEFAULT 0,
        total_purchase_price REAL NOT NULL DEFAULT 0, -- NEW: Added for profit calculation
        created_at TEXT
    );
    """)

    # Sale details table - FIXED: Added subtotal column, NEW: purchase_price_each
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sale_details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        quantity REAL NOT NULL,
        price_each REAL NOT NULL,
        subtotal REAL NOT NULL DEFAULT 0,
        purchase_price_each REAL NOT NULL DEFAULT 0, -- NEW: Added to record purchase price at sale time
        created_at TEXT,
        FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
        FOREIGN KEY (item_id) REFERENCES items(id) -- Will migrate to CASCADE
    );
    """)

    conn.commit()

    # Add purchase_price column if it doesn't exist
    if not _table_has_column(conn, 'items', 'purchase_price'):
        print("Adding purchase_price column to items table...")
        cur.execute("ALTER TABLE items ADD COLUMN purchase_price REAL NOT NULL DEFAULT 0")
        conn.commit()

    # Add subtotal column to sale_details if it doesn't exist
    if not _table_has_column(conn, 'sale_details', 'subtotal'):
        print("Adding subtotal column to sale_details table...")
        cur.execute("ALTER TABLE sale_details ADD COLUMN subtotal REAL NOT NULL DEFAULT 0")
        # Calculate subtotal for existing records
        cur.execute("UPDATE sale_details SET subtotal = quantity * price_each WHERE subtotal = 0")
        conn.commit()
    
    # Add purchase_price_each column to sale_details if it doesn't exist
    if not _table_has_column(conn, 'sale_details', 'purchase_price_each'):
        print("Adding purchase_price_each column to sale_details table...")
        cur.execute("ALTER TABLE sale_details ADD COLUMN purchase_price_each REAL NOT NULL DEFAULT 0")
        # Populate with current item purchase prices for existing records
        cur.execute("""
            UPDATE sale_details
            SET purchase_price_each = (SELECT i.purchase_price FROM items i WHERE i.id = sale_details.item_id)
            WHERE purchase_price_each = 0;
        """)
        conn.commit()

    # Add total_purchase_price column to sales if it doesn't exist
    if not _table_has_column(conn, 'sales', 'total_purchase_price'):
        print("Adding total_purchase_price column to sales table...")
        cur.execute("ALTER TABLE sales ADD COLUMN total_purchase_price REAL NOT NULL DEFAULT 0")
        # Populate total_purchase_price for existing sales
        cur.execute("""
            UPDATE sales
            SET total_purchase_price = (
                SELECT COALESCE(SUM(sd.quantity * sd.purchase_price_each), 0)
                FROM sale_details sd
                WHERE sd.sale_id = sales.id
            )
            WHERE total_purchase_price = 0;
        """)
        conn.commit()

    # Check if created_at column exists in sales table, add if not
    if not _table_has_column(conn, 'sales', 'created_at'):
        print("Adding created_at column to sales table...")
        cur.execute("ALTER TABLE sales ADD COLUMN created_at TEXT")
        current_time = datetime.now().isoformat()
        cur.execute("UPDATE sales SET created_at = ? WHERE created_at IS NULL", (current_time,))
        conn.commit()

    # Check if created_at column exists in sale_details table, add if not
    if not _table_has_column(conn, 'sale_details', 'created_at'):
        print("Adding created_at column to sale_details table...")
        cur.execute("ALTER TABLE sale_details ADD COLUMN created_at TEXT")
        current_time = datetime.now().isoformat()
        cur.execute("UPDATE sale_details SET created_at = ? WHERE created_at IS NULL", (current_time,))
        conn.commit()

    # Check if created_at column exists in categories table, add if not
    if not _table_has_column(conn, 'categories', 'created_at'):
        print("Adding created_at column to categories table...")
        cur.execute("ALTER TABLE categories ADD COLUMN created_at TEXT")
        current_time = datetime.now().isoformat()
        cur.execute("UPDATE categories SET created_at = ? WHERE created_at IS NULL", (current_time,))
        conn.commit()

    # Check if updated_at column exists in items table, add if not
    if not _table_has_column(conn, 'items', 'updated_at'):
        print("Adding updated_at column to items table...")
        cur.execute("ALTER TABLE items ADD COLUMN updated_at TEXT")
        current_time = datetime.now().isoformat()
        cur.execute("UPDATE items SET updated_at = ? WHERE updated_at IS NULL", (current_time,))
        conn.commit()

    # Ensure CASCADE for item_id in sale_details
    # This migration step is a bit more involved due to SQLite's ALTER TABLE limitations.
    # We will create a new table, copy data, drop the old, and rename the new.
    # This step is critical for proper deletion cascades.
    cur.execute("PRAGMA foreign_keys = OFF;")
    conn.commit()

    cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='sale_details';")
    current_sale_details_schema = cur.fetchone()
    
    # Check if the existing sale_details table already has ON DELETE CASCADE for item_id
    needs_rebuild = True
    if current_sale_details_schema:
        if "FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE" in current_sale_details_schema['sql']:
            needs_rebuild = False

    if needs_rebuild:
        print("Migrating sale_details table to add CASCADE foreign key for items...")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS _sale_details_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            price_each REAL NOT NULL,
            subtotal REAL NOT NULL DEFAULT 0,
            purchase_price_each REAL NOT NULL DEFAULT 0,
            created_at TEXT,
            FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
        );
        """)

        # Copy data, including existing subtotal and purchase_price_each (if they exist)
        # Use COALESCE for created_at and default values for new columns
        cur.execute("""
        INSERT INTO _sale_details_new (id, sale_id, item_id, quantity, price_each, subtotal, purchase_price_each, created_at)
        SELECT 
            id, 
            sale_id, 
            item_id, 
            quantity, 
            price_each, 
            COALESCE(subtotal, quantity * price_each), 
            COALESCE(purchase_price_each, 0), -- Default to 0 if column didn't exist
            COALESCE(created_at, datetime('now'))
        FROM sale_details;
        """)

        cur.execute("DROP TABLE sale_details;")
        cur.execute("ALTER TABLE _sale_details_new RENAME TO sale_details;")
        conn.commit()
        print("Migration completed successfully.")

    cur.execute("PRAGMA foreign_keys = ON;")
    conn.commit()


    # Create indexes for performance
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_items_barcode ON items(barcode);",
        "CREATE INDEX IF NOT EXISTS idx_items_category ON items(category_id);",
        "CREATE INDEX IF NOT EXISTS idx_items_stock ON items(stock_count);",
        "CREATE INDEX IF NOT EXISTS idx_sales_datetime ON sales(datetime);",
        "CREATE INDEX IF NOT EXISTS idx_sale_details_sale_id ON sale_details(sale_id);",
        "CREATE INDEX IF NOT EXISTS idx_sale_details_item_id ON sale_details(item_id);",
        "CREATE INDEX IF NOT EXISTS idx_items_name ON items(name);",
        "CREATE INDEX IF NOT EXISTS idx_sales_created_at ON sales(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_items_purchase_price ON items(purchase_price);",
        "CREATE INDEX IF NOT EXISTS idx_sale_details_subtotal ON sale_details(subtotal);",
        "CREATE INDEX IF NOT EXISTS idx_sale_details_purchase_price_each ON sale_details(purchase_price_each);",
        "CREATE INDEX IF NOT EXISTS idx_sales_total_purchase_price ON sales(total_purchase_price);"
    ]
    for sql in indexes:
        try:
            cur.execute(sql)
        except:
            pass  # Ignore errors if index already exists

    conn.commit()

    # Seed data if new DB
    if must_seed:
        print("Seeding initial data...")
        cur.execute("INSERT OR IGNORE INTO categories(name, created_at) VALUES (?, ?)", 
                   ("غير مصنّف", datetime.now().isoformat()))
        for cat in ["مواد غذائية", "مشروبات", "منظفات", "أدوات منزلية", "قرطاسية"]:
            cur.execute("INSERT OR IGNORE INTO categories(name, created_at) VALUES (?, ?)", 
                       (cat, datetime.now().isoformat()))
        conn.commit()
        print("Initial data seeded.")

    conn.close()
    print("Database setup completed successfully.")

def backup_database(backup_path=None):
    """Create a backup of the database"""
    if not backup_path:
        from datetime import datetime
        backup_path = f"store_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    import shutil
    shutil.copy2(DB_NAME, backup_path)
    return backup_path

def get_database_stats():
    """Return stats: table counts & DB size"""
    conn = get_connection()
    cur = conn.cursor()
    stats = {}
    for table in ['categories', 'items', 'sales', 'sale_details']:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        stats[f"{table}_count"] = cur.fetchone()[0]
    stats['db_size_bytes'] = os.path.getsize(DB_NAME) if os.path.exists(DB_NAME) else 0
    stats['db_size_mb'] = round(stats['db_size_bytes'] / (1024*1024), 2)
    conn.close()
    return stats
