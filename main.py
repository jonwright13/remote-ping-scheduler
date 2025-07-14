from src.db_check import check_all_dbs


def main(event=None, context=None):
    log_file, success = check_all_dbs()
    # Optional: send log to Cloud Storage or email here
    print(f"Check finished. Log at {log_file}")
    if not success:
        raise RuntimeError("One or more DB checks failed.")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        print(str(e))
        exit(1)
