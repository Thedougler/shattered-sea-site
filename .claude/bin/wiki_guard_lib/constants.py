from __future__ import annotations

import re

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")
SNAKE_CASE_RE = re.compile(r"^[a-z0-9_]+$")
INDEX_ROW_RE = re.compile(r"^\|\s*\[\[([a-z0-9_]+)\]\]\s*\|\s*(.*?)\s*\|")
PROPER_NOUN_RE = re.compile(r"\b[A-Z][A-Za-z]+(?:[ \t]+[A-Z][A-Za-z]+){0,2}\b")
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

# Terms that frequently appear as campaign/meta scaffolding but should not drive
# entity gap creation recommendations.
ENTITY_GAP_STOP_TERMS = STOP_TERMS | {
    "Campaign",
    "Timeline",
    "History",
    "Day",
    "Days",
    "Session",
    "Sessions",
    "Sea",
    "Shattered",
}

# Sentence-start artifacts that are not useful gap candidates.
GAP_NOISE_WORDS = {
    "In",
    "On",
    "At",
    "Aboard",
    "Of",
    "To",
    "For",
    "And",
    "But",
    "Or",
    "A",
    "An",
    "As",
    "By",
    "From",
    "Into",
    "Over",
    "Under",
    "When",
    "Then",
    "Than",
    "This",
    "That",
    "These",
    "Those",
    "Their",
    "She",
    "Its",
    "His",
    "Her",
    "Use",
    "One",
    "All",
    "Home",
    "Event",
    "Date",
    "Template",
    "Season",
    "Tier",
    "Claude",
    "Five",
    "Rescued",
    "Significance",
    "Connections",
    "Three",
    "Whether",
}
