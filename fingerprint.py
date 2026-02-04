
# fingerprint.py
#
# Generates a stable audio fingerprint for duplicate detection.
# Uses:
# - pydub for audio loading
# - numpy for signal processing
#
# The fingerprint is based on the first 30 seconds of audio.
# This is enough to uniquely identify a track while keeping it fast.

from pydub import AudioSegment
import numpy as np
import hashlib


# ============================================================
# Load audio and return normalized sample array
# ============================================================
def load_audio(filepath: str, max_ms: int = 30000):
    """
    Loads the first `max_ms` milliseconds of audio.
    Returns a numpy array of samples, or None on failure.
    """
    try:
        audio = AudioSegment.from_file(filepath)

        # Normalize format
        audio = audio.set_channels(1)          # mono for consistency
        audio = audio.set_frame_rate(22050)    # downsample for speed

        # Trim to first 30 seconds
        audio = audio[:max_ms]

        samples = np.array(audio.get_array_of_samples()).astype(np.float32)
        return samples

    except Exception:
        return None


# ============================================================
# Generate fingerprint hash
# ============================================================
def generate_fingerprint(filepath: str) -> str | None:
    """
    Generates a stable fingerprint hash for the audio file.
    Returns a hex string or None if audio can't be read.
    """
    samples = load_audio(filepath)

    if samples is None or len(samples) == 0:
        return None

    # Normalize amplitude
    samples = samples / (np.max(np.abs(samples)) + 1e-9)

    # Downsample further for hashing
    reduced = samples[::100]  # take every 100th sample

    # Convert to bytes
    data_bytes = reduced.tobytes()

    # Hash using SHA‑1 (fast + stable)
    fingerprint = hashlib.sha1(data_bytes).hexdigest()

    return fingerprint



