"""Seed database with realistic customer data."""

from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Date, text
from sqlalchemy.orm import sessionmaker
import random

from config import settings

engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def seed_database():
    """Create tables and populate with realistic customer data."""

    # Create tables using raw SQL
    with engine.connect() as conn:
        # Customers table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                country TEXT,
                region TEXT,
                segment TEXT,
                created_at DATE
            )
        """))

        # Orders table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                order_date DATE,
                total_amount REAL,
                status TEXT
            )
        """))

        # Products table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY,
                name TEXT,
                category TEXT,
                price REAL,
                stock INTEGER
            )
        """))

        # Order items table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS order_items (
                order_item_id INTEGER PRIMARY KEY,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER,
                unit_price REAL
            )
        """))

        conn.commit()

    # Seed data
    session = SessionLocal()

    # Check if data already exists
    result = session.execute(text("SELECT COUNT(*) FROM customers"))
    if result.scalar() > 0:
        print("Database already seeded. Skipping...")
        session.close()
        return

    # Countries and regions
    regions_map = {
        'USA': ['Northeast', 'Southeast', 'Midwest', 'West'],
        'Canada': ['Eastern', 'Central', 'Western'],
        'UK': ['England', 'Scotland', 'Wales'],
        'Germany': ['North', 'Central', 'South'],
        'France': ['Northern', 'Central', 'Southern'],
        'Japan': ['Tokyo', 'Kansai', 'Kyushu'],
        'Australia': ['New South Wales', 'Victoria', 'Queensland'],
        'Brazil': ['Southeast', 'South', 'Northeast'],
    }

    segments = ['Enterprise', 'Mid-Market', 'SMB', 'Startup']

    # Generate customers
    customer_names = [
        'Acme Corp', 'Blue Sky Inc', 'CloudVenture', 'DataFlow Systems', 'EdgeTech',
        'FutureScale', 'GlobalNet', 'HyperGrow', 'InnovatePro', 'JumpStart Digital',
        'KineticForce', 'LeverageAI', 'MotivaConsult', 'NexusVentures', 'OmniTech',
        'PeakPerformance', 'QuantumLeap', 'RapidScale', 'SynergyTech', 'TrustVault',
        'UltraFlow', 'VelocityMark', 'WaveSync', 'XcellusBiz', 'YieldPro',
        'ZenithCorp', 'AlphaStream', 'BraveVenture', 'CatalystHub', 'DeltaForce',
        'EchoPath', 'FlexiTech', 'GrowthLabs', 'HeritageGroup', 'ImpactZone'
    ]

    product_data = [
        ('Enterprise Platform', 'Software', 50000),
        ('Cloud Analytics', 'Software', 35000),
        ('Security Suite', 'Software', 25000),
        ('Data Warehouse', 'Software', 45000),
        ('API Gateway', 'Software', 20000),
        ('Integration Hub', 'Software', 30000),
        ('BI Dashboard', 'Software', 15000),
        ('Migration Tools', 'Services', 40000),
        ('Professional Services', 'Services', 12000),
        ('Support Premium', 'Services', 5000),
        ('Training Program', 'Services', 8000),
        ('Consulting', 'Services', 15000),
    ]

    # Insert products
    for i, (name, category, price) in enumerate(product_data, 1):
        session.execute(text("""
            INSERT INTO products (product_id, name, category, price, stock)
            VALUES (:id, :name, :category, :price, :stock)
        """), {
            'id': i,
            'name': name,
            'category': category,
            'price': price,
            'stock': random.randint(10, 100)
        })

    # Insert customers
    countries = list(regions_map.keys())
    customer_id = 1

    for name in customer_names:
        country = random.choice(countries)
        region = random.choice(regions_map[country])
        segment = random.choice(segments)
        created_date = datetime.now() - timedelta(days=random.randint(30, 730))

        session.execute(text("""
            INSERT INTO customers (customer_id, name, email, country, region, segment, created_at)
            VALUES (:id, :name, :email, :country, :region, :segment, :created_at)
        """), {
            'id': customer_id,
            'name': name,
            'email': f'{name.lower().replace(" ", ".")}@example.com',
            'country': country,
            'region': region,
            'segment': segment,
            'created_at': created_date.date()
        })
        customer_id += 1

    session.commit()

    # Insert orders and order items
    order_id = 1
    order_item_id = 1

    for cust_id in range(1, customer_id):
        # Each customer has 2-8 orders
        num_orders = random.randint(2, 8)

        for _ in range(num_orders):
            order_date = datetime.now() - timedelta(days=random.randint(1, 700))

            # 2-5 items per order
            num_items = random.randint(2, 5)
            order_total = 0

            # Generate order items
            item_ids = random.sample(range(1, len(product_data) + 1), min(num_items, len(product_data)))

            for prod_id in item_ids:
                qty = random.randint(1, 5)
                # Get product price
                prod_price = [p[2] for i, p in enumerate(product_data, 1) if i == prod_id][0]
                item_total = qty * prod_price
                order_total += item_total

                session.execute(text("""
                    INSERT INTO order_items (order_item_id, order_id, product_id, quantity, unit_price)
                    VALUES (:id, :order_id, :product_id, :qty, :price)
                """), {
                    'id': order_item_id,
                    'order_id': order_id,
                    'product_id': prod_id,
                    'qty': qty,
                    'price': prod_price
                })
                order_item_id += 1

            # Insert order
            status = random.choice(['completed', 'completed', 'completed', 'pending', 'shipped'])

            session.execute(text("""
                INSERT INTO orders (order_id, customer_id, order_date, total_amount, status)
                VALUES (:id, :customer_id, :order_date, :total, :status)
            """), {
                'id': order_id,
                'customer_id': cust_id,
                'order_date': order_date.date(),
                'total': round(order_total, 2),
                'status': status
            })
            order_id += 1

    session.commit()
    print(f"✓ Database seeded: {customer_id - 1} customers, {order_id - 1} orders, {order_item_id - 1} order items")
    session.close()


if __name__ == "__main__":
    seed_database()
