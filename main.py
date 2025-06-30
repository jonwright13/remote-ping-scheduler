import psycopg2
import os, json


# Get the string value from env
db_urls_raw = os.environ.get("DATABASE_URLS", "[]")

# Convert the json list to a list
try:
    db_urls = json.loads(db_urls_raw)
    print("Parsed DB URLs:", len(db_urls))
except json.JSONDecodeError:
    print("Invalid JSON in DATABASE_URLS")
    db_urls = []


for url in db_urls:

    try:
        conn = psycopg2.connect(url)
        conn.close()
        print("✅ Database is reachable.")
    except Exception as e:
        print(f"❌ Failed to connect to the database: {e}")
