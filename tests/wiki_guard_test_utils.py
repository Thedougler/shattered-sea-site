from __future__ import annotations

import json
from pathlib import Path


def write_required_root(repo_root: Path) -> None:
    for name in ["index.md", "hot.md", "log.md"]:
        (repo_root / name).write_text("ok\n", encoding="utf-8")


def write_page(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def write_manifest(repo_root: Path, sources: dict[str, dict[str, object]]) -> None:
    payload = {"version": 1, "stats": {}, "sources": sources}
    (repo_root / ".manifest.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
