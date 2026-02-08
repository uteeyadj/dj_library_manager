import argparse
from dj_library_manager import __version__
from dj_library_manager.db_upgrade import upgrade_database
from dj_library_manager.update_checker import check_for_updates

from dj_library_manager.database import (
    init_db,
    auto_crate,
    get_crates,
    get_tracks,
    get_tracks_in_crate,
    search_by_artist,
    search_by_title,
    format_track,
    show_tracks_missing_bpm,
    show_tracks_missing_genre,
    find_duplicates,
    delete_duplicate_tracks,
)

from dj_library_manager.audio_reader import scan_folder
from collections import Counter

def parse_args():
    parser = argparse.ArgumentParser(
        description="DJ Library Manager – A professional DJ library scanning and management tool",
        add_help=True
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Show the installed version and exit"
    )

    return parser.parse_args()

# ============================================================
# OPEN CRATE (SUMMARY + SORT)
# ============================================================
def open_crate(crate):
    crate_id, crate_name = crate

    print(f"\n=== Crate: {crate_name} ===")

    tracks = get_tracks_in_crate(crate_id)
    if not tracks:
        print("This crate is empty.")
        return

    print(f"{len(tracks)} tracks found:\n")

    # Track structure:
    # (id, title, artist, bpm, musical_key, filepath)
    bpms = [t[3] for t in tracks if t[3] is not None]
    keys = [t[4] for t in tracks if t[4]]

    if bpms:
        avg_bpm = sum(bpms) / len(bpms)
        print(f"Average BPM: {avg_bpm:.1f}")
        print(f"BPM Range: {min(bpms)}–{max(bpms)}")

    if keys:
        common_key = Counter(keys).most_common(1)[0][0]
        print(f"Most common key: {common_key}")

    # Sorting menu
    print("\n--- Sorting Options ---")
    print("1. Artist")
    print("2. Title")
    print("3. BPM")
    print("4. Key")
    print("5. No sorting")

    sort_choice = input("Choose sorting option: ")

    if sort_choice == "1":
        tracks.sort(key=lambda t: (t[2] or "").lower())
    elif sort_choice == "2":
        tracks.sort(key=lambda t: (t[1] or "").lower())
    elif sort_choice == "3":
        tracks.sort(key=lambda t: (t[3] or 0))
    elif sort_choice == "4":
        tracks.sort(key=lambda t: (t[4] or ""))

    print("")
    for t in tracks:
        track_id, title, artist, bpm, musical_key, filepath = t
        print(f"[{track_id}] {artist} – {title} | {bpm} BPM | Key: {musical_key}")


# ============================================================
# SMART AUTO‑CRATES
# ============================================================
def smart_auto_crates_menu():
    print("\n=== Smart Auto‑Crates ===")
    print("1. Energy Crates")
    print("2. Genre Crates")
    print("3. Key‑Compatible Crates")
    print("4. Back")

    choice = input("Choose an option: ")

    if choice == "1":
        create_energy_crates()
    elif choice == "2":
        create_genre_crates()
    elif choice == "3":
        create_key_crates()


def create_energy_crates():
    print("\nCreating Energy Crates...")

    auto_crate(name="Low Energy (0–95 BPM)", max_bpm=95)
    auto_crate(name="Mid Energy (96–115 BPM)", min_bpm=96, max_bpm=115)
    auto_crate(name="High Energy (116+ BPM)", min_bpm=116)

    print("Energy crates created!")


def create_genre_crates():
    print("\nCreating Genre Crates...")

    tracks = get_tracks()
    genres = set(t[5] for t in tracks if t[5])

    for g in genres:
        auto_crate(name=f"{g} Collection", genre=g)

    print("Genre crates created!")


def create_key_crates():
    print("\nCreating Key‑Compatible Crates...")

    camelot_groups = {
        "1A / 1B": ["1A", "1B"],
        "2A / 2B": ["2A", "2B"],
        "3A / 3B": ["3A", "3B"],
        "4A / 4B": ["4A", "4B"],
        "5A / 5B": ["5A", "5B"],
        "6A / 6B": ["6A", "6B"],
        "7A / 7B": ["7A", "7B"],
        "8A / 8B": ["8A", "8B"],
        "9A / 9B": ["9A", "9B"],
        "10A / 10B": ["10A", "10B"],
        "11A / 11B": ["11A", "11B"],
        "12A / 12B": ["12A", "12B"],
    }

    tracks = get_tracks()

    for name, keys in camelot_groups.items():
        matching = [t for t in tracks if t[4] in keys]
        if matching:
            auto_crate(name=f"Key Group {name}")

    print("Key‑compatible crates created!")


