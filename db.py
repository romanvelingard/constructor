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

    # 1. Create foods table with carbs & fat columns
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS foods (
            name TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            protein_density REAL NOT NULL,
            carbs_density REAL NOT NULL DEFAULT 0.0,
            fat_density REAL NOT NULL DEFAULT 0.0
        )
    """)

    # 2. Run Migration: Check if carbs_density exists in existing foods table (for backward compatibility)
    try:
        execute_query(cursor, "SELECT carbs_density FROM foods LIMIT 1")
    except Exception:
        # Transaction must be rolled back on Postgres if a select query fails
        conn.rollback()
        cursor = conn.cursor()
        try:
            execute_query(cursor, "ALTER TABLE foods ADD COLUMN carbs_density REAL NOT NULL DEFAULT 0.0")
            execute_query(cursor, "ALTER TABLE foods ADD COLUMN fat_density REAL NOT NULL DEFAULT 0.0")
            conn.commit()
            
            # Populate existing seeded items with realistic macronutrients
            default_macros = {
                'Turkey': (25.0, 0.0, 1.0),
                'Chicken': (24.0, 0.0, 3.0),
                'Fish': (21.0, 0.0, 5.0),
                'Beef': (26.0, 0.0, 15.0),
                'Liver': (20.0, 4.0, 5.0),
                'Tuna': (22.0, 0.0, 1.0),
                'Sardines': (23.0, 0.0, 10.0),
                'Beans': (8.0, 20.0, 0.5),
                'Cottage Cheese': (15.0, 3.0, 4.0),
                'Tofu': (15.0, 2.0, 8.0),
                'Buckwheat': (3.0, 20.0, 1.0),
                'Quinoa': (4.0, 21.0, 2.0),
                'Rice': (2.5, 28.0, 0.3),
                'Potato': (2.0, 17.0, 0.1),
                'Pasta': (5.0, 30.0, 1.0),
                'Almonds': (21.0, 22.0, 50.0),
                'Cashews': (18.0, 30.0, 44.0),
                'Walnuts': (15.0, 14.0, 65.0)
            }
            for name, (p, c, f) in default_macros.items():
                execute_query(cursor, "UPDATE foods SET protein_density = ?, carbs_density = ?, fat_density = ? WHERE name = ?", (p, c, f, name))
            conn.commit()
        except Exception:
            pass

    # 3. Create meal_plan table
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS meal_plan (
            day TEXT NOT NULL,
            meal_type TEXT NOT NULL,
            food_name TEXT,
            garnish_name TEXT,
            PRIMARY KEY (day, meal_type)
        )
    """)

    # Migration: Update 'Снэк' to 'Снэк 1' and seed 'Снэк 2' if they exist
    try:
        execute_query(cursor, "SELECT COUNT(*) FROM meal_plan WHERE meal_type = 'Снэк'")
        if cursor.fetchone()[0] > 0:
            execute_query(cursor, "UPDATE meal_plan SET meal_type = 'Снэк 1' WHERE meal_type = 'Снэк'")
            days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            for day in days_of_week:
                if is_postgres():
                    execute_query(cursor, "INSERT INTO meal_plan (day, meal_type, food_name, garnish_name) VALUES (?, 'Снэк 2', 'None', NULL) ON CONFLICT (day, meal_type) DO NOTHING", (day,))
                else:
                    execute_query(cursor, "INSERT OR IGNORE INTO meal_plan (day, meal_type, food_name, garnish_name) VALUES (?, 'Снэк 2', 'None', NULL)", (day,))
            conn.commit()
    except Exception:
        pass

    # 4. Create checked_groceries table
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS checked_groceries (
            item_key TEXT PRIMARY KEY
        )
    """)

    # 5. Create settings table
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS settings (
            setting_key TEXT PRIMARY KEY,
            value REAL NOT NULL
        )
    """)

    # 6. Create weight_history table
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS weight_history (
            date TEXT PRIMARY KEY,
            weight REAL NOT NULL
        )
    """)

    # 7. Create injection_history table
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS injection_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            medication TEXT NOT NULL,
            dose REAL NOT NULL
        )
    """)

    # 8. Create food_log table
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS food_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            meal_type TEXT NOT NULL,
            food_name TEXT NOT NULL,
            garnish_name TEXT,
            food_portion REAL NOT NULL,
            garnish_portion REAL NOT NULL
        )
    """)

    # 9. Create profile table
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS profile (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    conn.commit()

    # Seed default foods if empty
    execute_query(cursor, "SELECT COUNT(*) FROM foods")
    if cursor.fetchone()[0] == 0:
        default_foods = [
            # Proteins (name, category, protein, carbs, fat)
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
            # Garnishes
            ('Buckwheat', 'Garnish', 3.0, 20.0, 1.0),
            ('Quinoa', 'Garnish', 4.0, 21.0, 2.0),
            ('Rice', 'Garnish', 2.5, 28.0, 0.3),
            ('Potato', 'Garnish', 2.0, 17.0, 0.1),
            ('Pasta', 'Garnish', 5.0, 30.0, 1.0),
            # Snacks
            ('Almonds', 'Snack', 21.0, 22.0, 50.0),
            ('Cashews', 'Snack', 18.0, 30.0, 44.0),
            ('Walnuts', 'Snack', 15.0, 14.0, 65.0),
            # New GLP-1 and dietary additions
            ('Gouda cheese', 'Proteins', 25.0, 2.2, 27.0),
            ('Majadra', 'Garnish', 5.0, 23.0, 3.0),
            ('Protein Yogurt', 'Proteins', 10.0, 4.0, 0.0),
            ('Soft white cheese', 'Proteins', 11.0, 3.5, 5.0),
            # Bread additions (Garnish category)
            ('bread', 'Garnish', 9.0, 49.0, 3.2),
            ('baguete', 'Garnish', 9.2, 52.0, 1.5),
            ('rie bread', 'Garnish', 8.5, 48.0, 1.5),
            ('Pita', 'Garnish', 9.0, 55.0, 1.2),
            ('Eggs L size', 'Proteins', 13.0, 1.1, 11.0),
            ('Eggs M size', 'Proteins', 13.0, 1.1, 11.0)
        ]
        execute_many(cursor, "INSERT INTO foods (name, category, protein_density, carbs_density, fat_density) VALUES (?, ?, ?, ?, ?)", default_foods)
        conn.commit()

    # Migration check to ensure Eggs L size and Eggs M size are present in existing DB
    for egg_name in ['Eggs L size', 'Eggs M size']:
        execute_query(cursor, "SELECT COUNT(*) FROM foods WHERE name = ?", (egg_name,))
        if cursor.fetchone()[0] == 0:
            execute_query(
                cursor,
                "INSERT INTO foods (name, category, protein_density, carbs_density, fat_density) VALUES (?, 'Proteins', 13.0, 1.1, 11.0)",
                (egg_name,)
            )
            conn.commit()


    # Seed default meal plan if empty
    execute_query(cursor, "SELECT COUNT(*) FROM meal_plan")
    if cursor.fetchone()[0] == 0:
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        default_plans = []
        for day in days_of_week:
            # Завтрак
            default_plans.append((day, "Завтрак", "Cottage Cheese", "None"))
            # Снэк 1
            default_plans.append((day, "Снэк 1", "Almonds", None))
            # Обед
            default_plans.append((day, "Обед", "Chicken", "Buckwheat"))
            # Снэк 2
            default_plans.append((day, "Снэк 2", "Cashews", None))
            # Ужин
            default_plans.append((day, "Ужин", "Turkey", "Rice"))
        
        execute_many(cursor, "INSERT INTO meal_plan (day, meal_type, food_name, garnish_name) VALUES (?, ?, ?, ?)", default_plans)
        conn.commit()

    # Seed default settings if empty
    execute_query(cursor, "SELECT COUNT(*) FROM settings")
    if cursor.fetchone()[0] == 0:
        default_settings = [
            ('protein_portion', 150.0),
            ('garnish_portion', 80.0),
            ('snack_portion', 30.0),
            ('target_protein', 130.0),
            ('target_carbs', 150.0),
            ('target_fat', 60.0)
        ]
        execute_many(cursor, "INSERT INTO settings (setting_key, value) VALUES (?, ?)", default_settings)
        conn.commit()
    else:
        # Seed missing target settings if settings exist but missed carbs/fat
        for key, val in [('target_carbs', 150.0), ('target_fat', 60.0)]:
            execute_query(cursor, "SELECT COUNT(*) FROM settings WHERE setting_key = ?", (key,))
            if cursor.fetchone()[0] == 0:
                execute_query(cursor, "INSERT INTO settings (setting_key, value) VALUES (?, ?)", (key, val))
                conn.commit()

    conn.close()

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

def get_meal_plan_from_db():
    """Retrieve the weekly meal plan structure from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "SELECT day, meal_type, food_name, garnish_name FROM meal_plan")
    rows = cursor.fetchall()
    conn.close()

    meal_plan = {}
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

