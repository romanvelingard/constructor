import sqlite3
import os
import hashlib

DB_FILE = "meal_planner.db"

def is_postgres():
    """Check if PostgreSQL DATABASE_URL is configured."""
    url = os.environ.get("DATABASE_URL")
    return bool(url and (url.startswith("postgres://") or url.startswith("postgresql://")))

def get_connection():
    """Return a connection to SQLite or PostgreSQL depending on environment."""
    url = os.environ.get("DATABASE_URL")
    if url and (url.startswith("postgres://") or url.startswith("postgresql://")):
        import psycopg2
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(url)
    else:
        return sqlite3.connect(DB_FILE)

def execute_query(cursor, sql, params=()):
    """Execute SQL query replacing SQLite placeholders with PostgreSQL ones if needed."""
    if is_postgres():
        sql = sql.replace('?', '%s')
        sql = sql.replace('INTEGER PRIMARY KEY AUTOINCREMENT', 'SERIAL PRIMARY KEY')
    cursor.execute(sql, params)
    return cursor

def execute_many(cursor, sql, params_list):
    """Execute batch SQL query replacing SQLite placeholders with PostgreSQL ones if needed."""
    if is_postgres():
        sql = sql.replace('?', '%s')
    cursor.executemany(sql, params_list)
    return cursor

