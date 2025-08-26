import models
import database
from datetime import datetime, timedelta
import random
from faker import Faker

fake = Faker('ar_SA') # Use Arabic locale for names

def add_default_categories():
    """Ensures default categories exist in the database."""
    default_cats = ["غير مصنّف", "مواد غذائية", "مشروبات", "منظفات", "أدوات منزلية", "قرطاسية", "إلكترونيات", "ملابس", "حلويات", "خضروات وفواكه", "لحوم وأسماك"]
    for cat_name in default_cats:
        try:
            models.add_category(cat_name)
            # print(f"Added category: {cat_name}") # Suppress for cleaner output
        except Exception:
            pass # Ignore if category already exists

def generate_items_data(num_items=100):
    """Generates a list of dictionaries for sample items."""
    print(f"\nGenerating {num_items} sample items...")
    items = []
    categories = models.get_categories()
    if not categories:
        print("Error: No categories found. Please ensure categories are seeded.")
        return []

    category_ids = [cat['id'] for cat in categories]
    # Keep track of generated barcodes to ensure uniqueness in this run
    generated_barcodes = set()

    # Try to add items until num_items is reached or we can't generate unique barcodes
    while len(items) < num_items:
        item_name = fake.word() + " " + fake.word() + " " + str(random.randint(1, 100)) # More varied names
        barcode = str(random.randint(100000000000, 9999999999999)) # 13-digit barcode
        
        # Ensure barcode is unique
        if barcode in generated_barcodes:
            continue
        
        generated_barcodes.add(barcode)

        price = round(random.uniform(10.0, 1000.0), 2)
        purchase_price = round(price * random.uniform(0.6, 0.9), 2) # 60-90% of selling price
        stock_count = random.randint(0, 200) # Varied stock levels
        category_id = random.choice(category_ids)
        
        items.append({
            'name': item_name,
            'category_id': category_id,
            'barcode': barcode,
            'price': price,
            'purchase_price': purchase_price,
            'stock_count': float(stock_count), # Ensure float type
            'photo_path': None, # No photos for sample data
            'add_date': datetime.now().isoformat()
        })
    return items

def populate_items(items_data):
    """Inserts generated item data into the database."""
    all_barcodes = set()
    # Get existing barcodes to prevent conflicts
    for item in models.get_items():
        if item['barcode']:
            all_barcodes.add(item['barcode'])

    added_count = 0
    for item in items_data:
        if item['barcode'] in all_barcodes:
            continue # Skip if barcode already exists in DB or was already added in this run

        try:
            models.add_item(
                item['name'], item['category_id'], item['barcode'],
                item['price'], item['stock_count'], item['photo_path'],
                purchase_price=item['purchase_price']
            )
            all_barcodes.add(item['barcode']) 
            added_count += 1
        except Exception as e:
            # print(f"Error adding item '{item['name']}' (barcode: {item['barcode']}): {e}")
            pass # Ignore errors, likely unique constraint violations

    print(f"Added {added_count} new items to the database.")

def generate_sales_data(num_sales=100):
    """Generates sales data over a period of time."""
    print(f"\nGenerating {num_sales} sample sales...")
    sales_to_add = []
    
    # Get all items with stock from the database
    all_current_items = models.get_items()
    items_with_stock = {item['id']: item for item in all_current_items if item['stock_count'] > 0}
    
    if not items_with_stock:
        print("No items with available stock found to create sales. Please add items with stock first.")
        return []

    item_ids = list(items_with_stock.keys())

    end_date = datetime.now()
    # Spread sales over the last 90 days
    start_date = end_date - timedelta(days=90) 

    for sale_idx in range(num_sales):
        sale_date = start_date + timedelta(days=random.randint(0, 90), 
                                           hours=random.randint(0, 23), 
                                           minutes=random.randint(0, 59))
        
        # Each sale will have 1 to 5 different items
        num_details = random.randint(1, 5)
        # Ensure we don't try to sample more items than are available with stock
        selected_item_ids = random.sample(item_ids, min(num_details, len(item_ids)))
        
        current_sale_details = []
        total_price = 0.0
        total_purchase_price = 0.0

        for item_id in selected_item_ids:
            item_info = items_with_stock.get(item_id) # Get item info from our pre-filtered dict
            
            if item_info and item_info['stock_count'] > 0:
                max_qty = int(item_info['stock_count']) # Cannot sell more than available stock
                quantity = random.randint(1, max(1, min(5, max_qty))) # Sell 1 to 5, or up to available stock
                
                if quantity > 0:
                    price_each = item_info['price']
                    purchase_price_each = item_info['purchase_price']
                    subtotal = price_each * quantity
                    
                    current_sale_details.append({
                        'item_id': item_id,
                        'quantity': float(quantity), # Ensure float type
                        'price_each': price_each,
                        'purchase_price_each': purchase_price_each,
                        'subtotal': subtotal
                    })
                    total_price += subtotal
                    total_purchase_price += purchase_price_each * quantity
            
        if current_sale_details: # Only add sale if it has details
            sales_to_add.append({
                'datetime': sale_date.isoformat(),
                'total_price': total_price,
                'total_purchase_price': total_purchase_price,
                'details': current_sale_details
            })
        else:
            print(f"Skipped generating sale {sale_idx+1} due to no available items or insufficient stock.")

    print(f"Generated {len(sales_to_add)} valid sales to be added.")
    return sales_to_add

def populate_sales(sales_data):
    """Inserts generated sales data into the database."""
    added_sales_count = 0
    added_details_count = 0
    
    for sale in sales_data:
        try:
            sale_id = models.add_sale(
                sale['total_price'], sale['total_purchase_price'], sale['datetime']
            )
            for detail in sale['details']:
                models.add_sale_detail(
                    sale_id, detail['item_id'], detail['quantity'], 
                    detail['price_each'], detail['purchase_price_each']
                )
                added_details_count += 1
            added_sales_count += 1
        except Exception as e:
            print(f"Error adding sale on {sale['datetime']}: {e}")

    print(f"Added {added_sales_count} new sales and {added_details_count} sale details to the database.")

if __name__ == "__main__":
    print("Starting database population...")
    database.setup_database() # Ensure DB structure is set up
    add_default_categories()

    # Populate items
    items_data = generate_items_data(num_items=100)
    populate_items(items_data)

    # Populate sales (item_ids are fetched dynamically within the function)
    sales_data = generate_sales_data(num_sales=100)
    populate_sales(sales_data)

    print("\nDatabase population completed.")
    print("You can now run your main application (`python main.py`) to see the populated data.")
