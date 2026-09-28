"""
setup_oms_database.py
Creates and seeds the OMS database tables for Meridian Freight Group.
Deliberately injects data quality issues for realistic pipeline testing.
"""

import os
import pyodbc
import random
from faker import Faker
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

fake = Faker('en_AU')

# --- Connection ---
def get_connection():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.getenv('SQL_SERVER')};"
        f"DATABASE={os.getenv('SQL_DATABASE')};"
        f"UID={os.getenv('SQL_USERNAME')};"
        f"PWD={os.getenv('SQL_PASSWORD')};"
    )
    return pyodbc.connect(conn_str)


# --- Create Tables ---
def create_tables(conn):
    cursor = conn.cursor()

    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='merchants' AND xtype='U')
        CREATE TABLE merchants (
            merchant_id     VARCHAR(20) PRIMARY KEY,
            merchant_name   VARCHAR(100),
            merchant_state  VARCHAR(10),
            created_at      DATETIME DEFAULT GETDATE()
        )
    """)

    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='carriers' AND xtype='U')
        CREATE TABLE carriers (
            carrier_id      VARCHAR(20) PRIMARY KEY,
            carrier_name    VARCHAR(100),
            carrier_type    VARCHAR(50)
        )
    """)

    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='orders' AND xtype='U')
        CREATE TABLE orders (
            order_id            VARCHAR(30) PRIMARY KEY,
            merchant_id         VARCHAR(20),
            carrier_id          VARCHAR(20),
            pickup_address      VARCHAR(200),
            pickup_postcode     VARCHAR(10),
            delivery_address    VARCHAR(200),
            delivery_postcode   VARCHAR(10),
            order_status        VARCHAR(30),
            declared_value      DECIMAL(10,2),
            created_at          DATETIME,
            updated_at          DATETIME
        )
    """)

    conn.commit()
    print("Tables created successfully.")


# --- Seed Carriers ---
def seed_carriers(conn):
    cursor = conn.cursor()
    carriers = [
        ('CAR001', 'Australia Post', 'Parcel'),
        ('CAR002', 'StarTrack', 'Express'),
        ('CAR003', 'Team Global Express', 'General Freight'),
        ('CAR004', 'Toll Group', 'General Freight'),
        ('CAR005', 'CouriersPlease', 'Parcel'),
    ]
    for c in carriers:
        cursor.execute("""
            IF NOT EXISTS (SELECT 1 FROM carriers WHERE carrier_id = ?)
            INSERT INTO carriers VALUES (?, ?, ?)
        """, c[0], c[0], c[1], c[2])
    conn.commit()
    print("Carriers seeded.")


# --- Seed Merchants ---
def seed_merchants(conn):
    cursor = conn.cursor()
    states = ['NSW', 'VIC', 'QLD', 'SA', 'WA', 'TAS']
    for i in range(1, 51):
        merchant_id = f'MER{i:04d}'
        cursor.execute("""
            IF NOT EXISTS (SELECT 1 FROM merchants WHERE merchant_id = ?)
            INSERT INTO merchants (merchant_id, merchant_name, merchant_state)
            VALUES (?, ?, ?)
        """, merchant_id, merchant_id,
             fake.company(), random.choice(states))
    conn.commit()
    print("Merchants seeded.")


# --- Seed Orders ---
def seed_orders(conn):
    cursor = conn.cursor()
    statuses = ['CREATED', 'PICKED_UP', 'IN_TRANSIT', 'OUT_FOR_DELIVERY',
                'DELIVERED', 'FAILED_DELIVERY', 'RETURNED']
    carrier_ids = ['CAR001', 'CAR002', 'CAR003', 'CAR004', 'CAR005']

    for i in range(1, 201):
        order_id = f'ORD{i:06d}'
        merchant_id = f'MER{random.randint(1, 50):04d}'
        carrier_id = random.choice(carrier_ids)
        created_at = datetime.now() - timedelta(days=random.randint(1, 30))
        updated_at = created_at + timedelta(hours=random.randint(1, 48))

        # Deliberate data quality issues
        delivery_postcode = fake.postcode()
        if random.random() < 0.05:        # 5% missing postcodes
            delivery_postcode = None
        if random.random() < 0.03:        # 3% invalid postcodes
            delivery_postcode = 'XXXX'

        declared_value = round(random.uniform(10, 2000), 2)
        if random.random() < 0.02:        # 2% negative values
            declared_value = -declared_value

        cursor.execute("""
            IF NOT EXISTS (SELECT 1 FROM orders WHERE order_id = ?)
            INSERT INTO orders (order_id, merchant_id, carrier_id,
                pickup_address, pickup_postcode,
                delivery_address, delivery_postcode,
                order_status, declared_value, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, order_id, order_id, merchant_id, carrier_id,
             fake.street_address(), fake.postcode(),
             fake.street_address(), delivery_postcode,
             random.choice(statuses), declared_value,
             created_at, updated_at)

    conn.commit()
    print("Orders seeded — 200 rows with deliberate quality issues.")


# --- Main ---
if __name__ == "__main__":
    print("Connecting to database...")
    conn = get_connection()
    print("Connected.")
    create_tables(conn)
    seed_carriers(conn)
    seed_merchants(conn)
    seed_orders(conn)
    conn.close()
    print("Done.")