def update_meal_plan_in_db(day, meal_type, food_name, garnish_name=None):
    """Update a specific meal plan slot in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if is_postgres():
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

# --- Weight Tracker Operations ---

def get_weight_history():
    """Retrieve all weight entries ordered by date."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "SELECT date, weight FROM weight_history ORDER BY date ASC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_weight_entry(date_str, weight):
    """Insert or update a weight entry for a specific date."""
    conn = get_connection()
    cursor = conn.cursor()
    if is_postgres():
        execute_query(
            cursor,
            """
            INSERT INTO weight_history (date, weight) VALUES (?, ?)
            ON CONFLICT (date) DO UPDATE SET weight = EXCLUDED.weight
            """,
            (date_str, weight)
        )
    else:
        execute_query(
            cursor,
            """
            INSERT INTO weight_history (date, weight) VALUES (?, ?)
            ON CONFLICT (date) DO UPDATE SET weight = excluded.weight
            """,
            (date_str, weight)
        )
    conn.commit()
    conn.close()

def delete_weight_entry(date_str):
    """Delete a weight entry."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "DELETE FROM weight_history WHERE date = ?", (date_str,))
    conn.commit()
    conn.close()

# --- GLP-1 Injection Log Operations ---

def get_injection_history():
    """Retrieve all injection logs ordered by date."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "SELECT id, date, medication, dose FROM injection_history ORDER BY date DESC, id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_injection_entry(date_str, medication, dose):
    """Record an injection log."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(
        cursor,
        "INSERT INTO injection_history (date, medication, dose) VALUES (?, ?, ?)",
        (date_str, medication, dose)
    )
    conn.commit()
    conn.close()

def delete_injection_entry(entry_id):
    """Delete an injection log."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "DELETE FROM injection_history WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()

