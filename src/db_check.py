import psycopg2
import os, json, tempfile
from datetime import datetime, timezone
from urllib.parse import urlparse, urlunparse

log_fname = "db_status_{}.log"


def get_log_path(timestamp):
    running_in_gcf = os.environ.get("K_SERVICE") is not None
    if running_in_gcf:
        return os.path.join(tempfile.gettempdir(), log_fname.format(timestamp))
    else:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        local_tmp_dir = os.path.join(project_root, "tmp")
        os.makedirs(local_tmp_dir, exist_ok=True)
        return os.path.join(local_tmp_dir, log_fname.format(timestamp))


def sanitize_db_url(url):
    parsed = urlparse(url)
    netloc = parsed.hostname
    if parsed.port:
        netloc += f":{parsed.port}"
    if parsed.username:
        netloc = f"{parsed.username}@{netloc}"

    return urlunparse((parsed.scheme, netloc, parsed.path, "", "", ""))


def check_db(url):
    sanitized_url = sanitize_db_url(url)
    try:
        conn = psycopg2.connect(url)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name ASC LIMIT 1
        """
        )
        result = cur.fetchone()
        if not result:
            raise Exception("No user tables found in 'public' schema")

        table = result[0]
        cur.execute(f'SELECT * FROM "{table}" LIMIT 1;')
        cur.fetchone()
        cur.close()
        conn.close()
        return f"SUCCESS: {sanitized_url} | Queried Table: {table}", True
    except Exception as e:
        return f"FAIL: {sanitized_url} — {e}", False


def check_all_dbs():
    db_urls_raw = os.environ.get("DATABASE_URLS", "[]")
    timestamp = os.environ.get(
        "RUN_TIMESTAMP", datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    )
    log_file = get_log_path(timestamp)

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
            line, result = check_db(url)
            if not result:
                success = False
            print(line)
            f.write(line + "\n")

    return log_file, success
