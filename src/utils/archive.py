"""Archive system utilities.

Handles TOML/YAML I/O, frontmatter parsing, slug helpers, mention
extraction, and the QMD subprocess wrapper for the archive system.
"""

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import tomllib
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import urlparse

import httpx
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


def get_raw_markdown_path(content_hash: str) -> Path:
    return get_raw_dir() / f"{content_hash}.md"


def get_raw_sidecar_path(content_hash: str) -> Path:
    return get_raw_dir() / f"{content_hash}.toml"


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


# -- Raw ingestion helpers --

_MARKDOWN_SOURCE_ERROR = (
    "Only markdown sources supported for v1; PDFs/HTML belong in raw/unprocessed/ "
    "(future spec)."
)


def hash_file(path: Path) -> str:
    """Return the first 12 chars of the SHA256 hash for a file's bytes."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()[:12]


def fetch_url_to_temp(url: str) -> Path:
    """Fetch a markdown URL to a temp .md file and return its path."""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("URL must start with http:// or https://")

    response = httpx.get(url, follow_redirects=True, timeout=30.0)
    response.raise_for_status()

    content_type = response.headers.get("content-type", "").split(";")[0].strip().lower()
    path_suffix = Path(parsed.path).suffix.lower()
    markdown_content_types = {"text/markdown", "text/x-markdown", "text/plain"}
    if content_type == "text/html" or (
        content_type not in markdown_content_types and path_suffix != ".md"
    ):
        raise ValueError(_MARKDOWN_SOURCE_ERROR)

    with tempfile.NamedTemporaryFile("wb", suffix=".md", delete=False) as tmp:
        tmp.write(response.content)
        return Path(tmp.name)


def read_first_h1(markdown_text: str) -> str | None:
    """Return the first markdown H1 title, if present."""
    for line in markdown_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# ") and stripped[2:].strip():
            return stripped[2:].strip()
    return None


_EXCERPT_STOPWORDS = {"a", "an", "and", "of", "the", "to", "in", "across"}


def extract_excerpt(markdown_text: str, word_count: int = 500) -> str:
    """Return the first word_count plain words from markdown text."""
    words = [
        word
        for word in re.findall(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*", markdown_text)
        if word.lower() not in _EXCERPT_STOPWORDS
    ]
    return " ".join(words[:word_count])


def save_raw(
    source_path: Path,
    content_hash: str,
    original_path: str | None = None,
) -> tuple[Path, Path]:
    """Copy source_path into raw/<hash>.md and write raw/<hash>.toml metadata."""
    raw_path = get_raw_markdown_path(content_hash)
    sidecar_path = get_raw_sidecar_path(content_hash)
    raw_path.parent.mkdir(parents=True, exist_ok=True)

    tmp_path = raw_path.with_suffix(".md.tmp")
    shutil.copyfile(source_path, tmp_path)
    tmp_path.replace(raw_path)

    data = source_path.read_bytes()
    text = data.decode("utf-8", errors="replace")
    metadata = {
        "hash": content_hash,
        "filename": raw_path.name,
        "original_path": original_path or str(source_path),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "title_guess": read_first_h1(text) or "",
        "byte_size": len(data),
        "line_count": len(text.splitlines()),
    }
    _save_toml(sidecar_path, metadata)
    return raw_path, sidecar_path


_KEYWORD_STOPWORDS = {
    "about",
    "after",
    "again",
    "also",
    "because",
    "before",
    "between",
    "from",
    "have",
    "into",
    "more",
    "over",
    "such",
    "that",
    "their",
    "then",
    "there",
    "these",
    "this",
    "through",
    "with",
    "without",
}


def _keywords(text: str) -> set[str]:
    return {
        word
        for word in re.findall(r"[a-z0-9]+", text.lower())
        if len(word) >= 4 and word not in _KEYWORD_STOPWORDS
    }


def find_candidate_topics_by_keywords(text: str) -> list[TopicConfig]:
    """Rank topics by simple keyword overlap against title + summary."""
    query_words = _keywords(text)
    if not query_words:
        return []

    scored: list[tuple[int, str, TopicConfig]] = []
    for topic in list_all_topics():
        topic_words = _keywords(f"{topic.title} {topic.summary}")
        score = len(query_words & topic_words)
        if score:
            scored.append((score, topic.slug, topic))

    scored.sort(key=lambda item: (-item[0], item[1]))
    return [topic for _score, _slug, topic in scored]


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


def mark_work_item_resolved(kind: str, slug: str) -> None:
    """Remove persisted work items matching kind + slug."""
    queue = load_work_queue()
    queue.items = [
        item for item in queue.items if not (item.kind == kind and item.slug == slug)
    ]
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

    inbound = _inbound_ref_index(docs)

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


def _inbound_ref_index(
    docs: list[tuple[str, DocFrontmatter, str]] | None = None,
) -> dict[str, set[str]]:
    """Map target slug -> source slugs for links and mentions."""
    docs = docs if docs is not None else list(list_all_docs_with_frontmatter())
    inbound: dict[str, set[str]] = {}
    for slug, fm, _body in docs:
        for link in fm.links:
            inbound.setdefault(link.slug, set()).add(slug)
        for mention in fm.mentions:
            inbound.setdefault(mention, set()).add(slug)
    return inbound


def compute_orphans() -> list[str]:
    """Return doc slugs with no topics or no inbound links/mentions."""
    docs = list(list_all_docs_with_frontmatter())
    inbound = _inbound_ref_index(docs)
    out: list[str] = []
    for slug, fm, _body in docs:
        if not fm.topics or not inbound.get(slug):
            out.append(slug)
    return sorted(out)


def compute_stales(staleness_days: int) -> list[str]:
    """Return stale doc slugs, oldest maintained first."""
    threshold = date.today() - timedelta(days=staleness_days)
    stale: list[tuple[date, str]] = []
    for slug, fm, _body in list_all_docs_with_frontmatter():
        last = fm.last_maintained or fm.updated
        if last < threshold:
            stale.append((last, slug))
    return [slug for _last, slug in sorted(stale)]


def compute_contradictions() -> list[tuple[str, str]]:
    """Return best-effort contradiction candidates.

    v1 keeps this conservative. QMD-backed contradiction discovery is surfaced
    as manual maintenance guidance rather than automated flags.
    """
    return []


def get_topic_member_freshness(topic_slug: str) -> bool:
    """Return True if a topic likely needs summary/member freshness review."""
    if not topic_exists(topic_slug):
        return False
    topic = load_topic(topic_slug)
    if topic.last_maintained is None:
        return True
    for member in topic.docs:
        if not doc_exists(member.slug):
            return True
        try:
            fm, _body = load_doc(member.slug)
        except Exception:
            return True
        if fm.updated > topic.last_maintained:
            return True
    return False


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


def output_exists(slug: str) -> bool:
    return get_output_path(slug).is_file()


def load_output(slug: str) -> tuple[OutputFrontmatter, str]:
    text = get_output_path(slug).read_text(encoding="utf-8")
    fm_dict, body = parse_frontmatter(text)
    return OutputFrontmatter(**fm_dict), body


def save_output(frontmatter: OutputFrontmatter, body: str) -> None:
    fm_dict = frontmatter.model_dump(mode="json", exclude_none=True)
    text = serialize_doc(fm_dict, body)
    _atomic_write_text(get_output_path(frontmatter.slug), text)


def list_all_outputs(
    status_filter: str | None = None,
) -> list[OutputFrontmatter]:
    outputs: list[OutputFrontmatter] = []
    for _slug, fm, _body in list_all_outputs_with_frontmatter():
        if status_filter is None or fm.status == status_filter:
            outputs.append(fm)
    return outputs


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


def _qmd_unwrap_hits(payload: Any) -> list[dict]:
    """Coerce qmd JSON output to a list of hit dicts.

    qmd may return either a bare list of hits or a dict with a 'results' /
    'hits' key. Be defensive — third-party tools change shapes.
    """
    if payload is None:
        return []
    if isinstance(payload, list):
        return [h for h in payload if isinstance(h, dict)]
    if isinstance(payload, dict):
        for key in ("results", "hits", "data"):
            if key in payload and isinstance(payload[key], list):
                return [h for h in payload[key] if isinstance(h, dict)]
    return []


def qmd_search(q: str, n: int) -> list[dict]:
    """Raw qmd search hits. Reads collection name from archive.toml."""
    config = load_archive_config()
    payload = qmd_run(
        [
            "search",
            q,
            "-c",
            config.qmd.collection_name,
            "--json",
            "-n",
            str(n),
        ],
        parse_json=True,
    )
    return _qmd_unwrap_hits(payload)


def qmd_query(q: str, n: int) -> list[dict]:
    """Raw qmd query hits (BM25 + vector + reranker). Reads collection name from archive.toml."""
    config = load_archive_config()
    payload = qmd_run(
        [
            "query",
            q,
            "-c",
            config.qmd.collection_name,
            "--json",
            "-n",
            str(n),
        ],
        parse_json=True,
    )
    return _qmd_unwrap_hits(payload)


def qmd_path_to_slug(path: str | None) -> str | None:
    """Map a qmd hit's path to a wiki slug. Returns None if the slug can't be resolved."""
    if not path:
        return None
    p = Path(path)
    if p.suffix != ".md":
        return None
    slug = p.stem
    return slug if doc_exists(slug) else None


def qmd_update_collection() -> None:
    """Run `qmd update --collections <name>` and stamp state.toml's last_qmd_update.

    Clears state.toml's pending_qmd_update flag on success. Raises
    QmdNotInstalledError or RuntimeError on failure (caller decides how
    to handle).
    """
    config = load_archive_config()
    qmd_run(["update", "--collections", config.qmd.collection_name])
    state = load_archive_state()
    state.last_qmd_update = datetime.now(timezone.utc)
    state.pending_qmd_update = False
    save_archive_state(state)


def trigger_qmd_update_after_mutation(echo) -> None:
    """Run a qmd update after a mutation. Marks pending first; clears on success.

    Mutation commands MUST succeed even if qmd is unavailable, so this
    function always swallows qmd failures and just emits a warning via
    the supplied `echo` callable (typically typer.echo).
    """
    mark_pending_qmd_update()
    try:
        qmd_update_collection()
    except QmdNotInstalledError:
        echo(
            "Warning: qmd is not installed; skipped index update. "
            "Run `nexus archive reindex` after installing qmd."
        )
    except RuntimeError as e:
        echo(f"Warning: qmd update failed (state remains pending): {e}")
