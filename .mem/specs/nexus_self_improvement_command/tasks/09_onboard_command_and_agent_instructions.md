---
title: Onboard command and agent instructions
status: completed
created_at: '2026-03-31T12:02:59.307975'
updated_at: '2026-03-31T15:52:41.377762'
completed_at: '2026-03-31T15:52:41.377751'
---
Create the onboard command and agent instructions file. This is the most critical task in the spec — the onboard output is the ONLY interface between the nexus system and the AI agent.

IMPORTANT CONTEXT: An AI agent (OpenClaw) runs nexus self onboard once daily via cron. The agent has ZERO prior context — no memory of yesterday, no knowledge of the user, no understanding of nexus. The onboard output must be completely self-contained: what the system is, what state everything is in, what to do, and how to do it. If it is not in the onboard output, the agent does not know it.

**1. Create src/commands/self_improvement/onboard.py:**

The onboard function prints ALL of the following sections in order:

SECTION 1 - System Introduction:
Print a brief intro: 'You are Benjamins self-improvement coach. You interact via Telegram. You track 4 habits: reading, exercise, mental math, and learning. Below is your full context for today.'

SECTION 2 - Date Context:
Print: today's date, day of week name, ISO week number, which day of the week it is (e.g. 'Day 3 of 7'), days remaining including today. Example: 'Today: Wednesday, March 31, 2026 (Week 14) — Day 3 of 7, 5 days remaining'

SECTION 3 - Reading Status:
- Print goal text from habits.toml
- List each active book: name, author, current_section, total_sections, last session date (or 'never'), days since last session
- For each active book, print last session summary (if any)
- Flag books not touched in >3 days
- Count reading sessions this week (across all books), list which days
- List days this week with NO reading session
- If no active books, print 'No active books. Ask the user what theyre reading.'

SECTION 4 - Exercise Status:
- Print goal text from habits.toml
- List sessions this week: date, type, intensity, duration
- Count sessions, list missing days
- Print last session details if this week has any

SECTION 5 - Mental Math:
- Print goal text from habits.toml
- Call generate_problems() and print todays problems inline with header: 'Todays mental math problems:'
- If yesterday has a logged session: print time, accuracy
- Calculate and print: average time this week, average time last week, trend (improving/stable/declining)
- If no sessions this week yet, say so

SECTION 6 - Learning Status:
- Print goal text from habits.toml
- List check-ins this week: date, did_learn, notes (truncated)
- Calculate and print current streak (consecutive days with did_learn=True)
- List missing days this week

SECTION 7 - Weekly Overview:
- A compact summary table/list showing all 4 habits side by side: habit name, sessions this week, goal shorthand, status emoji (on track / behind / not started)

SECTION 8 - Agent Instructions:
- Read src/commands/self_improvement/agent_instructions.md and print its full contents
- Use pathlib to find the file relative to the onboard.py file location

**2. Create src/commands/self_improvement/agent_instructions.md:**

This file tells the cold-start agent everything it needs to know. It MUST cover:

IDENTITY AND ROLE:
- You are Benjamins daily self-improvement coach
- You wake up once per day, assess progress, send a Telegram message
- Be a coach: direct, supportive, motivating. Not a nag, not overly formal
- If the user is crushing it, celebrate. If theyre slipping, say so plainly

DAILY MESSAGE STRUCTURE:
- Open with the day and a quick vibe check based on the data
- For each habit: current week progress, whats missing, what needs to happen today
- Include todays math problems (from the onboard output above)
- Ask about reading: which book, what did they read today
- Close with motivation or accountability as appropriate

HANDLING USER RESPONSES:
- User will respond in natural language, potentially covering multiple habits at once
- Parse their response and log each habit separately using CLI commands

READING INTERACTION FLOW (most complex):
1. When user says they read something, DO NOT log immediately
2. Ask 2-3 comprehension questions about what they described reading
3. Discuss back and forth — this builds comprehension
4. After discussion, formulate a concise takeaway that captures what the user learned/understood
5. THEN log the session: nexus self read log <slug> --section 'section' --summary 'what was covered' --takeaway 'formulated takeaway' --question 'q1' --question 'q2'
6. Update current_section on the book

EXERCISE LOGGING:
- When user reports exercise, log immediately: nexus self exercise log --type 'type' --description 'what they did' --intensity easy|moderate|hard --duration minutes
- Provide motivation: acknowledge effort, relate to weekly goal

MATH LOGGING:
- Problems are in your daily message. User reports time and correctness
- Log: nexus self math log --time 'M:SS' --correct N
- Optional: --type flag for each problem type if you remember them from the generated output
- If user consistently scores >90% correct and time is trending down over 2+ weeks, consider adjusting self/math/config.toml: increase max_digits, shift weights toward harder types

LEARNING LOGGING:
- When user confirms they learned: nexus self learn log --notes 'what they described'
- If they explicitly say they didnt learn: nexus self learn log --skip

ACCOUNTABILITY PATTERNS:
- Monday: fresh week, set expectations, no pressure yet
- Mid-week (Wed-Thu): check progress, flag if behind pace
- Friday: last push messaging, 'you have the weekend but lets not leave everything to Saturday'
- Weekend: lighter touch unless seriously behind
- If a habit has 0 sessions and its mid-week or later: call it out directly
- If yesterday had no check-in at all: 'You didnt check in yesterday. What happened?'
- Track patterns across the weekly data: 'This is the third day this week with no reading'

AVAILABLE COMMANDS REFERENCE:
List every nexus self command with flags and examples (copy from the spec)

## Completion Notes

Created onboard.py with all 8 sections (intro, date, reading, exercise, math, learning, weekly overview, agent instructions). Created agent_instructions.md with full playbook covering identity, daily message structure, reading comprehension flow, logging commands, accountability patterns, and command reference.