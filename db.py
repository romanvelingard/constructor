import sqlite3
import os

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
        # Some platforms specify postgres:// which psycopg2 sometimes requires to be postgresql://
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(url)
    else:
        return sqlite3.connect(DB_FILE)

def execute_query(cursor, sql, params=()):
    """Execute SQL query replacing SQLite placeholders with PostgreSQL ones if needed."""
    if is_postgres():
        sql = sql.replace('?', '%s')
    cursor.execute(sql, params)
    return cursor

def execute_many(cursor, sql, params_list):
    """Execute batch SQL query replacing SQLite placeholders with PostgreSQL ones if needed."""
    if is_postgres():
        sql = sql.replace('?', '%s')
    cursor.executemany(sql, params_list)
    return cursor

def init_db():
    """Initialize database tables and seed default values if empty."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Create foods table
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS foods (
            name TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            protein_density REAL NOT NULL
        )
    """)

    # 2. Create meal_plan table
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS meal_plan (
            day TEXT NOT NULL,
            meal_type TEXT NOT NULL,
            food_name TEXT,
            garnish_name TEXT,
            PRIMARY KEY (day, meal_type)
        )
    """)

    # 3. Create checked_groceries table
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS checked_groceries (
            item_key TEXT PRIMARY KEY
        )
    """)

    # 4. Create settings table (use setting_key instead of key to avoid PG reserved keyword issues)
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS settings (
            setting_key TEXT PRIMARY KEY,
            value REAL NOT NULL
        )
    """)

    conn.commit()

    # Seed default foods if empty
    execute_query(cursor, "SELECT COUNT(*) FROM foods")
    if cursor.fetchone()[0] == 0:
        default_foods = [
            # Proteins
            ('Turkey', 'Proteins', 25.0),
            ('Chicken', 'Proteins', 24.0),
            ('Fish', 'Proteins', 21.0),
            ('Beef', 'Proteins', 26.0),
            ('Liver', 'Proteins', 20.0),
            ('Tuna', 'Proteins', 22.0),
            ('Sardines', 'Proteins', 23.0),
            ('Beans', 'Proteins', 8.0),
            ('Cottage Cheese', 'Proteins', 15.0),
            ('Tofu', 'Proteins', 15.0),
            # Garnishes
            ('Buckwheat', 'Garnish', 0.0),
            ('Quinoa', 'Garnish', 0.0),
            ('Rice', 'Garnish', 0.0),
            ('Potato', 'Garnish', 0.0),
            ('Pasta', 'Garnish', 0.0),
            # Snacks
            ('Almonds', 'Snack', 21.0),
            ('Cashews', 'Snack', 18.0),
            ('Walnuts', 'Snack', 15.0)
        ]
        execute_many(cursor, "INSERT INTO foods (name, category, protein_density) VALUES (?, ?, ?)", default_foods)
        conn.commit()

    # Seed default meal plan if empty
    execute_query(cursor, "SELECT COUNT(*) FROM meal_plan")
    if cursor.fetchone()[0] == 0:
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        default_plans = []
        for day in days_of_week:
            # Завтрак
            default_plans.append((day, "Завтрак", "Cottage Cheese", "None"))
            # Обед
            default_plans.append((day, "Обед", "Chicken", "Buckwheat"))
            # Ужин
            default_plans.append((day, "Ужин", "Turkey", "Rice"))
            # Снэк
            default_plans.append((day, "Снэк", "Almonds", None))
        
        execute_many(cursor, "INSERT INTO meal_plan (day, meal_type, food_name, garnish_name) VALUES (?, ?, ?, ?)", default_plans)
        conn.commit()

    # Seed default settings if empty
    execute_query(cursor, "SELECT COUNT(*) FROM settings")
    if cursor.fetchone()[0] == 0:
        default_settings = [
            ('protein_portion', 150.0),
            ('garnish_portion', 80.0),
            ('snack_portion', 30.0),
            ('target_protein', 130.0)
        ]
        execute_many(cursor, "INSERT INTO settings (setting_key, value) VALUES (?, ?)", default_settings)
        conn.commit()

    conn.close()

# --- Foods Database Operations ---

def get_foods_by_category(category):
    """Retrieve all foods in a given category."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "SELECT name, protein_density FROM foods WHERE category = ?", (category,))
    rows = cursor.fetchall()
    conn.close()
    
    if category == 'Garnish':
        # Garnish is stored as a list in original session_state
        return [row[0] for row in rows]
    else:
        # Proteins and Snacks are stored as dictionary mapping food -> density
        return {row[0]: row[1] for row in rows}

