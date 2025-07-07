import psycopg2
import os, json
from datetime import datetime, timezone


# Load environment variables
db_urls_raw = os.environ.get("DATABASE_URLS", "[]")
timestamp = os.environ.get(
    "RUN_TIMESTAMP", datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
)
log_file = f"db_status_{timestamp}.log"

# Convert the json list to a list
try:
    db_urls = json.loads(db_urls_raw)
    print("Parsed DB URLs:", len(db_urls))
except json.JSONDecodeError:
    print("Invalid JSON in DATABASE_URLS")
    db_urls = []


success = True
with open(log_file, "w") as f:
    f.write(f"Database Status Check - {timestamp}\n")
    f.write("=" * 40 + "\n")
    for url in db_urls:
        try:
            conn = psycopg2.connect(url)
            cur = conn.cursor()
            cur.execute("SELECT 1;")  # 🟢 Ensure the DB is queried
            cur.fetchone()
            cur.close()
            conn.close()
            line = f"SUCCESS: {url}"
        except Exception as e:
            success = False
            line = f"FAIL: {url} — {e}"
        print(line)
        f.write(line + "\n")

exit(0 if success else 1)
