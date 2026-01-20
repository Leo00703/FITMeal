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
            status TEXT DEFAULT 'draft',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Migration: Add status column if it doesn't exist
    try:
        conn.execute('ALTER TABLE plans ADD COLUMN status TEXT DEFAULT "draft"')
    except sqlite3.OperationalError:
        pass
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id TEXT PRIMARY KEY,
            weight REAL,
            height REAL,
            sex TEXT,
            age INTEGER,
            goal TEXT,
            activity_level TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Migration: Add new columns if they don't exist
    try:
        conn.execute('ALTER TABLE user_profiles ADD COLUMN bio TEXT')
    except sqlite3.OperationalError:
        pass # Column likely exists
        
    try:
        conn.execute('ALTER TABLE user_profiles ADD COLUMN profile_pic TEXT')
    except sqlite3.OperationalError:
        pass

    conn.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            user_id TEXT,
            recipe_id TEXT,
            recipe_name TEXT,
            PRIMARY KEY (user_id, recipe_id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

def save_plan(user_id, plan_data, status='draft'):
    """Save a generated plan for a user."""
    conn = get_db_connection()
    conn.execute('INSERT OR REPLACE INTO plans (user_id, plan_data, status) VALUES (?, ?, ?)',
                 (user_id, json.dumps(plan_data), status))
    conn.commit()
    conn.close()

def update_plan_status(user_id, status):
    """Update the status of a user's plan."""
    conn = get_db_connection()
    conn.execute('UPDATE plans SET status = ? WHERE user_id = ?', (status, user_id))
    conn.commit()
    conn.close()

def get_plan(user_id):
    """Retrieve a saved plan."""
    conn = get_db_connection()
    row = conn.execute('SELECT plan_data, status FROM plans WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    if row:
        return {
            'week_plan': json.loads(row['plan_data'])['week_plan'],
            'status': row['status']
        }
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

def get_user_profile(user_id):
    """Retrieve user profile data."""
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def update_user_profile(user_id, profile_data):
    """Update or create user profile."""
    conn = get_db_connection()
    # Check if record exists to preserve existing fields if not provided in update
    existing = conn.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,)).fetchone()
    
    current_data = dict(existing) if existing else {}
    current_data.update(profile_data)
    
    conn.execute('''
        INSERT OR REPLACE INTO user_profiles (user_id, weight, height, sex, age, goal, activity_level, bio, profile_pic)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        current_data.get('weight'),
        current_data.get('height'),
        current_data.get('sex'),
        current_data.get('age'),
        current_data.get('goal'),
        current_data.get('activity_level'),
        current_data.get('bio'),
        current_data.get('profile_pic')
    ))
    conn.commit()
    conn.close()

def add_favorite(user_id, recipe_id, recipe_name):
    """Add a recipe to favorites."""
    conn = get_db_connection()
    conn.execute('INSERT OR IGNORE INTO favorites (user_id, recipe_id, recipe_name) VALUES (?, ?, ?)',
                 (user_id, recipe_id, recipe_name))
    conn.commit()
    conn.close()

def get_favorites(user_id):
    """Get user favorites."""
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM favorites WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def remove_favorite(user_id, recipe_id):
    """Remove a recipe from favorites."""
    conn = get_db_connection()
    conn.execute('DELETE FROM favorites WHERE user_id = ? AND recipe_id = ?', (user_id, recipe_id))
    conn.commit()
    conn.close()

