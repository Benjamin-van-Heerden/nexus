---
title: Contact CRUD commands
status: completed
created_at: '2026-03-31T09:14:35.148991'
updated_at: '2026-03-31T10:57:07.065018'
completed_at: '2026-03-31T10:57:07.065012'
---
Create src/commands/management/contact.py with typer app:

Commands:
- contact new 'name' — create TOML in management/contacts/<slug>.toml. Options: --phone, --email, --birthday (date string YYYY-MM-DD), --relationship. After creation, if birthday is set, print a note that birthday reminders will appear in onboard/upcoming.
- contact list — list all contacts (name, relationship, birthday if set)
- contact show <slug> — show full contact details including info section
- contact edit <slug> — update fields. Options: --phone, --email, --birthday, --relationship, --info-key and --info-value (add/update info dict entry), --remove-info-key
- contact delete <slug> — confirm, then delete contact TOML

Contact slugs are resolved by scanning management/contacts/ directory (no index needed for contacts — there won't be thousands).

## Completion Notes

Created src/commands/management/contact.py with 5 commands: new (--phone, --email, --birthday, --relationship), list (shows name, relationship, birthday), show (full details + info dict), edit (all fields + --info-key/--info-value/--remove-info-key), delete (with confirmation). Contacts resolved by scanning contacts/ directory, no index needed.