from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent / "submission.zip"
EXCLUDE_PARTS = {".git", "__pycache__", ".pytest_cache"}


def main() -> None:
    if OUT.exists():
        OUT.unlink()
    with ZipFile(OUT, "w", ZIP_DEFLATED) as archive:
        for path in ROOT.rglob("*"):
            if path.is_dir():
                continue
            if any(part in EXCLUDE_PARTS for part in path.parts):
                continue
            archive.write(path, path.relative_to(ROOT.parent))
    print(OUT)


if __name__ == "__main__":
    main()
