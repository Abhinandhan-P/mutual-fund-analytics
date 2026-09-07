from pathlib import Path
import sqlite3


# ============================================================
# Project paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "db" / "bluestock_mf.db"
SQL_PATH = BASE_DIR / "sql" / "queries.sql"


# ============================================================
# Read SQL file
# ============================================================

with open(SQL_PATH, "r", encoding="utf-8") as file:
    sql_text = file.read()


# ============================================================
# ============================================================
# Split queries using "-- Query" markers
# ============================================================

queries = []

current_query = []
inside_query = False

for line in sql_text.splitlines():

    if line.strip().startswith("-- Query"):

        if current_query:
            queries.append("\n".join(current_query))

        current_query = []
        inside_query = True

    elif inside_query:

        current_query.append(line)


if current_query:
    queries.append("\n".join(current_query))
# ============================================================
# Run queries
# ============================================================

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

print("=" * 60)
print("Running 10 analytical SQL queries")
print("=" * 60)

for number, query in enumerate(queries, start=1):

    query = query.strip()

    if not query:
        continue

    try:

        cursor.execute(query)

        rows = cursor.fetchall()

        print(f"\nQuery {number}: PASS")
        print(f"Rows returned: {len(rows)}")

        # Show first 3 rows as a quick verification
        for row in rows[:3]:
            print(row)

    except Exception as error:

        print(f"\nQuery {number}: FAIL")
        print(f"Error: {error}")


connection.close()

print("\n" + "=" * 60)
print("SQL query validation completed.")
print("=" * 60)