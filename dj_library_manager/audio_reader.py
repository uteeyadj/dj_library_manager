
# audio_reader.py

#

# Main scanning engine:

# - reads audio files

# - extracts metadata

# - normalizes fields

# - generates fingerprints

# - detects duplicates

# - supports fast-scan mode

# - logs events

# - builds scan reports

import os
import time
from mutagen import File as MutagenFile

from dj_library_manager.metadata_utils import (
    normalize_title,
    normalize_artist,
    normalize_genre,
    extract_bpm,
    extract_key,
    extract_genre,
    extract_title,
    extract_artist,
)
import librosa
import numpy as np

KEYS = [
    "C", "C#", "D", "D#", "E", "F",
    "F#", "G", "G#", "A", "A#", "B"
]

def detect_bpm(filepath):
    try:
        y, sr = librosa.load(filepath, sr=None, mono=True)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        return int(tempo)
    except Exception:
        return None

def detect_key(filepath):
    try:
        y, sr = librosa.load(filepath, sr=None, mono=True)
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        chroma_mean = chroma.mean(axis=1)
        key_index = chroma_mean.argmax()
        return KEYS[key_index]
    except Exception:
        return None

from dj_library_manager.fingerprint import generate_fingerprint

from dj_library_manager.logging_utils import (
    log_added,
    log_duplicate,
    log_missing_bpm,
    log_missing_key,
    log_missing_genre,
    log_error,
    info,
    success,
    warning,
    error,
    mode,
)


from dj_library_manager.scan_report import ScanReport

from dj_library_manager.db_upgrade import (
    get_scanned_file,
    update_scanned_file,
    fingerprint_exists,
    insert_fingerprint,
)

from dj_library_manager.database import insert_track


# ============================================================
# ANSI Color Codes
# ============================================================
class Color:
    RESET = "\033[0m"

    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"

    BOLD = "\033[1m"
    DIM = "\033[2m"


def progress_bar(percent, length=30):
    filled = int(length * percent / 100)
    return "█" * filled + "░" * (length - filled)


SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".flac", ".m4a", ".aac"}


def is_audio_file(filepath: str) -> bool:
    _, ext = os.path.splitext(filepath.lower())
    return ext in SUPPORTED_EXTENSIONS


# ============================================================
# SCAN FOLDER (supports fast_mode)
# ============================================================
def scan_folder(folder_path: str, fast_mode: bool = False) -> ScanReport:
    report = ScanReport()

    # -----------------------------------------
    # Pre-count audio files
    # -----------------------------------------
    all_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if is_audio_file(file):
                all_files.append(os.path.join(root, file))

    total_files = len(all_files)
    print(f"\nFound {total_files} audio files.\n")

    current_index = 0
    start_time = time.time()

    # -----------------------------------------
    # Main scanning loop
    # -----------------------------------------
    try:
        for filepath in all_files:
            current_index += 1

            # Progress percentage
            percent = (current_index / total_files) * 100

            # ETA calculation
            elapsed = time.time() - start_time
            avg_time = elapsed / current_index
            remaining = avg_time * (total_files - current_index)

            # Progress bar
            bar = progress_bar(percent)

            print(
                f"{Color.CYAN}[{bar}] {percent:5.1f}%{Color.RESET} "
                f"{Color.BLUE}Scanning:{Color.RESET} {filepath} "
                f"{Color.YELLOW}| ETA: {remaining:5.1f}s{Color.RESET}"
            )

            report.inc_scanned()

            try:
                process_file(filepath, report, fast_mode)
            except Exception as e:
                log_error(filepath, str(e))
                report.inc_unreadable()

    except KeyboardInterrupt:
        print("\nScan cancelled by user.\n")
        return report

    # -----------------------------------------
    # End of scan summary
    # -----------------------------------------
    elapsed = time.time() - start_time
    mode_label = "Fast Scan" if fast_mode else "Full Scan"
    report.print_summary(mode_label, elapsed)
    return report


# ============================================================
# PROCESS FILE (supports fast_mode)
# ============================================================
def process_file(filepath: str, report: ScanReport, fast_mode: bool):
    # -----------------------------------------
    # Check last modified time
    # -----------------------------------------
    last_modified = int(os.path.getmtime(filepath))
    scanned_info = get_scanned_file(filepath)

    # Skip unchanged files
    if scanned_info and scanned_info[0] == last_modified:
        return

    # -----------------------------------------
    # Load metadata
    # -----------------------------------------
    try:
        audio = MutagenFile(filepath, easy=True)
        tags = audio.tags if audio else None
    except Exception:
        tags = None

    # -----------------------------------------
    # Extract metadata
    # -----------------------------------------
    title = normalize_title(extract_title(tags, filepath))
    artist = normalize_artist(extract_artist(tags))
    genre = normalize_genre(extract_genre(tags))
    bpm = extract_bpm(tags)
    key = extract_key(tags)
     
    # -----------------------------------------
    # Intelligent detection (BPM, Key)
    # -----------------------------------------
    if bpm is None:
        detected_bpm = detect_bpm(filepath)
        if detected_bpm:
            bpm = detected_bpm

    if key is None:
        detected_key = detect_key(filepath)
        if detected_key:
            key = detected_key

    # -----------------------------------------
    # Fingerprint (skip in fast mode)
    # -----------------------------------------
    fingerprint = None
    if not fast_mode:
        fingerprint = generate_fingerprint(filepath)

    # -----------------------------------------
    # Duplicate detection
    # -----------------------------------------
    if fingerprint and not fast_mode:
        existing_track_id = fingerprint_exists(fingerprint)
        if existing_track_id:
            log_duplicate(filepath)
            report.inc_duplicate()
            update_scanned_file(filepath, last_modified, fingerprint)
            return

    # -----------------------------------------
    # Insert into database
    # -----------------------------------------
    track_id = insert_track(
        title=title,
        artist=artist,
        genre=genre,
        bpm=bpm,
        key=key,
        filepath=filepath,
    )

    # Store fingerprint (only in full scan)
    if fingerprint and not fast_mode:
        insert_fingerprint(fingerprint, track_id)

    # Update scanned_files table
    update_scanned_file(filepath, last_modified, fingerprint)

    # -----------------------------------------
    # Logging + report counters
    # -----------------------------------------
    log_added(filepath)
    report.inc_added()

    if bpm is None:
        log_missing_bpm(filepath)
        report.inc_missing_bpm()

    if key is None:
        log_missing_key(filepath)
        report.inc_missing_key()

    if genre is None:
        log_missing_genre(filepath)
        report.inc_missing_genre()






