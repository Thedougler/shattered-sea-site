from __future__ import annotations

from dataclasses import dataclass


@dataclass
class OrphanFinding:
    slug: str
    inbound_count: int
    suggested_links_from: list[str]


@dataclass
class DeadLinkFinding:
    target: str
    source_pages: list[str]
    count: int
    classification: str
    likely_meant: str | None


@dataclass
class IndexAuditFinding:
    index_ghosts: list[str]
    wiki_ghosts: list[str]
    empty_summaries: list[str]


@dataclass
class StaleFinding:
    slug: str
    last_updated: str
    source_count: int
    ingestions_since_update: int
    reason: str


@dataclass
class ContradictionFinding:
    slug: str
    open_since: str
    open_days: int
    conflict: str


@dataclass
class EntityGapFinding:
    term: str
    mentions: int
    pages: list[str]
    priority: str


@dataclass
class LintResults:
    pages_audited: int
    index_entries: int
    ingestion_events: int
    orphans: list[OrphanFinding]
    dead_links: list[DeadLinkFinding]
    index: IndexAuditFinding
    stale: list[StaleFinding]
    contradictions: list[ContradictionFinding]
    gaps: list[EntityGapFinding]


@dataclass
class DeadLinkAggregate:
    count: int
    sources: set[str]


@dataclass
class Issue:
    level: str
    path: str
    message: str


@dataclass
class IngestSourceStatus:
    raw_path: str
    status: str
    size_bytes: int
    content_hash: str
    ingested_at: str | None
    pages_created: int
    pages_updated: int


@dataclass
class QueryPrepCandidate:
    slug: str
    rel_path: str
    score: int
    match_reasons: list[str]
    summary: str
    status: str
    visibility: str
    tags: list[str]
    aliases: list[str]
    outbound_links: list[str]
    snippets: list[str]


@dataclass
class QueryPrepResult:
    question: str
    query_type: str
    mode: str
    filtered: bool
    top_k: int
    primary: list[QueryPrepCandidate]
    secondary: list[QueryPrepCandidate]
    excluded_internal_count: int


@dataclass
class StatusSourceRecord:
    source_path: str
    status: str
    source_type: str
    size_bytes: int
    modified_at: str
    last_ingested: str | None
    last_modified: str | None
    project: str | None


@dataclass
class ProjectDelta:
    project: str
    conversations_total: int
    memory_files_total: int
    new_conversations: int
    updated_memory_files: int
    is_new_project: bool


@dataclass
class VisibilityTally:
    public: int
    internal: int
    pii: int
    total_pages: int


@dataclass
class WikiStatusReport:
    total_wiki_pages: int
    wiki_categories: int
    visibility: VisibilityTally
    total_sources_ingested: int
    projects_tracked: int
    last_ingest: str | None
    sources: list[StatusSourceRecord]
    deleted_sources: list[str]
    project_deltas: list[ProjectDelta]
    recommendation: str


@dataclass
class SynthesisCandidate:
    left_slug: str
    right_slug: str
    title: str
    score: int
    cooccurrence_count: int
    shared_by_pages: list[str]
    cross_domain: bool
    shared_tags: list[str]
    hub_involved: bool
    contradiction_signal: bool


@dataclass
class SynthesisReport:
    pages_scanned: int
    candidate_pairs_scanned: int
    covered_pairs: int
    topic_filter: str | None
    top_candidates: list[SynthesisCandidate]
    skipped_candidates: list[SynthesisCandidate]
