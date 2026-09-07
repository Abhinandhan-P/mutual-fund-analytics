from pathlib import Path
import sqlite3

# Project paths
BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "data" / "db"
SQL_DIR = BASE_DIR / "sql"

# Create database folder if it doesn't exist
DB_DIR.mkdir(parents=True, exist_ok=True)

# Database path
DB_PATH = DB_DIR / "bluestock_mf.db"

# Schema file
SCHEMA_PATH = SQL_DIR / "schema.sql"

# Connect to SQLite
connection = sqlite3.connect(DB_PATH)

# Read schema.sql
with open(SCHEMA_PATH, "r", encoding="utf-8") as file:
    schema_sql = file.read()

# Execute schema
connection.executescript(schema_sql)

# Save changes
connection.commit()

connection.close()

print(f"Database created successfully:")
print(DB_PATH)