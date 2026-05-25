---
title: End-to-end testing
status: completed
created_at: '2026-03-31T12:07:19.905157'
updated_at: '2026-03-31T15:52:47.215444'
completed_at: '2026-03-31T15:52:47.215435'
---
Test the full self-improvement system end-to-end using the nexus CLI. Fix any bugs found.

IMPORTANT CONTEXT: Run all commands via 'uv run python main.py self ...' from the project root. The system uses TOML files in the self/ directory. All dates should be real (today's date). Test with actual data that exercises the full flow.

**1. Reading flow:**
- Create a book: nexus self read new 'Test Book' --author 'Test Author' --section 'Chapter 1' --total '10 chapters'
- Verify TOML created in self/reading/active/test_book.toml
- List books, verify it appears
- Log a session: nexus self read log test_book --section 'Chapter 2-3' --summary 'Test summary of chapters' --takeaway 'Key insight from reading' --question 'First question' --question 'Second question'
- Verify session appended to TOML, current_section updated
- Show book, verify session details appear
- Complete book, verify moved to self/reading/completed/
- Run history, verify completed book appears

**2. Exercise flow:**
- Log a session: nexus self exercise log --type gym --description 'Bench press 4x8, rows 4x8' --intensity hard --duration 60
- Log another: nexus self exercise log --type run --description '5km easy' --intensity moderate --duration 30
- Run status, verify both sessions show and weekly count is correct
- Run history, verify sessions appear grouped by week

**3. Mental math flow:**
- Run generate, verify 5 problems printed with correct symbols
- Verify problem distribution roughly matches config weights (multiplication should appear more)
- Verify division always produces whole numbers
- Log a session: nexus self math log --time '3:20' --correct 5
- Run status, verify session appears with formatted time
- Run config, verify config displayed correctly

**4. Learning flow:**
- Log a session: nexus self learn log --notes 'Worked on Rust exercises'
- Run status, verify check-in appears
- Try logging again for today, verify overwrite warning
- Log a skip: nexus self learn log --skip
- Verify did_learn=false recorded

**5. Onboard (most critical test):**
- With the above test data in place, run nexus self onboard
- Verify ALL sections print:
  - System intro
  - Date context (correct day, week number, days remaining)
  - Reading status (active books, session counts, missing days)
  - Exercise status (sessions this week, missing days)
  - Math problems (5 problems generated inline)
  - Learning status (check-ins, streak)
  - Weekly overview
  - Agent instructions (full content of agent_instructions.md)
- Verify the output is self-contained: a cold-start agent reading ONLY this output would know what to do

**6. Edge cases:**
- Onboard with no data at all (fresh install) — should still work, show empty states
- Reading with no active books
- Exercise with no sessions this week
- Math with no logged sessions (trends should say 'no data')

## Completion Notes

Tested all flows: reading (new, list, show, log, complete, history), exercise (log, status, history), math (generate, log, status, config), learning (log, status), and onboard (with data and empty state). All passing. Cleaned up test data.