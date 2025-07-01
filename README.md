# 🛰️ Remote Ping Scheduler

A GitHub Actions–powered tool that automatically checks the availability of remote PostgreSQL databases once per day and logs the results.

---

## 🚀 Overview

This project uses a Python script and GitHub Actions to:

- Connect to one or more PostgreSQL database URLs
- Log success/failure for each connection attempt
- Upload a timestamped log file as an artifact
- Notify you by email (via GitHub notifications) if any database is unreachable

---

## 📦 Features

- ✅ Daily scheduled execution via GitHub Actions
- 📄 Timestamped logs for every run
- 📬 Email notifications on failure (via built-in GitHub notifications)
- 🔒 Secure handling of database credentials via GitHub Secrets

---

## ⚙️ Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/remote-ping-scheduler.git
cd remote-ping-scheduler
```

### 2. Add your database URLs

In your GitHub repo:

- Go to ```Settings``` → ```Secrets and variables``` → ```Actions``` → ```New repository secret```
- Add a secret:

```perl
Name: DATABASE_URLS
Value: ["postgresql://user:pass@host1/db", "postgresql://user:pass@host2/db"]
```

💡 The value must be a valid JSON array of strings.

### 3. (Optional) Customize schedule

By default, the action runs daily at 06:00 UTC. You can adjust the ```cron``` schedule in ```.github/workflows/db_status_check.yml```:

```yaml
schedule:
  - cron: '0 6 * * *'
```

---

## 🖥️ How It Works

- ```main.py``` reads the ```DATABASE_URLS``` environment variable
- It attempts to connect to each DB using ```psycopg2```
- It logs the result to a file named like ```db_status_<timestamp>.log```
- If any DB is unreachable, the job fails and GitHub sends you a failure email
- The log file is uploaded as an artifact for future reference

---

## 📄 Example Log

```sql
Database Status Check - 20250630_060001
========================================
✅ SUCCESS: postgresql://user@host1/db
❌ FAIL: postgresql://user@host2/db — could not connect: timeout
```
