"""Archive system utilities.

Handles TOML/YAML I/O, frontmatter parsing, slug helpers, mention
extraction, and the QMD subprocess wrapper for the archive system.
"""

import json
import re
import subprocess
import tomllib
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator

import tomli_w
import yaml

from src.models.archive.archive import ArchiveConfig, ArchiveState
from src.models.archive.doc import DocFrontmatter
from src.models.archive.index import IndexFile, IndexTopicEntry
from src.models.archive.output import OutputFrontmatter
from src.models.archive.topic import TopicConfig, TopicMember
from src.models.archive.work import WorkItem, WorkQueue
from src.utils.paths import get_archive_dir

# -- Path getters --


def get_wiki_dir() -> Path:
    return get_archive_dir() / "wiki"


def get_topics_dir() -> Path:
    return get_archive_dir() / "topics"


def get_raw_dir() -> Path:
    return get_archive_dir() / "raw"


def get_outputs_dir() -> Path:
    return get_archive_dir() / "outputs"


def get_archive_config_path() -> Path:
    return get_archive_dir() / "archive.toml"


def get_archive_state_path() -> Path:
    return get_archive_dir() / "state.toml"


def get_work_path() -> Path:
    return get_archive_dir() / "work.toml"


def get_index_path() -> Path:
    return get_archive_dir() / "index.toml"


def get_agent_instructions_path() -> Path:
    return Path(__file__).resolve().parent.parent / "commands" / "archive" / "agent_instructions.md"


# -- Atomic write helper --


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(path)


def _atomic_write_text(path: Path, text: str) -> None:
    _atomic_write_bytes(path, text.encode("utf-8"))


# -- TOML I/O --


def _load_toml(path: Path) -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)


def _dump_toml_bytes(data: dict) -> bytes:
    return tomli_w.dumps(data, multiline_strings=True).encode("utf-8")


def _save_toml(path: Path, data: dict) -> None:
    _atomic_write_bytes(path, _dump_toml_bytes(data))


# -- Config / state --


def load_archive_config() -> ArchiveConfig:
    path = get_archive_config_path()
    if not path.exists() or path.stat().st_size == 0:
        return ArchiveConfig()
    return ArchiveConfig(**_load_toml(path))


def save_archive_config(config: ArchiveConfig) -> None:
    _save_toml(get_archive_config_path(), config.model_dump(mode="json", exclude_none=True))


def load_archive_state() -> ArchiveState:
    path = get_archive_state_path()
    if not path.exists() or path.stat().st_size == 0:
        return ArchiveState()
    return ArchiveState(**_load_toml(path))


def save_archive_state(state: ArchiveState) -> None:
    _save_toml(get_archive_state_path(), state.model_dump(mode="json", exclude_none=True))


# -- Work queue --


def load_work_queue() -> WorkQueue:
    path = get_work_path()
    if not path.exists() or path.stat().st_size == 0:
        return WorkQueue()
    return WorkQueue(**_load_toml(path))


def save_work_queue(queue: WorkQueue) -> None:
    _save_toml(get_work_path(), queue.model_dump(mode="json", exclude_none=True))


def enqueue_work(item: WorkItem) -> None:
    queue = load_work_queue()
    queue.items.append(item)
    save_work_queue(queue)


# -- Topics --


def get_topic_path(slug: str) -> Path:
    return get_topics_dir() / f"{slug}.toml"


def load_topic(slug: str) -> TopicConfig:
    return TopicConfig(**_load_toml(get_topic_path(slug)))


def save_topic(topic: TopicConfig) -> None:
    _save_toml(get_topic_path(topic.slug), topic.model_dump(mode="json", exclude_none=True))


def topic_exists(slug: str) -> bool:
    return get_topic_path(slug).is_file()


def list_all_topics() -> list[TopicConfig]:
    topics_dir = get_topics_dir()
    if not topics_dir.is_dir():
        return []
    out: list[TopicConfig] = []
    for path in sorted(topics_dir.glob("*.toml")):
        try:
            out.append(TopicConfig(**_load_toml(path)))
        except Exception:
            continue
    return out


