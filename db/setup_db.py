import base64
import hashlib
import os
import sqlite3
from pathlib import Path

DB_PATH = Path("db/app.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    salt_b64 = base64.b64encode(salt).decode("ascii")
    derived_b64 = base64.b64encode(derived).decode("ascii")
    return f"{salt_b64}${derived_b64}"

# Drop tables to guarantee consistent schema for local tests
cursor.execute("DROP TABLE IF EXISTS orders")
cursor.execute("DROP TABLE IF EXISTS items")
cursor.execute("DROP TABLE IF EXISTS product_model")
cursor.execute("DROP TABLE IF EXISTS users")

# Product model table
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS product_model (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL
)
"""
)

# Products table (mapped as items in the app)
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    sku TEXT UNIQUE NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    product_model_id INTEGER,
    FOREIGN KEY (product_model_id) REFERENCES product_model (id)
)
"""
)

# Users table
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1
)
"""
)

# Orders table
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    total_price REAL NOT NULL DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES items (id)
)
"""
)

# 3 test product models (id, title)
product_models = [
    ("Fruit Basic",),
    ("Fruit Premium",),
    ("Fruit Export",),
]
cursor.executemany(
    """
INSERT INTO product_model (title)
VALUES (?)
""",
    product_models,
)

# 3 test products
products = [
    ("Apple", 5.0, "ITEM-APPLE-001", 120, 1),
    ("Banana", 3.0, "ITEM-BANANA-001", 80, 2),
    ("Orange", 4.5, "ITEM-ORANGE-001", 95, 3),
]
cursor.executemany(
    """
INSERT INTO items (name, price, sku, stock, product_model_id)
VALUES (?, ?, ?, ?, ?)
""",
    products,
)

# 3 test users (active) for login
users = [
    ("admin", "admin@example.com", hash_password("admin1234"), "ADMIN", 1),
    ("jdoe", "jdoe@example.com", hash_password("jdoe1234"), "EDITOR", 1),
    ("viewer", "viewer@example.com", hash_password("viewer1234"), "VIEWER", 1),
]
cursor.executemany(
    """
INSERT INTO users (username, email, password_hash, role, is_active)
VALUES (?, ?, ?, ?, ?)
""",
    users,
)

# 3 test orders
orders = [
    (1, 2, 10.0),
    (2, 10, 30.0),
    (3, 4, 18.0),
]
cursor.executemany(
    """
INSERT INTO orders (product_id, quantity, total_price)
VALUES (?, ?, ?)
""",
    orders,
)

conn.commit()
conn.close()

print(f"Database seeded at: {DB_PATH}")
print("ProductModels: 3 | Products: 3 | Users: 3 | Orders: 3")