# --- Food Log Operations ---

def get_food_log(date_str):
    """Retrieve logged foods for a specific date."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "SELECT id, date, meal_type, food_name, garnish_name, food_portion, garnish_portion FROM food_log WHERE date = ? ORDER BY id ASC", (date_str,))
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

def add_food_log_entry(date_str, meal_type, food_name, garnish_name, food_portion, garnish_portion):
    """Record a logged food entry."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(
        cursor,
        "INSERT INTO food_log (date, meal_type, food_name, garnish_name, food_portion, garnish_portion) VALUES (?, ?, ?, ?, ?, ?)",
        (date_str, meal_type, food_name, garnish_name, food_portion, garnish_portion)
    )
    conn.commit()
    conn.close()

def delete_food_log_entry(entry_id):
    """Delete a food log entry."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "DELETE FROM food_log WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()

def get_actual_intake_in_range(start_date_str, end_date_str):
    """Retrieve all logged food entries in a date range (inclusive)."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(
        cursor,
        "SELECT id, date, meal_type, food_name, garnish_name, food_portion, garnish_portion FROM food_log WHERE date >= ? AND date <= ? ORDER BY date ASC, id ASC",
        (start_date_str, end_date_str)
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

def get_profile_value(key, default=""):
    """Retrieve a profile value."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "SELECT value FROM profile WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else default

def update_profile_value(key, value):
    """Update or insert a profile value."""
    conn = get_connection()
    cursor = conn.cursor()
    if is_postgres():
        execute_query(
            cursor,
            """
            INSERT INTO profile (key, value)
            VALUES (?, ?)
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
            """,
            (key, value)
        )
    else:
        execute_query(
            cursor,
            """
            INSERT INTO profile (key, value)
            VALUES (?, ?)
            ON CONFLICT (key) DO UPDATE SET value = excluded.value
            """,
            (key, value)
        )
    conn.commit()
    conn.close()


