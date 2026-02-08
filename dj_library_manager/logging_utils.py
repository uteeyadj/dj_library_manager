# logging_utils.py
#
# Color-coded console output using Rich + traditional file logging.

import os
from datetime import datetime
from rich.console import Console
from rich.text import Text

# ============================================================
# Rich console setup
# ============================================================
console = Console()

def info(message: str):
    console.print(Text(message, style="bold cyan"))

def success(message: str):
    console.print(Text(message, style="bold green"))

def warning(message: str):
    console.print(Text(message, style="bold yellow"))

def error(message: str):
    console.print(Text(message, style="bold red"))

def mode(message: str, fast: bool = False):
    style = "bold bright_cyan" if fast else "bold magenta"
    console.print(Text(message, style=style))


# ============================================================
# Log file setup (unchanged)
# ============================================================
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "scan.log")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


# ============================================================
# Core file logging
# ============================================================
def log(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"{timestamp}: {message}"

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")


# ============================================================
# Convenience helpers (unchanged)
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