def add_food_to_db(name, category, protein_density):
    """Insert a new food item into the database."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        execute_query(
            cursor,
            "INSERT INTO foods (name, category, protein_density) VALUES (?, ?, ?)",
            (name, category, protein_density)
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

def get_meal_plan_from_db():
    """Retrieve the weekly meal plan structure from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "SELECT day, meal_type, food_name, garnish_name FROM meal_plan")
    rows = cursor.fetchall()
    conn.close()

    # Build the original session state structure
    meal_plan = {}
    for day, meal_type, food, garnish in rows:
        if day not in meal_plan:
            meal_plan[day] = {}
        if meal_type == "Снэк":
            meal_plan[day][meal_type] = {"snack": food if food else "None"}
        else:
            meal_plan[day][meal_type] = {
                "protein": food if food else "None",
                "garnish": garnish if garnish else "None"
            }
    return meal_plan

def update_meal_plan_in_db(day, meal_type, food_name, garnish_name=None):
    """Update a specific meal plan slot in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if is_postgres():
        # Postgres ON CONFLICT syntax
        execute_query(
            cursor,
            """
            INSERT INTO meal_plan (day, meal_type, food_name, garnish_name)
            VALUES (?, ?, ?, ?)
            ON CONFLICT (day, meal_type) DO UPDATE SET
                food_name = EXCLUDED.food_name,
                garnish_name = EXCLUDED.garnish_name
            """,
            (day, meal_type, food_name, garnish_name)
        )
    else:
        # SQLite ON CONFLICT syntax
        execute_query(
            cursor,
            """
            INSERT INTO meal_plan (day, meal_type, food_name, garnish_name)
            VALUES (?, ?, ?, ?)
            ON CONFLICT (day, meal_type) DO UPDATE SET
                food_name = excluded.food_name,
                garnish_name = excluded.garnish_name
            """,
            (day, meal_type, food_name, garnish_name)
        )
    conn.commit()
    conn.close()

# --- Checked Groceries Operations ---

def get_checked_groceries_from_db():
    """Retrieve all checked shopping list items from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "SELECT item_key FROM checked_groceries")
    rows = cursor.fetchall()
    conn.close()
    return {row[0] for row in rows}

def set_grocery_checked_state(item_key, is_checked):
    """Set the checked state of a shopping list item."""
    conn = get_connection()
    cursor = conn.cursor()
    if is_checked:
        if is_postgres():
            execute_query(cursor, "INSERT INTO checked_groceries (item_key) VALUES (?) ON CONFLICT (item_key) DO NOTHING", (item_key,))
        else:
            execute_query(cursor, "INSERT OR IGNORE INTO checked_groceries (item_key) VALUES (?)", (item_key,))
    else:
        execute_query(cursor, "DELETE FROM checked_groceries WHERE item_key = ?", (item_key,))
    conn.commit()
    conn.close()

# --- Settings Operations ---

def get_setting_value(key, default):
    """Retrieve a configuration setting value."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "SELECT value FROM settings WHERE setting_key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else default

def update_setting_value(key, value):
    """Update or insert a configuration setting value."""
    conn = get_connection()
    cursor = conn.cursor()
    if is_postgres():
        execute_query(
            cursor,
            """
            INSERT INTO settings (setting_key, value)
            VALUES (?, ?)
            ON CONFLICT (setting_key) DO UPDATE SET value = EXCLUDED.value
            """,
            (key, value)
        )
    else:
        execute_query(
            cursor,
            """
            INSERT INTO settings (setting_key, value)
            VALUES (?, ?)
            ON CONFLICT (setting_key) DO UPDATE SET value = excluded.value
            """,
            (key, value)
        )
    conn.commit()
    conn.close()
