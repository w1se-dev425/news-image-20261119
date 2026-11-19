"""news-image-20261119 entry (Python 3.13, standard library only).

Writes one image summing up Thursday 19 November 2026's world news to
/output/entry.png: a newspaper front page (masthead, hero illustration of
the day's lead story, four more stories and a briefs strip) composed from
that day's top stories. The program reads the bundled image `entry.png` (held in this repository),
checks it really is a PNG no larger than 1024x1024, writes it to the output
path and verifies the copy byte for byte, so it is fully deterministic: no
randomness, no network, no clock reads; two runs write identical bytes.
"""

import hashlib
import os
import struct
from pathlib import Path

OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

HERE = Path(__file__).resolve().parent
SRC = HERE / "entry.png"

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_SIDE = 1024


def read_and_validate(path):
    data = path.read_bytes()
    if not data.startswith(PNG_MAGIC):
        raise SystemExit(f"not a PNG file: {path}")
    if len(data) < 33:
        raise SystemExit(f"PNG too short to hold an IHDR chunk: {path}")
    width, height = struct.unpack(">II", data[16:24])
    if width == 0 or height == 0 or width > MAX_SIDE or height > MAX_SIDE:
        raise SystemExit(
            f"PNG is {width}x{height}, expected at most {MAX_SIDE}x{MAX_SIDE}: {path}"
        )
    return data, width, height


def main():
    data, width, height = read_and_validate(SRC)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUTPUT_DIR / "entry.png"
    out.write_bytes(data)
    if hashlib.sha256(out.read_bytes()).hexdigest() != hashlib.sha256(data).hexdigest():
        raise SystemExit(f"output does not match source: {out}")
    print(f"wrote {out} ({width}x{height}, {len(data)} bytes)")


if __name__ == "__main__":
    main()