def sync_topic_membership(
    doc_slug: str,
    new_topics: list[str],
    old_topics: list[str],
    hook_overrides: dict[str, str] | None = None,
) -> None:
    """Reconcile a doc's topic membership across all referenced topic files.

    For each topic in (new - old): add the doc to its [[docs]] list with empty
    hook (or the override if provided). For each topic in (old - new): remove
    the doc from its [[docs]] list. Existing hooks on no-op topics are
    preserved. Topics that don't exist on disk are skipped silently — caller
    is responsible for validation.
    """
    new_set = set(new_topics)
    old_set = set(old_topics)
    overrides = hook_overrides or {}

    for topic_slug in new_set - old_set:
        if not topic_exists(topic_slug):
            continue
        topic = load_topic(topic_slug)
        if not any(d.slug == doc_slug for d in topic.docs):
            topic.docs.append(
                TopicMember(slug=doc_slug, hook=overrides.get(topic_slug, ""))
            )
            save_topic(topic)

    for topic_slug in old_set - new_set:
        if not topic_exists(topic_slug):
            continue
        topic = load_topic(topic_slug)
        before = len(topic.docs)
        topic.docs = [d for d in topic.docs if d.slug != doc_slug]
        if len(topic.docs) != before:
            save_topic(topic)


def get_or_create_topic_member_hook(topic_slug: str, doc_slug: str) -> str:
    """Return the existing hook for a doc in a topic, or empty string."""
    if not topic_exists(topic_slug):
        return ""
    topic = load_topic(topic_slug)
    for d in topic.docs:
        if d.slug == doc_slug:
            return d.hook
    return ""


# -- Index --


def load_index() -> IndexFile | None:
    path = get_index_path()
    if not path.exists() or path.stat().st_size == 0:
        return None
    return IndexFile(**_load_toml(path))


def save_index(index: IndexFile) -> None:
    _save_toml(get_index_path(), index.model_dump(mode="json", exclude_none=True))


def regenerate_index() -> IndexFile:
    """Rebuild archive/index.toml from the current on-disk state.

    Walks topics/, wiki/, and outputs/. Computes topic doc-counts plus
    archive-wide totals: orphan/stale/broken_link/pending_output counts.
    """
    topics = list_all_topics()
    docs = list(list_all_docs_with_frontmatter())
    outputs = list(list_all_outputs_with_frontmatter())

    # Inbound reference index — for orphan detection
    inbound: dict[str, set[str]] = {}
    for slug, fm, body in docs:
        for link in fm.links:
            inbound.setdefault(link.slug, set()).add(slug)
        for m in fm.mentions:
            inbound.setdefault(m, set()).add(slug)

    # Counts
    config = load_archive_config()
    threshold = date.today() - timedelta(days=config.maintenance.staleness_days)

    orphan_count = 0
    stale_count = 0
    broken_link_count = 0
    for slug, fm, _body in docs:
        broken_link_count += len(fm.broken_links)
        no_topics = not fm.topics
        no_inbound = not inbound.get(slug)
        if no_topics or no_inbound:
            orphan_count += 1
        last = fm.last_maintained or fm.updated
        if last < threshold:
            stale_count += 1

    pending_outputs = sum(1 for _, fm, _ in outputs if fm.status == "pending_review")

    children_by_parent: dict[str, list[str]] = {}
    for t in topics:
        if t.parent:
            children_by_parent.setdefault(t.parent, []).append(t.slug)

    entries: list[IndexTopicEntry] = []
    for t in topics:
        summary_line = (t.summary or "").strip().splitlines()[0] if t.summary else ""
        entries.append(
            IndexTopicEntry(
                slug=t.slug,
                summary_line=summary_line,
                doc_count=len(t.docs),
                parent=t.parent,
                related=list(t.related),
                children=sorted(children_by_parent.get(t.slug, [])),
            )
        )

    index = IndexFile(
        generated=datetime.now(timezone.utc),
        doc_count=len(docs),
        topic_count=len(topics),
        pending_outputs=pending_outputs,
        orphan_count=orphan_count,
        stale_count=stale_count,
        broken_link_count=broken_link_count,
        topics=entries,
    )
    save_index(index)
    return index


