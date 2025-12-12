import sqlite3
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_NAME = "fitmeal.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with tables."""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS plans (
            user_id TEXT PRIMARY KEY,
            plan_data TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id TEXT PRIMARY KEY,
            data TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_plan(user_id, plan_data):
    """Save a generated plan for a user."""
    conn = get_db_connection()
    conn.execute('INSERT OR REPLACE INTO plans (user_id, plan_data) VALUES (?, ?)',
                 (user_id, json.dumps(plan_data)))
    conn.commit()
    conn.close()

def get_plan(user_id):
    """Retrieve a saved plan."""
    conn = get_db_connection()
    row = conn.execute('SELECT plan_data FROM plans WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    if row:
        return json.loads(row['plan_data'])
    return None

def save_recipe(recipe_id, recipe_data):
    """Save a recipe detail."""
    conn = get_db_connection()
    conn.execute('INSERT OR REPLACE INTO recipes (id, data) VALUES (?, ?)',
                 (recipe_id, json.dumps(recipe_data)))
    conn.commit()
    conn.close()

def get_recipe(recipe_id):
    """Retrieve a recipe."""
    conn = get_db_connection()
    row = conn.execute('SELECT data FROM recipes WHERE id = ?', (recipe_id,)).fetchone()
    conn.close()
    if row:
        return json.loads(row['data'])
    return None

def create_user(username, password, user_id):
    """Create a new user."""
    conn = get_db_connection()
    try:
        hashed_pw = generate_password_hash(password)
        conn.execute('INSERT INTO users (id, username, password) VALUES (?, ?, ?)',
                     (user_id, username, hashed_pw))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    """Verify user credentials and return user_id if valid."""
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password'], password):
        return user['id']
    return None

