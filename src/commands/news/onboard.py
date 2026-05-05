"""Onboard and refresh commands for the news system.

`onboard` runs the full daily pipeline: RSS + xAI sourcing + LLM synthesis,
saves a digest, updates tracked stories, prints the newspaper.

`refresh` is a lighter check-in: only fresh X searches, a quick LLM pass to
surface what's new since the morning digest, no record overwrite.
"""

from datetime import date
from pathlib import Path

import typer

from src.models.news.digest import DailyDigest, StoryCluster
from src.utils.news import (
    apply_tracked_story_updates,
    fetch_all_feeds_sync,
    list_tracked_stories,
    load_daily_digest,
    load_news_config,
    load_recent_records,
    save_daily_digest,
    synthesize_breaking,
    synthesize_newspaper,
    web_search_gaps,
    x_search_global,
    x_search_local,
)
from src.utils.pause import check_pause


# -- Display helpers --


def _print_cluster(cluster: StoryCluster) -> None:
    tracked_marker = (
        f"  [tracking: {cluster.tracked_story}]" if cluster.tracked_story else ""
    )
    sources_marker = (
        f"  ({cluster.sources_count} sources)" if cluster.sources_count > 1 else ""
    )
    print(f"  ▸ {cluster.headline}{sources_marker}{tracked_marker}")
    if cluster.source_names:
        print(f"      Sources: {', '.join(cluster.source_names)}")
    print(f"      {cluster.summary}")
    if cluster.perspectives:
        for p in cluster.perspectives:
            print(f"      - {p.lean} ({p.source}): {p.summary}")


def _print_categorized_clusters(
    clusters: list[StoryCluster], category_order: list[str]
) -> None:
    by_category: dict[str, list[StoryCluster]] = {}
    for c in clusters:
        by_category.setdefault(c.category, []).append(c)

    seen: set[str] = set()
    for cat in category_order:
        bucket = by_category.get(cat, [])
        if not bucket:
            continue
        seen.add(cat)
        print("-" * 60)
        print(cat.upper())
        print("-" * 60)
        for c in bucket:
            _print_cluster(c)
        print()

    # Any unexpected categories the LLM emitted
    for cat, bucket in by_category.items():
        if cat in seen:
            continue
        print("-" * 60)
        print(cat.upper())
        print("-" * 60)
        for c in bucket:
            _print_cluster(c)
        print()


def _print_x_section(title: str, content: str) -> None:
    if not content.strip():
        return
    print("-" * 60)
    print(title)
    print("-" * 60)
    print(content.strip())
    print()


def _print_tracked_updates(digest: DailyDigest) -> None:
    if not digest.tracked_story_updates:
        return
    print("-" * 60)
    print("TRACKED STORIES")
    print("-" * 60)
    for update in digest.tracked_story_updates:
        print(f"  • {update.slug}")
        print(f"      {update.headline}")
        print(f"      → {update.development}")
    print()


def _print_agent_instructions() -> None:
    instructions_path = Path(__file__).parent / "agent_instructions.md"
    if not instructions_path.exists():
        return
    print("-" * 60)
    print("AGENT INSTRUCTIONS")
    print("-" * 60)
    print(instructions_path.read_text().strip())
    print()


def _print_action_required() -> None:
    print("=" * 60)
    print("ACTION REQUIRED")
    print("=" * 60)
    print("Read the newspaper above and present it to Benjamin NOW.")
    print("Do not silently process this output — the user is waiting.")
    print("=" * 60)
    print()


def _run_full_daily_pipeline(command_name: str, prefix_message: str | None = None) -> None:
    today = date.today()
    config = load_news_config()
    recent_records = load_recent_records(n=config.history_days)
    tracked_stories = list_tracked_stories(active_only=True)

    print("=" * 60)
    print(command_name)
    print("=" * 60)
    print(f"Date: {today.strftime('%A, %B %d, %Y')}")
    if prefix_message:
        print(prefix_message)
    print(f"Sources: {len(config.sources)} RSS feeds configured")
    print(f"Tracked: {len(tracked_stories)} active stories")
    print(f"History: last {len(recent_records)} record(s) loaded for continuity")
    print()

    print("Fetching RSS feeds…")
    rss_headlines = fetch_all_feeds_sync(
        config.sources,
        max_entries_per_source=config.max_entries_per_source,
        max_total_entries=config.max_total_entries,
        max_entry_age_hours=config.max_entry_age_hours,
    )
    print(f"  → {len(rss_headlines)} headlines")
    print()

    print("Searching X for global discourse…")
    x_global = x_search_global(
        model=config.xai_model, tracked_stories=tracked_stories
    )
    print(f"  → {len(x_global)} chars")
    print()

    print("Searching X for South African discourse…")
    x_local = x_search_local(
        model=config.xai_model, tracked_stories=tracked_stories
    )
    print(f"  → {len(x_local)} chars")
    print()

    print("Web search for under-covered stories…")
    web_results = web_search_gaps(
        model=config.xai_model, tracked_stories=tracked_stories
    )
    print(f"  → {len(web_results)} chars")
    print()

    print("Synthesizing newspaper…")
    digest = synthesize_newspaper(
        rss_headlines=rss_headlines,
        x_global=x_global,
        x_local=x_local,
        web_results=web_results,
        tracked_stories=tracked_stories,
        recent_records=recent_records,
        config=config,
        today=today,
    )
    print(f"  → {len(digest.story_clusters)} clusters")
    print()

    save_daily_digest(digest)
    n_updated = apply_tracked_story_updates(digest.tracked_story_updates, today=today)
    if n_updated:
        print(f"Updated {n_updated} tracked story(ies).")
        print()

    print("=" * 60)
    print(f"DAILY NEWSPAPER — {today.strftime('%A, %B %d, %Y')}")
    print("=" * 60)
    print()

    _print_tracked_updates(digest)
    _print_categorized_clusters(digest.story_clusters, config.categories)
    _print_x_section("TRENDING ON X — GLOBAL", digest.x_trending_global)
    _print_x_section("TRENDING ON X — SOUTH AFRICA", digest.x_trending_sa)

    _print_agent_instructions()
    _print_action_required()


