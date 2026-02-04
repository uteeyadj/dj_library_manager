
# scan_report.py
#
# Builds a clean, structured summary of the scanning process.
# Used by audio_reader.py to report:
# - total scanned
# - new tracks added
# - duplicates skipped
# - missing metadata
# - unreadable files

class ScanReport:
    def __init__(self):
        self.total_scanned = 0
        self.added = 0
        self.duplicates = 0
        self.missing_bpm = 0
        self.missing_key = 0
        self.missing_genre = 0
        self.unreadable = 0

    # ============================================================
    # Increment helpers
    # ============================================================
    def inc_scanned(self):
        self.total_scanned += 1

    def inc_added(self):
        self.added += 1

    def inc_duplicate(self):
        self.duplicates += 1

    def inc_missing_bpm(self):
        self.missing_bpm += 1

    def inc_missing_key(self):
        self.missing_key += 1

    def inc_missing_genre(self):
        self.missing_genre += 1

    def inc_unreadable(self):
        self.unreadable += 1

    # ============================================================
    # Summary formatting
    # ============================================================
    def summary_text(self) -> str:
        lines = [
            "=== Scan Summary ===",
            f"Total scanned: {self.total_scanned}",
            f"New tracks added: {self.added}",
            f"Duplicates skipped: {self.duplicates}",
            f"Missing BPM: {self.missing_bpm}",
            f"Missing Key: {self.missing_key}",
            f"Missing Genre: {self.missing_genre}",
            f"Unreadable files: {self.unreadable}",
        ]
        return "\n".join(lines)

    def __str__(self):
        return self.summary_text()


