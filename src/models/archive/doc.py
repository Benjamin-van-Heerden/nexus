"""Wiki document frontmatter model.

Maps to: archive/wiki/<slug>.md (YAML frontmatter block)
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel

DocStatus = Literal["draft", "stable", "stale", "contradicted"]

LinkRelation = Literal[
    "supersedes",
    "superseded_by",
    "depends_on",
    "extends",
    "contradicts",
    "spawned",
    "references",
    "part_of_series",
]


class LinkRef(BaseModel):
    slug: str
    relation: LinkRelation


class Provenance(BaseModel):
    ingested_from: Literal["add", "output_integration", "manual"] = "add"
    origin_outputs: list[str] = []


class DocFrontmatter(BaseModel):
    slug: str
    title: str
    summary: str
    created: date
    updated: date
    status: DocStatus = "draft"
    topics: list[str] = []
    links: list[LinkRef] = []
    mentions: list[str] = []
    sources: list[str] = []
    provenance: Provenance = Provenance()
    broken_links: list[str] = []
    last_maintained: date | None = None
    tags: list[str] = []