def init_db():
    """Initialize database tables, run migrations, and seed default values."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create users table first
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()

    # Check if we need to migrate from SQLite without users (we drop old tables if they don't have user_id)
    # Check if meal_plan table exists and if it has user_id column
    migrate = False
    try:
        execute_query(cursor, "SELECT user_id FROM meal_plan LIMIT 1")
    except Exception:
        # Table doesn't exist or doesn't have user_id, trigger migration (drop tables to recreate)
        migrate = True
        if is_postgres():
            conn.rollback()
            cursor = conn.cursor()

    if migrate:
        tables_to_drop = ["meal_plan", "checked_groceries", "settings", "weight_history", "injection_history", "food_log", "profile"]
        for table in tables_to_drop:
            try:
                execute_query(cursor, f"DROP TABLE IF EXISTS {table}")
            except Exception:
                if is_postgres():
                    conn.rollback()
                    cursor = conn.cursor()
        conn.commit()

    # 1. Create foods table (global pool of foods)
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS foods (
            name TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            protein_density REAL NOT NULL,
            carbs_density REAL NOT NULL DEFAULT 0.0,
            fat_density REAL NOT NULL DEFAULT 0.0
        )
    """)

    # 2. Create user-scoped tables
    # 2.1 meal_plan
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS meal_plan (
            user_id INTEGER NOT NULL,
            day TEXT NOT NULL,
            meal_type TEXT NOT NULL,
            food_name TEXT,
            garnish_name TEXT,
            PRIMARY KEY (user_id, day, meal_type)
        )
    """)

    # 2.2 checked_groceries
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS checked_groceries (
            user_id INTEGER NOT NULL,
            item_key TEXT NOT NULL,
            PRIMARY KEY (user_id, item_key)
        )
    """)

    # 2.3 settings
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS settings (
            user_id INTEGER NOT NULL,
            setting_key TEXT NOT NULL,
            value REAL NOT NULL,
            PRIMARY KEY (user_id, setting_key)
        )
    """)

    # 2.4 weight_history
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS weight_history (
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            weight REAL NOT NULL,
            PRIMARY KEY (user_id, date)
        )
    """)

    # 2.5 injection_history
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS injection_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            medication TEXT NOT NULL,
            dose REAL NOT NULL
        )
    """)

    # 2.6 food_log
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS food_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            meal_type TEXT NOT NULL,
            food_name TEXT NOT NULL,
            garnish_name TEXT,
            food_portion REAL NOT NULL,
            garnish_portion REAL NOT NULL
        )
    """)

    # 2.7 profile
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS profile (
            user_id INTEGER NOT NULL,
            key TEXT NOT NULL,
            value TEXT,
            PRIMARY KEY (user_id, key)
        )
    """)

    conn.commit()

    # Seed default user if empty
    execute_query(cursor, "SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        h = hash_password("LedokoL10")
        execute_query(cursor, "INSERT INTO users (email, password) VALUES ('roman.vel@gmail.com', ?)", (h,))
        conn.commit()

    # Get Roman's user ID for seeding defaults
    execute_query(cursor, "SELECT id FROM users WHERE email = 'roman.vel@gmail.com'")
    roman_id = cursor.fetchone()[0]

    # Seed default foods if empty
    execute_query(cursor, "SELECT COUNT(*) FROM foods")
    if cursor.fetchone()[0] == 0:
        default_foods = [
            ('Turkey', 'Proteins', 25.0, 0.0, 1.0),
            ('Chicken', 'Proteins', 24.0, 0.0, 3.0),
            ('Fish', 'Proteins', 21.0, 0.0, 5.0),
            ('Beef', 'Proteins', 26.0, 0.0, 15.0),
            ('Liver', 'Proteins', 20.0, 4.0, 5.0),
            ('Tuna', 'Proteins', 22.0, 0.0, 1.0),
            ('Sardines', 'Proteins', 23.0, 0.0, 10.0),
            ('Beans', 'Proteins', 8.0, 20.0, 0.5),
            ('Cottage Cheese', 'Proteins', 15.0, 3.0, 4.0),
            ('Tofu', 'Proteins', 15.0, 2.0, 8.0),
            ('Buckwheat', 'Garnish', 3.0, 20.0, 1.0),
            ('Quinoa', 'Garnish', 4.0, 21.0, 2.0),
            ('Rice', 'Garnish', 2.5, 28.0, 0.3),
            ('Potato', 'Garnish', 2.0, 17.0, 0.1),
            ('Pasta', 'Garnish', 5.0, 30.0, 1.0),
            ('Almonds', 'Snack', 21.0, 22.0, 50.0),
            ('Cashews', 'Snack', 18.0, 30.0, 44.0),
            ('Walnuts', 'Snack', 15.0, 14.0, 65.0),
            ('Gouda cheese', 'Proteins', 25.0, 2.2, 27.0),
            ('Majadra', 'Garnish', 5.0, 23.0, 3.0),
            ('Protein Yogurt', 'Proteins', 10.0, 4.0, 0.0),
            ('Soft white cheese', 'Proteins', 11.0, 3.5, 5.0),
            ('bread', 'Garnish', 9.0, 49.0, 3.2),
            ('baguete', 'Garnish', 9.2, 52.0, 1.5),
            ('rie bread', 'Garnish', 8.5, 48.0, 1.5),
            ('Pita', 'Garnish', 9.0, 55.0, 1.2),
            ('Eggs L size', 'Proteins', 13.0, 1.1, 11.0),
            ('Eggs M size', 'Proteins', 13.0, 1.1, 11.0)
        ]
        execute_many(cursor, "INSERT INTO foods (name, category, protein_density, carbs_density, fat_density) VALUES (?, ?, ?, ?, ?)", default_foods)
        conn.commit()

    # Seed default meal plan if empty for Roman
    execute_query(cursor, "SELECT COUNT(*) FROM meal_plan WHERE user_id = ?", (roman_id,))
    if cursor.fetchone()[0] == 0:
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        default_plans = []
        for day in days_of_week:
            default_plans.append((roman_id, day, "Завтрак", "Cottage Cheese", "None"))
            default_plans.append((roman_id, day, "Снэк 1", "Almonds", None))
            default_plans.append((roman_id, day, "Обед", "Chicken", "Buckwheat"))
            default_plans.append((roman_id, day, "Снэк 2", "Cashews", None))
            default_plans.append((roman_id, day, "Ужин", "Turkey", "Rice"))
        execute_many(cursor, "INSERT INTO meal_plan (user_id, day, meal_type, food_name, garnish_name) VALUES (?, ?, ?, ?, ?)", default_plans)
        conn.commit()

    # Seed default settings if empty for Roman
    execute_query(cursor, "SELECT COUNT(*) FROM settings WHERE user_id = ?", (roman_id,))
    if cursor.fetchone()[0] == 0:
        default_settings = [
            (roman_id, 'protein_portion', 150.0),
            (roman_id, 'garnish_portion', 80.0),
            (roman_id, 'snack_portion', 30.0),
            (roman_id, 'target_protein', 130.0),
            (roman_id, 'target_carbs', 150.0),
            (roman_id, 'target_fat', 60.0)
        ]
        execute_many(cursor, "INSERT INTO settings (user_id, setting_key, value) VALUES (?, ?, ?)", default_settings)
        conn.commit()

    conn.close()

# --- User Operations ---

def hash_password(password):
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(email, password):
    """Create a new user with a hashed password."""
    conn = get_connection()
    cursor = conn.cursor()
    success = False
    try:
        h = hash_password(password)
        execute_query(cursor, "INSERT INTO users (email, password) VALUES (?, ?)", (email.lower().strip(), h))
        conn.commit()
        success = True
    except Exception:
        pass
    finally:
        conn.close()
    return success

def verify_user(email, password):
    """Verify user credentials. Returns (user_id, email) if valid, else None."""
    conn = get_connection()
    cursor = conn.cursor()
    h = hash_password(password)
    execute_query(cursor, "SELECT id, email FROM users WHERE email = ? AND password = ?", (email.lower().strip(), h))
    row = cursor.fetchone()
    conn.close()
    return (row[0], row[1]) if row else None

def change_user_password(user_id, new_password):
    """Update password for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    h = hash_password(new_password)
    execute_query(cursor, "UPDATE users SET password = ? WHERE id = ?", (h, user_id))
    conn.commit()
    conn.close()
    return True