# -- Commands --


def onboard():
    """Generate today's full newspaper: RSS + xAI sourcing + synthesis."""
    paused = check_pause("news")
    if paused:
        print(
            f"Nexus news is paused. Reason: {paused.reason or 'no reason provided'}. "
            f"Will resume on {paused.resume_date}. Nothing further to do."
        )
        raise typer.Exit(0)

    _run_full_daily_pipeline("NEXUS NEWS ONBOARD")


def refresh():
    """Lighter pass: fresh X discourse only, surface what's new since onboard."""
    paused = check_pause("news")
    if paused:
        print(
            f"Nexus news is paused. Reason: {paused.reason or 'no reason provided'}. "
            f"Will resume on {paused.resume_date}. Nothing further to do."
        )
        raise typer.Exit(0)

    today = date.today()
    config = load_news_config()
    today_record = load_daily_digest(today)
    tracked_stories = list_tracked_stories(active_only=True)

    if today_record is None:
        _run_full_daily_pipeline(
            "NEXUS NEWS REFRESH",
            prefix_message=(
                "No daily digest exists for today. Running the full daily "
                "newspaper pipeline now."
            ),
        )
        return

    print("=" * 60)
    print("NEXUS NEWS REFRESH")
    print("=" * 60)
    print(f"Date: {today.strftime('%A, %B %d, %Y')}")
    print(
        f"Morning digest: {len(today_record.story_clusters)} clusters, "
        f"generated {today_record.generated_at}"
    )
    print(f"Tracked: {len(tracked_stories)} active stories")
    print()

    print("Searching X for fresh global discourse…")
    x_global = x_search_global(
        model=config.xai_model, tracked_stories=tracked_stories
    )
    print(f"  → {len(x_global)} chars")
    print()

    print("Searching X for fresh South African discourse…")
    x_local = x_search_local(
        model=config.xai_model, tracked_stories=tracked_stories
    )
    print(f"  → {len(x_local)} chars")
    print()

    print("Filtering for breaking and developing stories…")
    breaking = synthesize_breaking(
        today_record=today_record,
        tracked_stories=tracked_stories,
        x_global=x_global,
        x_local=x_local,
        config=config,
    )
    print(f"  → {len(breaking.new_clusters)} new clusters")
    print()

    n_updated = apply_tracked_story_updates(breaking.tracked_story_updates, today=today)
    if n_updated:
        print(f"Updated {n_updated} tracked story(ies).")
        print()

    print("=" * 60)
    print(f"REFRESH — {today.strftime('%A, %B %d, %Y')}")
    print("=" * 60)
    print()

    if breaking.summary.strip():
        print("-" * 60)
        print("WHAT CHANGED SINCE MORNING")
        print("-" * 60)
        print(breaking.summary.strip())
        print()

    if breaking.new_clusters:
        _print_categorized_clusters(breaking.new_clusters, config.categories)
    elif not breaking.summary.strip():
        print("Nothing new or breaking since the morning digest.")
        print()

    if breaking.tracked_story_updates:
        print("-" * 60)
        print("TRACKED STORY DEVELOPMENTS")
        print("-" * 60)
        for update in breaking.tracked_story_updates:
            print(f"  • {update.slug}")
            print(f"      {update.headline}")
            print(f"      → {update.development}")
        print()

    print("-" * 60)
    print("REFRESH INSTRUCTIONS")
    print("-" * 60)
    print("Relay only the new / breaking material above to Benjamin.")
    print("Lead with tracked-story developments, then any new clusters.")
    print("If nothing new, say so briefly. Do not restate the morning digest.")
    print()

    print("=" * 60)
    print("ACTION REQUIRED")
    print("=" * 60)
    print("Send the breaking material to Benjamin NOW.")
    print("=" * 60)
    print()