# ============================================================
# MAIN MENU
# ============================================================
def main():
    args = parse_args()

    # Check for updates before doing anything else
    check_for_updates()

    if args.version:
        print(f"DJ Library Manager v{__version__}")
        return

    init_db()
    upgrade_database()
    print(">>> RUNNING CORRECT MAIN.PY <<<")


    while True:
        print("\n=== DJ Library Manager ===")
        print("1. Scan music folder")
        print("2. View all tracks")
        print("3. View crates")
        print("4. Search tracks")
        print("5. Create auto‑crate")
        print("6. Show tracks missing BPM")
        print("7. Show tracks missing Genre")
        print("8. Smart Auto‑Crates")
        print("9. Exit")
        print("10. Show duplicate tracks")
        print("11. Auto‑delete duplicates")
        print("12. Fast Scan (no fingerprinting)")

        choice = input("Choose an option: ")

        # 1 — Full Scan
        if choice == "1":
            folder = input("Enter folder path to scan: ")
            scan_folder(folder)

        # 2 — View All Tracks
        elif choice == "2":
            tracks = get_tracks()
            for t in tracks:
                print(format_track(t))

        # 3 — View Crates
        elif choice == "3":
            crates = get_crates()

            print("\n=== Crates ===")
            if not crates:
                print("No crates found.")
                continue

            for i, crate in enumerate(crates, start=1):
                crate_id, crate_name = crate
                print(f"{i}. {crate_name}")

            selection = input("\nSelect a crate number (or press Enter to cancel): ")
            if not selection.strip():
                continue

            try:
                index = int(selection) - 1
                if 0 <= index < len(crates):
                    open_crate(crates[index])
                else:
                    print("Invalid crate number.")
            except ValueError:
                print("Invalid input.")

        # 4 — Search
        elif choice == "4":
            term = input("Search term (artist/title): ")

            print("\nArtist matches:")
            for t in search_by_artist(term):
                print(format_track(t))

            print("\nTitle matches:")
            for t in search_by_title(term):
                print(format_track(t))

        # 5 — Create Auto‑Crate
        elif choice == "5":
            print("\n=== Create Auto‑Crate ===")
            crate_name = input("Crate name: ")
            min_bpm = input("Minimum BPM (or press Enter to skip): ")
            max_bpm = input("Maximum BPM (or press Enter to skip): ")
            genre = input("Genre (or press Enter to skip): ")

            min_bpm = int(min_bpm) if min_bpm.strip() else None
            max_bpm = int(max_bpm) if max_bpm.strip() else None
            genre = genre.strip() if genre.strip() else None

            auto_crate(
                name=crate_name,
                min_bpm=min_bpm,
                max_bpm=max_bpm,
                genre=genre,
            )

        # 6 — Missing BPM
        elif choice == "6":
            show_tracks_missing_bpm()

        # 7 — Missing Genre
        elif choice == "7":
            show_tracks_missing_genre()

        # 8 — Smart Auto‑Crates
        elif choice == "8":
            smart_auto_crates_menu()

        # 9 — Exit
        elif choice == "9":
            print("Goodbye!")
            break

        # 10 — Show Duplicates
        elif choice == "10":
            dups = find_duplicates()

            if not dups:
                print("\nNo duplicates found.\n")
            else:
                print("\nDuplicate Tracks:")
                print("-" * 40)
                for title, artist, bpm, count, ids in dups:
                    print(f"{artist} – {title} | {bpm} BPM")
                    print(f"Count: {count}")
                    print(f"IDs: {ids}")
                    print("-" * 40)

        # 11 — Auto‑Delete Duplicates
        elif choice == "11":
            removed = delete_duplicate_tracks()
            print(f"\nRemoved {removed} duplicate tracks.\n")

        # 12 — Fast Scan
        elif choice == "12":
            folder = input("Enter folder path to scan: ")
            scan_folder(folder, fast_mode=True)

        # Invalid Choice
        else:
            print("Invalid choice. Try again.")


