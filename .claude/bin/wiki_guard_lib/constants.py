from __future__ import annotations

import re

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")
SNAKE_CASE_RE = re.compile(r"^[a-z0-9_]+$")
INDEX_ROW_RE = re.compile(r"^\|\s*\[\[([a-z0-9_]+)\]\]\s*\|\s*(.*?)\s*\|")
PROPER_NOUN_RE = re.compile(r"\b[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,2}\b")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
INGEST_TIMESTAMP_RE = re.compile(r"\[(\d{4}-\d{2}-\d{2})T")
STOP_TERMS = {
    "Overview",
    "Relationships",
    "Sources",
    "Status",
    "Domain",
    "Type",
    "Summary",
    "The",
}
