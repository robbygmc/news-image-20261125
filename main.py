"""Copy and validate entry.png (1024x1024 PNG, max 1 MiB) to the output directory."""

import hashlib
import os
import shutil
import sys
from pathlib import Path

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_SIZE = 1048576
REQUIRED_WIDTH = 1024
REQUIRED_HEIGHT = 1024
HEADER_LENGTH = 24


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def main():
    if "MAKEFUN_OUTPUT_DIR" in os.environ:
        output_value = os.environ["MAKEFUN_OUTPUT_DIR"]
        if output_value == "":
            fail("MAKEFUN_OUTPUT_DIR is set but empty")
        output_dir = Path(output_value)
    else:
        output_dir = Path("/output")

    if output_dir.exists() and not output_dir.is_dir():
        fail(f"MAKEFUN_OUTPUT_DIR points at an existing file: {output_dir}")

    source = Path(__file__).resolve().parent / "entry.png"

    if not source.is_file():
        fail(f"entry.png not found: {source}")

    try:
        data = source.read_bytes()
    except OSError as exc:
        fail(f"could not read entry.png: {exc}")

    size = len(data)

    if size > MAX_SIZE:
        fail(f"entry.png is too large: {size} bytes (max {MAX_SIZE} bytes)")

    if not data.startswith(PNG_MAGIC):
        fail("entry.png does not start with the PNG magic bytes")

    if len(data) < HEADER_LENGTH:
        fail(f"entry.png is too short to contain a PNG header: {size} bytes")

    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    if width != REQUIRED_WIDTH or height != REQUIRED_HEIGHT:
        fail(
            f"entry.png must be exactly {REQUIRED_WIDTH}x{REQUIRED_HEIGHT}, "
            f"got {width}x{height}"
        )

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        fail(f"could not create output directory {output_dir}: {exc}")

    if not output_dir.is_dir():
        fail(f"MAKEFUN_OUTPUT_DIR is not a directory: {output_dir}")

    destination = output_dir / "entry.png"

    try:
        shutil.copyfile(source, destination)
    except OSError as exc:
        fail(f"could not copy entry.png to {destination}: {exc}")

    try:
        copied = destination.read_bytes()
    except OSError as exc:
        fail(f"could not read copied file {destination}: {exc}")

    source_hash = hashlib.sha256(data).hexdigest()
    copied_hash = hashlib.sha256(copied).hexdigest()
    if copied != data or copied_hash != source_hash:
        fail("copied file is not byte-identical to the source")

    print(f"destination: {destination}")
    print(f"size: {size}")
    print(f"sha256: {source_hash}")


if __name__ == "__main__":
    main()
