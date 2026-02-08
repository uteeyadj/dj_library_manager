from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

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

    def print_summary(self, mode: str, elapsed: float):
        table = Table(show_header=False, box=None, padding=(0, 1))

        table.add_row("Mode:", mode)
        table.add_row("Total scanned:", str(self.total_scanned))
        table.add_row("New tracks added:", str(self.added))
        table.add_row("Duplicates skipped:", str(self.duplicates))
        table.add_row("Missing BPM:", str(self.missing_bpm))
        table.add_row("Missing Key:", str(self.missing_key))
        table.add_row("Missing Genre:", str(self.missing_genre))
        table.add_row("Unreadable files:", str(self.unreadable))
        table.add_row("Time:", f"{elapsed:.2f}s")

        panel = Panel(
            table,
            title="SCAN SUMMARY",
            title_align="center",
            border_style="cyan",
            padding=(1, 2),
        )

        console.print(panel)
