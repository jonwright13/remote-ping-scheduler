import psycopg2
import os, json
from datetime import datetime, timezone
from urllib.parse import urlparse, urlunparse


def sanitize_db_url(url):
    parsed = urlparse(url)
    netloc = parsed.hostname
    if parsed.port:
        netloc += f":{parsed.port}"
    if parsed.username:
        netloc = f"{parsed.username}@{netloc}"

    return urlunparse((parsed.scheme, netloc, parsed.path, "", "", ""))


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
with open(log_file, "w", encoding="utf-8") as f:
    f.write(f"Database Status Check - {timestamp}\n")
    f.write("=" * 40 + "\n")
    for url in db_urls:
        sanitized_url = sanitize_db_url(url)
        try:
            conn = psycopg2.connect(url)
            cur = conn.cursor()
            # 🔍 Get first non-system table name
            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name ASC
                LIMIT 1
            """
            )
            result = cur.fetchone()
            if not result:
                raise Exception("No user tables found in 'public' schema")

            table = result[0]
            cur.execute(f'SELECT * FROM "{table}" LIMIT 1;')  # 🔄 Real table query
            row = cur.fetchone()

            cur.close()
            conn.close()
            line = f"SUCCESS: {sanitized_url} | Queried Table: {table}"
        except Exception as e:
            success = False
            line = f"FAIL: {sanitized_url} — {e}"
        print(line)
        f.write(line + "\n")

exit(0 if success else 1)
