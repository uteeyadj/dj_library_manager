
import sqlite3

DB_PATH = "dj_library.db"


# ============================================================
# Database Upgrade: Adds new tables for scanning + fingerprints
# ============================================================
def upgrade_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # -----------------------------------------
    # Table: scanned_files
    # Tracks files we've already scanned
    # -----------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scanned_files (
            filepath TEXT PRIMARY KEY,
            last_modified INTEGER,
            fingerprint TEXT
        )
    """)

    # -----------------------------------------
    # Table: fingerprints
    # Prevents duplicate audio content
    # -----------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fingerprints (
            fingerprint TEXT PRIMARY KEY,
            track_id INTEGER,
            FOREIGN KEY (track_id) REFERENCES tracks(id)
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# Retrieve scanned file info
# ============================================================
def get_scanned_file(filepath: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT last_modified, fingerprint FROM scanned_files WHERE filepath = ?",
        (filepath,)
    )

    row = cursor.fetchone()
    conn.close()
    return row  # (last_modified, fingerprint) or None


# ============================================================
# Insert or update scanned file entry
# ============================================================
def update_scanned_file(filepath: str, last_modified: int, fingerprint: str | None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO scanned_files (filepath, last_modified, fingerprint)
        VALUES (?, ?, ?)
        ON CONFLICT(filepath) DO UPDATE SET
            last_modified = excluded.last_modified,
            fingerprint = excluded.fingerprint
    """, (filepath, last_modified, fingerprint))

    conn.commit()
    conn.close()


# ============================================================
# Check if fingerprint already exists
# ============================================================
def fingerprint_exists(fingerprint: str) -> int | None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT track_id FROM fingerprints WHERE fingerprint = ?",
        (fingerprint,)
    )

    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


# ============================================================
# Insert fingerprint → track mapping
# ============================================================
def insert_fingerprint(fingerprint: str, track_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO fingerprints (fingerprint, track_id)
        VALUES (?, ?)
    """, (fingerprint, track_id))

    conn.commit()
    conn.close()

