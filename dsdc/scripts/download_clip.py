import os
import hashlib
import requests
import logging
import sys
from pathlib import Path

from dsdc import CONFIG

# Base URL and target directory
BASE_URL = "https://huggingface.co/openai/clip-vit-base-patch32/resolve/main"
DEST_DIR = CONFIG.paths.clip_model
DEST_DIR.mkdir(exist_ok=True, parents=True)

# Expected SHA256 checksums for each file
SHA256 = {
    "tokenizer_config.json": "34b7336e4bee12e0a9730eaf5189f582ef3c3eea5027f65730e5717256755aad",
    "special_tokens_map.json": "f8c0d6c39aee3f8431078ef6646567b0aba7f2246e9c54b8b99d55c22b707cbf",
    "config.json": "b575ef3c36f2a057fa19e221650105052d61cc9c1a972ec15019c6261ec98770",
    "merges.txt": "f526393189112391ce6f9795d4695f704121ce452c3aad1f5335cc41337eba85",
    "pytorch_model.bin": "a63082132ba4f97a80bea76823f544493bffa8082296d62d71581a4feff1576f",
    "vocab.json": "5047b556ce86ccaf6aa22b3ffccfc52d391ea4accdab9c2f2407da5b742d4363",
    "preprocessor_config.json": "910e70b3956ac9879ebc90b22fb3bc8a75b6a0677814500101a4c072bd7857bd",
}

# Logging configuration

def sha256sum(file_path: Path, chunk_size=8192) -> str:
    """Compute the SHA256 checksum of a file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def download_file(url: str, dest_path: Path) -> bool:
    """Download a file from a URL and save it to disk."""
    try:
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(dest_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return True
    except Exception as e:
        logging.error(f"\n❌ Failed to download {url}: {e}")
        return False


def file_valid(path: Path, expected_hash: str) -> bool:
    """Check if a file exists and matches the expected SHA256 checksum."""
    if not path.exists():
        return False
    actual_hash = sha256sum(path)
    return actual_hash == expected_hash


if __name__ == "__main__":
    failed_files = []

    for filename, expected_hash in SHA256.items():
        url = f"{BASE_URL}/{filename}"
        dest_path = DEST_DIR / filename

        # Log one-line progress message (no newline yet)
        logging.info(f"⬇️ {filename.ljust(25)}...")

        if file_valid(dest_path, expected_hash):
            logging.info("    ✔️  (already exists and verified)")
            continue

        success = download_file(url, dest_path)
        if success and file_valid(dest_path, expected_hash):
            logging.info("    ✔️  (downloaded and verified)")
        else:
            logging.info("    ✘ Failed or corrupted")
            failed_files.append(filename)
            if dest_path.exists():
                dest_path.unlink()  # Remove partial or invalid file

    # Summary
    if failed_files:
        logging.error(f"\n❌ Download failed for {len(failed_files)} file(s):")
        for f in failed_files:
            logging.error(f"   - {f}")
        sys.exit(1)
    else:
        logging.info("\n🎉 All files downloaded and verified successfully.")
