
import sqlite3


# =========================================================
# Database Initialization
# =========================================================
def init_db():
    conn = sqlite3.connect("dj_library.db")
    cursor = conn.cursor()

    # Tracks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            artist TEXT,
            bpm INTEGER,
            musical_key TEXT,
            genre TEXT,
            filepath TEXT
        )
    """)

    # Crates table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )
    """)

    # Crate-to-track mapping
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crate_tracks (
            crate_id INTEGER,
            track_id INTEGER,
            FOREIGN KEY (crate_id) REFERENCES crates(id),
            FOREIGN KEY (track_id) REFERENCES tracks(id)
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# Insert Track (used by audio_reader.py)
# =========================================================
def insert_track(title, artist, genre, bpm, key, filepath):
    conn = sqlite3.connect("dj_library.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tracks (title, artist, bpm, musical_key, genre, filepath)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, artist, bpm, key, genre, filepath))

    track_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return track_id


# =========================================================
# Auto‑Crate Creation
# =========================================================
def auto_crate(name, min_bpm=None, max_bpm=None, key=None, genre=None, artist=None, title=None):
    conn = sqlite3.connect("dj_library.db")
    cursor = conn.cursor()

    # Create crate
    cursor.execute("INSERT INTO crates (name) VALUES (?)", (name,))
    crate_id = cursor.lastrowid

    # Build dynamic query
    query = "SELECT id FROM tracks WHERE 1=1"
    params = []

    if min_bpm is not None:
        query += " AND bpm >= ?"
        params.append(min_bpm)

    if max_bpm is not None:
        query += " AND bpm <= ?"
        params.append(max_bpm)

    if key is not None:
        query += " AND musical_key = ?"
        params.append(key)

    if genre is not None:
        query += " AND genre = ?"
        params.append(genre)

    if artist is not None:
        query += " AND artist LIKE ?"
        params.append(f"%{artist}%")

    if title is not None:
        query += " AND title LIKE ?"
        params.append(f"%{title}%")

    cursor.execute(query, params)
    tracks = cursor.fetchall()

    # Add tracks to crate
    for (track_id,) in tracks:
        cursor.execute(
            "INSERT INTO crate_tracks (crate_id, track_id) VALUES (?, ?)",
            (crate_id, track_id)
        )

    conn.commit()
    conn.close()

    print(f"Auto‑crate '{name}' created with {len(tracks)} tracks.")


# =========================================================
# Track Retrieval
# =========================================================
def get_tracks():
    conn = sqlite3.connect("dj_library.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tracks ORDER BY artist, title")
    results = cursor.fetchall()

    conn.close()
    return results


def get_tracks_in_crate(crate_id):
    conn = sqlite3.connect("dj_library.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tracks.id, tracks.title, tracks.artist, tracks.bpm,
               tracks.musical_key, tracks.filepath
        FROM tracks
        JOIN crate_tracks ON tracks.id = crate_tracks.track_id
        WHERE crate_tracks.crate_id = ?
        ORDER BY tracks.artist, tracks.title
    """, (crate_id,))

    results = cursor.fetchall()
    conn.close()
    return results


# =========================================================
# Crate Retrieval
# =========================================================
def get_crates():
    conn = sqlite3.connect("dj_library.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM crates")
    crates = cursor.fetchall()

    conn.close()
    return crates


# =========================================================
# Searching
# =========================================================
def search_by_artist(term):
    conn = sqlite3.connect("dj_library.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM tracks
        WHERE artist LIKE ?
        ORDER BY artist, title
    """, (f"%{term}%",))

    results = cursor.fetchall()
    conn.close()
    return results


def search_by_title(term):
    conn = sqlite3.connect("dj_library.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM tracks
        WHERE title LIKE ?
        ORDER BY artist, title
    """, (f"%{term}%",))

    results = cursor.fetchall()
    conn.close()
    return results


# =========================================================
# Display Formatting
# =========================================================
def format_track(track):
    track_id, title, artist, bpm, musical_key, genre, filepath = track
    return f"[{track_id}] {artist} – {title} | {bpm} BPM | Key: {musical_key} | Genre: {genre}"


# =========================================================
# Missing Metadata Reports
# =========================================================
def show_tracks_missing_bpm():
    conn = sqlite3.connect("dj_library.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT title, artist, filepath, bpm
        FROM tracks
        WHERE bpm IS NULL
           OR bpm = ''
           OR bpm = '0'
           OR bpm = 'Unknown'
    """)

    results = cursor.fetchall()
    conn.close()

    if not results:
        print("\nAll tracks have BPM values.\n")
        return

    print("\nTracks Missing BPM:")
    print("-" * 40)

    for title, artist, filepath, bpm in results:
        print(f"{title} - {artist}")
        print(f"File: {filepath}")
        print(f"BPM: {bpm}")
        print("-" * 40)


def show_tracks_missing_genre():
    conn = sqlite3.connect("dj_library.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT title, artist, filepath, genre
        FROM tracks
        WHERE genre IS NULL
           OR genre = ''
           OR genre = 'Unknown'
    """)

    results = cursor.fetchall()
    conn.close()

    if not results:
        print("\nAll tracks have Genre values.\n")
        return

    print("\nTracks Missing Genre:")
    print("-" * 40)

    for title, artist, filepath, genre in results:
        print(f"{title} - {artist}")
        print(f"File: {filepath}")
        print(f"Genre: {genre}")
        print("-" * 40)


# =========================================================
# Duplicate Detection + Cleanup
# =========================================================
def find_duplicates():
    conn = sqlite3.connect("dj_library.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            title, artist, bpm,
            COUNT(*) AS count,
            GROUP_CONCAT(id) AS ids
        FROM tracks
        GROUP BY title, artist, bpm
        HAVING count > 1
    """)

    duplicates = cursor.fetchall()
    conn.close()
    return duplicates


def delete_duplicate_tracks():
    conn = sqlite3.connect("dj_library.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            title, artist, bpm,
            GROUP_CONCAT(id) AS ids
        FROM tracks
        GROUP BY title, artist, bpm
        HAVING COUNT(*) > 1
    """)

    groups = cursor.fetchall()
    deleted_count = 0

    for title, artist, bpm, ids_str in groups:
        ids = sorted(int(x) for x in ids_str.split(","))

        keep_id = ids[0]
        delete_ids = ids[1:]

        for track_id in delete_ids:
            cursor.execute("DELETE FROM crate_tracks WHERE track_id = ?", (track_id,))
            cursor.execute("DELETE FROM tracks WHERE id = ?", (track_id,))
            deleted_count += 1

    conn.commit()
    conn.close()

    return deleted_count