# -- Graph computation primitives --


def compute_backlinks(target_slug: str) -> list[tuple[str, str]]:
    """Return [(source_slug, relation), ...] for every doc linking to target_slug."""
    out: list[tuple[str, str]] = []
    for slug, fm, _body in list_all_docs_with_frontmatter():
        if slug == target_slug:
            continue
        for link in fm.links:
            if link.slug == target_slug:
                out.append((slug, link.relation))
    return out


def compute_mentioned_by(target_slug: str) -> list[str]:
    """Return slugs of docs whose body or mentions list contains target_slug."""
    pattern = re.compile(r"\[\[" + re.escape(target_slug) + r"\]\]")
    out: list[str] = []
    for slug, fm, body in list_all_docs_with_frontmatter():
        if slug == target_slug:
            continue
        if target_slug in fm.mentions or pattern.search(body):
            out.append(slug)
    return out


def compute_topic_siblings(slug: str, limit_per_topic: int = 5) -> dict[str, list[str]]:
    """Map topic_slug -> sibling doc slugs (up to limit_per_topic, excluding slug itself)."""
    if not doc_exists(slug):
        return {}
    fm, _ = load_doc(slug)
    out: dict[str, list[str]] = {}
    for topic_slug in fm.topics:
        if not topic_exists(topic_slug):
            continue
        topic = load_topic(topic_slug)
        siblings = [d.slug for d in topic.docs if d.slug != slug][:limit_per_topic]
        out[topic_slug] = siblings
    return out


# -- Frontmatter parse / serialize --

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Split a markdown file with YAML frontmatter into (frontmatter_dict, body).

    Raises ValueError if the file does not start with a `---` block.
    """
    match = _FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError("File does not start with a YAML frontmatter block (---)")
    raw_yaml, body = match.group(1), match.group(2)
    data = yaml.safe_load(raw_yaml) or {}
    if not isinstance(data, dict):
        raise ValueError("Frontmatter must be a YAML mapping")
    return data, body


def serialize_doc(frontmatter: dict[str, Any], body: str) -> str:
    """Serialize a frontmatter dict + body into the wiki-doc string format."""
    yaml_text = yaml.safe_dump(
        frontmatter,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
    ).rstrip()
    body = body.lstrip("\n")
    return f"---\n{yaml_text}\n---\n\n{body}" if body else f"---\n{yaml_text}\n---\n"


# -- Wiki docs --


def get_doc_path(slug: str) -> Path:
    return get_wiki_dir() / f"{slug}.md"


def load_doc(slug: str) -> tuple[DocFrontmatter, str]:
    text = get_doc_path(slug).read_text(encoding="utf-8")
    fm_dict, body = parse_frontmatter(text)
    return DocFrontmatter(**fm_dict), body


def save_doc(frontmatter: DocFrontmatter, body: str) -> None:
    fm_dict = frontmatter.model_dump(mode="json", exclude_none=True)
    text = serialize_doc(fm_dict, body)
    _atomic_write_text(get_doc_path(frontmatter.slug), text)


def doc_exists(slug: str) -> bool:
    return get_doc_path(slug).is_file()


def list_all_doc_slugs() -> set[str]:
    wiki_dir = get_wiki_dir()
    if not wiki_dir.is_dir():
        return set()
    return {p.stem for p in wiki_dir.glob("*.md")}


def list_all_docs_with_frontmatter() -> Iterator[tuple[str, DocFrontmatter, str]]:
    """Iterate (slug, frontmatter, body) over every wiki doc on disk."""
    wiki_dir = get_wiki_dir()
    if not wiki_dir.is_dir():
        return
    for path in sorted(wiki_dir.glob("*.md")):
        try:
            fm, body = load_doc(path.stem)
        except Exception:
            continue
        yield path.stem, fm, body


def list_all_outputs_with_frontmatter() -> Iterator[tuple[str, OutputFrontmatter, str]]:
    """Iterate (slug, frontmatter, body) over every output on disk."""
    out_dir = get_outputs_dir()
    if not out_dir.is_dir():
        return
    for path in sorted(out_dir.glob("*.md")):
        try:
            fm, body = load_output(path.stem)
        except Exception:
            continue
        yield path.stem, fm, body


def mark_pending_qmd_update() -> None:
    """Set state.toml's pending_qmd_update flag. Phase 5 turns this into an actual qmd update."""
    state = load_archive_state()
    if not state.pending_qmd_update:
        state.pending_qmd_update = True
        save_archive_state(state)


