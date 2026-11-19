"""news-image-20261119 entry.

Builds the one-image summary of Thursday 19 November 2026's world news.
The front page artwork is bundled with this repository as entry.png; the
script's job is to confirm that file is a well-formed PNG within the
size limit and place an exact copy at the output location. Nothing here
touches the network, the clock or any random source, so running it twice
yields the same bytes twice.
"""

import hashlib
import os
import struct
import sys
from pathlib import Path

IMAGE_FILE = "entry.png"
SIDE_LIMIT = 1024
MAGIC = b"\x89PNG\r\n\x1a\n"


def abort(reason):
    print("error:", reason, file=sys.stderr)
    sys.exit(1)


def fetch_source():
    folder = Path(__file__).resolve().parent
    candidate = folder / IMAGE_FILE
    try:
        content = candidate.read_bytes()
    except OSError as exc:
        abort(f"cannot read {candidate}: {exc}")
    if content[: len(MAGIC)] != MAGIC:
        abort(f"{candidate} is not a PNG file")
    if len(content) < 24:
        abort(f"{candidate} is too short to carry a PNG header")
    if content[12:16] != b"IHDR":
        abort(f"{candidate} has no IHDR chunk where one belongs")
    wide, tall = struct.unpack(">II", content[16:24])
    if not (1 <= wide <= SIDE_LIMIT and 1 <= tall <= SIDE_LIMIT):
        abort(f"image measures {wide}x{tall}; the cap is {SIDE_LIMIT}x{SIDE_LIMIT}")
    return content, wide, tall


def place_copy(content, wide, tall):
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    destination = out_dir / IMAGE_FILE
    destination.write_bytes(content)
    after = destination.read_bytes()
    if hashlib.sha256(after).hexdigest() != hashlib.sha256(content).hexdigest():
        abort(f"{destination} came out different from the source")
    print(f"wrote {destination} ({wide}x{tall}, {len(content)} bytes)")


def main():
    content, wide, tall = fetch_source()
    place_copy(content, wide, tall)


if __name__ == "__main__":
    main()
