import sqlite3
import random

product_names = ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'USB Cable', 'Webcam', 'Headset', 'SSD', 'RAM', 'GPU']
descriptions = ['High performance', 'Ergonomic', 'Mechanical', '4K Ultra HD', 'Fast charging', 'Noise cancelling', '1TB storage', '16GB', 'RTX 4080']

def seed_products():
    conn = sqlite3.connect('product-service/products.db')
    c = conn.cursor()
    c.execute('DELETE FROM product')
    for i in range(5):
        name = random.choice(product_names)
        desc = random.choice(descriptions)
        price = round(random.uniform(20, 1500), 2)
        c.execute('INSERT INTO product (name, description, price) VALUES (?,?,?)', (name, desc, price))
    conn.commit()
    conn.close()
    print("Seeded products table")

def seed_inventory():
    conn = sqlite3.connect('inventory-service/inventory.db')
    c = conn.cursor()
    c.execute('DELETE FROM inventory')
    for pid in range(1, 6):
        qty = random.randint(10, 100)
        c.execute('INSERT INTO inventory (product_id, quantity) VALUES (?,?)', (pid, qty))
    conn.commit()
    conn.close()
    print("Seeded inventory table")

def seed_orders():
    conn = sqlite3.connect('order-service/orders.db')
    c = conn.cursor()
    c.execute('DELETE FROM "order"')
    for i in range(3):
        pid = random.randint(1, 5)
        qty = random.randint(1, 5)
        total = round(qty * random.uniform(50, 1000), 2)
        c.execute('INSERT INTO "order" (product_id, quantity, total_price, created_at) VALUES (?,?,?, datetime("now"))', (pid, qty, total))
    conn.commit()
    conn.close()
    print("Seeded orders table")

if __name__ == '__main__':
    seed_products()
    seed_inventory()
    seed_orders()