# --- Foods Database Operations ---

def get_foods_by_category(category):
    """Retrieve list of names for all foods in a given category."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "SELECT name FROM foods WHERE category = ?", (category,))
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def get_all_food_macros():
    """Retrieve macronutrient densities for all foods."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "SELECT name, protein_density, carbs_density, fat_density FROM foods")
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: {'protein': row[1], 'carbs': row[2], 'fat': row[3]} for row in rows}

def add_food_to_db(name, category, protein_density, carbs_density=0.0, fat_density=0.0):
    """Insert a new food item with macronutrients into the database."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        execute_query(
            cursor,
            "INSERT INTO foods (name, category, protein_density, carbs_density, fat_density) VALUES (?, ?, ?, ?, ?)",
            (name, category, protein_density, carbs_density, fat_density)
        )
        conn.commit()
        success = True
    except Exception as e:
        if "unique" in str(e).lower() or "integrity" in str(e).lower():
            success = False
        else:
            raise e
    finally:
        conn.close()
    return success

# --- Meal Plan Operations ---

def get_meal_plan_from_db(user_id):
    """Retrieve the weekly meal plan structure from the database for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "SELECT day, meal_type, food_name, garnish_name FROM meal_plan WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()

    # Prepopulate standard empty structures
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    meal_plan = {}
    for day in days_of_week:
        meal_plan[day] = {
            "Завтрак": {"protein": "None", "garnish": "None"},
            "Снэк 1": {"snack": "None"},
            "Обед": {"protein": "None", "garnish": "None"},
            "Снэк 2": {"snack": "None"},
            "Ужин": {"protein": "None", "garnish": "None"}
        }

    for day, meal_type, food, garnish in rows:
        if day not in meal_plan:
            meal_plan[day] = {}
        if meal_type in ["Снэк 1", "Снэк 2"]:
            meal_plan[day][meal_type] = {"snack": food if food else "None"}
        else:
            meal_plan[day][meal_type] = {
                "protein": food if food else "None",
                "garnish": garnish if garnish else "None"
            }
    return meal_plan

def update_meal_plan_in_db(user_id, day, meal_type, food_name, garnish_name=None):
    """Update a specific meal plan slot in the database for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if is_postgres():
        execute_query(
            cursor,
            """
            INSERT INTO meal_plan (user_id, day, meal_type, food_name, garnish_name)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT (user_id, day, meal_type) DO UPDATE SET
                food_name = EXCLUDED.food_name,
                garnish_name = EXCLUDED.garnish_name
            """,
            (user_id, day, meal_type, food_name, garnish_name)
        )
    else:
        execute_query(
            cursor,
            """
            INSERT INTO meal_plan (user_id, day, meal_type, food_name, garnish_name)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT (user_id, day, meal_type) DO UPDATE SET
                food_name = excluded.food_name,
                garnish_name = excluded.garnish_name
            """,
            (user_id, day, meal_type, food_name, garnish_name)
        )
    conn.commit()
    conn.close()

# --- Checked Groceries Operations ---

def get_checked_groceries_from_db(user_id):
    """Retrieve all checked shopping list items from the database for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "SELECT item_key FROM checked_groceries WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return {row[0] for row in rows}

def set_grocery_checked_state(user_id, item_key, is_checked):
    """Set the checked state of a shopping list item for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    if is_checked:
        if is_postgres():
            execute_query(cursor, "INSERT INTO checked_groceries (user_id, item_key) VALUES (?, ?) ON CONFLICT (user_id, item_key) DO NOTHING", (user_id, item_key))
        else:
            execute_query(cursor, "INSERT OR IGNORE INTO checked_groceries (user_id, item_key) VALUES (?, ?)", (user_id, item_key))
    else:
        execute_query(cursor, "DELETE FROM checked_groceries WHERE user_id = ? AND item_key = ?", (user_id, item_key))
    conn.commit()
    conn.close()

# --- Settings Operations ---

def get_setting_value(user_id, key, default):
    """Retrieve a configuration setting value for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "SELECT value FROM settings WHERE user_id = ? AND setting_key = ?", (user_id, key))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else default

