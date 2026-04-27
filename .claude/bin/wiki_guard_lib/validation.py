from __future__ import annotations

from pathlib import Path

from .constants import SNAKE_CASE_RE, WIKILINK_RE
from .models import Issue
from .utils import parse_frontmatter


def gather_issues(repo_root: Path) -> list[Issue]:
    issues: list[Issue] = []
    wiki_dir = repo_root / "wiki"
    required_root = ["index.md", "hot.md", "log.md"]
    required_keys = {
        "domain",
        "type",
        "source_count",
        "status",
        "visibility",
        "tags",
        "related",
        "created",
        "updated",
    }

    for name in required_root:
        if not (repo_root / name).exists():
            issues.append(Issue("error", name, "missing required llm-wiki root file"))

    if not wiki_dir.exists():
        issues.append(Issue("error", "wiki", "wiki directory is missing"))
        return issues

    wiki_files = sorted(wiki_dir.rglob("*.md"))
    slugs = {f.stem for f in wiki_files}

    for path in wiki_files:
        rel_path = str(path.relative_to(repo_root))
        if not SNAKE_CASE_RE.match(path.stem):
            issues.append(Issue("warn", rel_path, "filename is not snake_case"))

        text = path.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(text)
        if frontmatter is None:
            issues.append(Issue("warn", rel_path, "missing or invalid YAML frontmatter"))
        else:
            missing = sorted(k for k in required_keys if k not in frontmatter)
            if missing:
                issues.append(
                    Issue(
                        "warn",
                        rel_path,
                        "missing frontmatter keys: " + ", ".join(missing),
                    )
                )

        for link in WIKILINK_RE.findall(text):
            target = link.split("/")[-1].strip()
            if not target:
                continue
            if target not in slugs:
                issues.append(Issue("warn", rel_path, f"dead wikilink: [[{link}]]"))

    return issues


def print_report(issues: list[Issue]) -> None:
    if not issues:
        print("wiki_guard: no issues found")
        return
    print(f"wiki_guard: found {len(issues)} issue(s)")
    for issue in issues:
        print(f"[{issue.level}] {issue.path}: {issue.message}")
