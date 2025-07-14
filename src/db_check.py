import psycopg2
import os, json, tempfile
from datetime import datetime, timezone
from urllib.parse import urlparse, urlunparse

log_fname = "db_status_{}.log"


def decode_db_urls():
    # ✅ Gen2 (or fallback) — DATABASE_URLS is a JSON string
    json_string = os.environ.get("DATABASE_URLS")
    if json_string:
        try:
            print("✅ Loaded DATABASE_URLS from secret or env var.")
            return json.loads(json_string)
        except Exception as e:
            print("❌ Failed to parse DATABASE_URLS from env:", e)
            return []

    # ✅ Local: fallback to DATABASE_URLS_JSON
    json_string = os.environ.get("DATABASE_URLS_JSON")
    if json_string:
        try:
            print("✅ Loaded DATABASE_URLS from local env var.")
            return json.loads(json_string)
        except Exception as e:
            print("❌ Failed to parse DATABASE_URLS_JSON:", e)
            return []

    # ✅ Fallback: dbs.json
    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        dbs_file = os.path.join(project_root, "dbs.json")
        with open(dbs_file, "r", encoding="utf-8") as f:
            print("✅ Loaded DATABASE_URLS from dbs.json file.")
            return json.load(f)
    except Exception as e:
        print("❌ Failed to load DATABASE_URLS from dbs.json:", e)
        return []


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
    db_urls = decode_db_urls()
    timestamp = os.environ.get(
        "RUN_TIMESTAMP", datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    )
    log_file = get_log_path(timestamp)

    print("Parsed DB URLs:", len(db_urls))
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