# -- Outputs --


def get_output_path(slug: str) -> Path:
    return get_outputs_dir() / f"{slug}.md"


def load_output(slug: str) -> tuple[OutputFrontmatter, str]:
    text = get_output_path(slug).read_text(encoding="utf-8")
    fm_dict, body = parse_frontmatter(text)
    return OutputFrontmatter(**fm_dict), body


def save_output(frontmatter: OutputFrontmatter, body: str) -> None:
    fm_dict = frontmatter.model_dump(mode="json", exclude_none=True)
    text = serialize_doc(fm_dict, body)
    _atomic_write_text(get_output_path(frontmatter.slug), text)


# -- Slug helpers --

_SLUG_VALID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def slugify(title: str) -> str:
    """Convert a title to a kebab-case slug suitable for archive identifiers."""
    s = title.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s


def is_valid_slug(slug: str) -> bool:
    return bool(_SLUG_VALID_RE.match(slug))


def ensure_unique_slug(candidate: str, existing: set[str]) -> str:
    """Return candidate if unused, otherwise append -2, -3, ... until unique."""
    if candidate not in existing:
        return candidate
    i = 2
    while f"{candidate}-{i}" in existing:
        i += 1
    return f"{candidate}-{i}"


# -- Mention extraction --

_MENTION_RE = re.compile(r"\[\[([a-z0-9]+(?:-[a-z0-9]+)*)\]\]")


def extract_mentions(body: str) -> list[str]:
    """Extract unique [[slug]] mentions from a doc body, preserving first-seen order."""
    seen: list[str] = []
    seen_set: set[str] = set()
    for m in _MENTION_RE.finditer(body):
        slug = m.group(1)
        if slug not in seen_set:
            seen.append(slug)
            seen_set.add(slug)
    return seen


# -- QMD wrapper --


class QmdNotInstalledError(RuntimeError):
    """Raised when the qmd binary is not available on PATH."""


_QMD_INSTALL_HINT = (
    "qmd is not installed. Install it with one of:\n"
    "  npm install -g @tobilu/qmd\n"
    "  bun install -g @tobilu/qmd"
)


def qmd_check() -> str:
    """Return qmd's version string. Raises QmdNotInstalledError if not on PATH."""
    try:
        result = subprocess.run(
            ["qmd", "--version"], capture_output=True, text=True, check=False
        )
    except FileNotFoundError as e:
        raise QmdNotInstalledError(_QMD_INSTALL_HINT) from e
    if result.returncode != 0:
        raise QmdNotInstalledError(
            f"qmd --version exited {result.returncode}: {result.stderr.strip()}"
        )
    return result.stdout.strip()


def qmd_run(args: list[str], parse_json: bool = False) -> Any:
    """Run a qmd subcommand. Returns parsed JSON if requested, else stdout string.

    Raises QmdNotInstalledError if qmd is missing; RuntimeError on non-zero exit.
    """
    try:
        result = subprocess.run(
            ["qmd", *args], capture_output=True, text=True, check=False
        )
    except FileNotFoundError as e:
        raise QmdNotInstalledError(_QMD_INSTALL_HINT) from e
    if result.returncode != 0:
        raise RuntimeError(
            f"qmd {' '.join(args)} exited {result.returncode}: {result.stderr.strip()}"
        )
    if parse_json:
        return json.loads(result.stdout) if result.stdout.strip() else None
    return result.stdout
