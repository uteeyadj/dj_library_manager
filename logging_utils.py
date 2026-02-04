# logging_utils.py
#
# Simple, professional logging system for the scanning engine.
# Creates logs/scan.log automatically and appends timestamped entries.

import os
from datetime import datetime


# ============================================================
# Log file setup
# ============================================================
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "scan.log")

# Ensure logs directory exists
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


# ============================================================
# Core logging function
# ============================================================
def log(message: str):
    """
    Writes a timestamped log entry to logs/scan.log.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"{timestamp}: {message}"

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")


# ============================================================
# Convenience helpers used by audio_reader.py
# ============================================================
def log_added(filepath: str):
    log(f"Added track: {filepath}")


def log_duplicate(filepath: str):
    log(f"Duplicate skipped: {filepath}")


def log_missing_bpm(filepath: str):
    log(f"Missing BPM: {filepath}")


def log_missing_key(filepath: str):
    log(f"Missing key: {filepath}")


def log_missing_genre(filepath: str):
    log(f"Missing genre: {filepath}")


def log_error(filepath: str, error: str):
    log(f"Error reading {filepath}: {error}")



