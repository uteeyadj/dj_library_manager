# uteeya-dj-tools

A professional DJ library scanning and management tool featuring:

- Intelligent BPM detection (librosa)
- Musical key detection (Camelot-style)
- Audio fingerprinting (Chromaprint / AcoustID)
- Duplicate detection
- Smart auto‑crates (energy, genre, key groups)
- Fast and full scan modes
- Rich-powered CLI output
- Metadata normalization and extraction
- Persistent database with upgrade support

This tool is designed for DJs who want a fast, reliable, and intelligent way to organize and analyze their music library.

---

## Installation

Install from PyPI:

```
pip install uteeya-dj-tools
```

This installs the command‑line tool:

```
djmanager
```

## Usage
After installation, launch the main CLI:
```
djmanager
```
This opens the interactive menu where you can scan your library, analyze tracks, detect duplicates, and manage crates.

### Full Library Scan
```
djmanager scan --full /path/to/music
```

### Fast Scan (only new or changed files)
```
djmanager scan --fast /path/to/music
```

### View Library Statistics
```
djmanager stats
```

### Detect Duplicates
```
djmanager duplicates
```

### Generate Smart Crates
```
djmanager crates auto
```