def update_setting_value(user_id, key, value):
    """Update or insert a configuration setting value for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    if is_postgres():
        execute_query(
            cursor,
            """
            INSERT INTO settings (user_id, setting_key, value)
            VALUES (?, ?, ?)
            ON CONFLICT (user_id, setting_key) DO UPDATE SET value = EXCLUDED.value
            """,
            (user_id, key, value)
        )
    else:
        execute_query(
            cursor,
            """
            INSERT INTO settings (user_id, setting_key, value)
            VALUES (?, ?, ?)
            ON CONFLICT (user_id, setting_key) DO UPDATE SET value = excluded.value
            """,
            (user_id, key, value)
        )
    conn.commit()
    conn.close()

# --- Weight Tracker Operations ---

def get_weight_history(user_id):
    """Retrieve all weight entries ordered by date for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "SELECT date, weight FROM weight_history WHERE user_id = ? ORDER BY date ASC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_weight_entry(user_id, date_str, weight):
    """Insert or update a weight entry for a specific date for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    if is_postgres():
        execute_query(
            cursor,
            """
            INSERT INTO weight_history (user_id, date, weight) VALUES (?, ?, ?)
            ON CONFLICT (user_id, date) DO UPDATE SET weight = EXCLUDED.weight
            """,
            (user_id, date_str, weight)
        )
    else:
        execute_query(
            cursor,
            """
            INSERT INTO weight_history (user_id, date, weight) VALUES (?, ?, ?)
            ON CONFLICT (user_id, date) DO UPDATE SET weight = excluded.weight
            """,
            (user_id, date_str, weight)
        )
    conn.commit()
    conn.close()

def delete_weight_entry(user_id, date_str):
    """Delete a weight entry for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "DELETE FROM weight_history WHERE user_id = ? AND date = ?", (user_id, date_str))
    conn.commit()
    conn.close()

# --- GLP-1 Injection Log Operations ---

def get_injection_history(user_id):
    """Retrieve all injection logs ordered by date for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "SELECT id, date, medication, dose FROM injection_history WHERE user_id = ? ORDER BY date DESC, id DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_injection_entry(user_id, date_str, medication, dose):
    """Record an injection log for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(
        cursor,
        "INSERT INTO injection_history (user_id, date, medication, dose) VALUES (?, ?, ?, ?)",
        (user_id, date_str, medication, dose)
    )
    conn.commit()
    conn.close()

def delete_injection_entry(user_id, entry_id):
    """Delete an injection log for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "DELETE FROM injection_history WHERE user_id = ? AND id = ?", (user_id, entry_id))
    conn.commit()
    conn.close()

# --- Food Log Operations ---

def get_food_log(user_id, date_str):
    """Retrieve logged foods for a specific date and user."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "SELECT id, date, meal_type, food_name, garnish_name, food_portion, garnish_portion FROM food_log WHERE user_id = ? AND date = ? ORDER BY id ASC", (user_id, date_str))
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            'id': row[0],
            'date': row[1],
            'meal_type': row[2],
            'food_name': row[3],
            'garnish_name': row[4],
            'food_portion': row[5],
            'garnish_portion': row[6]
        }
        for row in rows
    ]

def add_food_log_entry(user_id, date_str, meal_type, food_name, garnish_name, food_portion, garnish_portion):
    """Record a logged food entry for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(
        cursor,
        "INSERT INTO food_log (user_id, date, meal_type, food_name, garnish_name, food_portion, garnish_portion) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, date_str, meal_type, food_name, garnish_name, food_portion, garnish_portion)
    )
    conn.commit()
    conn.close()

def delete_food_log_entry(user_id, entry_id):
    """Delete a food log entry for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "DELETE FROM food_log WHERE user_id = ? AND id = ?", (user_id, entry_id))
    conn.commit()
    conn.close()

def get_actual_intake_in_range(user_id, start_date_str, end_date_str):
    """Retrieve all logged food entries in a date range (inclusive) for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(
        cursor,
        "SELECT id, date, meal_type, food_name, garnish_name, food_portion, garnish_portion FROM food_log WHERE user_id = ? AND date >= ? AND date <= ? ORDER BY date ASC, id ASC",
        (user_id, start_date_str, end_date_str)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            'id': row[0],
            'date': row[1],
            'meal_type': row[2],
            'food_name': row[3],
            'garnish_name': row[4],
            'food_portion': row[5],
            'garnish_portion': row[6]
        }
        for row in rows
    ]

# --- Profile Operations ---

def get_profile_value(user_id, key, default=""):
    """Retrieve a profile value for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "SELECT value FROM profile WHERE user_id = ? AND key = ?", (user_id, key))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else default

def update_profile_value(user_id, key, value):
    """Update or insert a profile value for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    if is_postgres():
        execute_query(
            cursor,
            """
            INSERT INTO profile (user_id, key, value)
            VALUES (?, ?, ?)
            ON CONFLICT (user_id, key) DO UPDATE SET value = EXCLUDED.value
            """,
            (user_id, key, value)
        )
    else:
        execute_query(
            cursor,
            """
            INSERT INTO profile (user_id, key, value)
            VALUES (?, ?, ?)
            ON CONFLICT (user_id, key) DO UPDATE SET value = excluded.value
            """,
            (user_id, key, value)
        )
    conn.commit()
    conn.close()
