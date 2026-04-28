from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class KnowledgeLayout:
    page_root: Path
    index_path: Path
    log_path: Path
    hot_path: Path


def detect_knowledge_layout(repo_root: Path) -> KnowledgeLayout | None:
    content_root = repo_root / "content"
    if (content_root / "index.md").exists():
        return KnowledgeLayout(
            page_root=content_root,
            index_path=content_root / "index.md",
            log_path=content_root / "log.md",
            hot_path=content_root / "hot.md",
        )

    wiki_root = repo_root / "wiki"
    root_index = repo_root / "index.md"
    wiki_index = wiki_root / "index.md"
    if wiki_root.exists() and any(wiki_root.rglob("*.md")):
        return KnowledgeLayout(
            page_root=wiki_root,
            index_path=root_index if root_index.exists() else wiki_index,
            log_path=(repo_root / "log.md")
            if (repo_root / "log.md").exists()
            else (wiki_root / "log.md"),
            hot_path=(repo_root / "hot.md")
            if (repo_root / "hot.md").exists()
            else (wiki_root / "hot.md"),
        )

    if root_index.exists():
        return KnowledgeLayout(
            page_root=repo_root,
            index_path=root_index,
            log_path=repo_root / "log.md",
            hot_path=repo_root / "hot.md",
        )

    return None
