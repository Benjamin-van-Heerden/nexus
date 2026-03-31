---
title: Utility module
status: completed
created_at: '2026-03-31T09:12:05.411522'
updated_at: '2026-03-31T10:00:29.364713'
completed_at: '2026-03-31T10:00:29.364707'
---
Create src/utils/management.py with:

- TOML I/O helpers: load_task(path), save_task(path, TaskConfig), load_contact(path), save_contact(path, ContactConfig), load_index(), save_index(). Use tomllib for reading, tomli_w for writing (with multiline_strings=True). Use model_dump(mode='json', exclude_none=True) for serialization.

- Index management: add_to_index(entry), remove_from_index(slug), update_index_entry(slug, **fields). Index lives at management/index.toml.

- Slug generation: slugify(name) — lowercase, spaces/special chars to underscores.

- Slug resolution: resolve_slug(slug_or_name) — check index, return IndexEntry or error if ambiguous/not found. Should accept exact slug or name (resolved to slug).

- Path helpers: get_management_dir(), get_tasks_dir(), get_completed_dir(), get_contacts_dir(), get_sync_dir(). Follow pattern from src/utils/paths.py (use get_project_root()).

- Cron helpers: parse_recurrence(cron_3field) — parse 'dom month dow' format. next_occurrence(cron_3field, after=datetime) — calculate next occurrence from pattern. is_due_in_window(cron_3field, days=14) — check if next occurrence is within window.

- Task tree helpers: get_subtasks(slug) — read index to find children. get_task_tree(slug) — recursive tree of task + all descendants. move_to_completed(slug) — move task.toml and subtask dir to completed/, remove from index recursively.

## Completion Notes

Created src/utils/management.py with TOML I/O (load/save for tasks, contacts, index), index management (add/remove/update entries), slug helpers (slugify, resolve_slug, resolve_contact_slug), cron helpers (parse_recurrence, next_occurrence, is_due_in_window — custom 3-field parser), task tree helpers (get_subtasks, get_task_tree, move_to_completed). Added get_management_dir() to src/utils/paths.py. All follows existing patterns from learn.py.