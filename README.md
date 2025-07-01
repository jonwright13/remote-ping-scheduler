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
