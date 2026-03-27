Best Practices for Creating a Skill File 

Here's a clear, comprehensive guide on how to create high-quality skill files in OpenClaw.

1. Skill File Structure (Strict Requirements)

Every skill must follow this exact structure:

skill-name/
├── SKILL.md                  ← REQUIRED
├── scripts/                  ← Optional but recommended
├── references/               ← Optional
└── assets/                   ← Optional

Important rules:

• The folder name and skill name must be identical and use kebab-case (lowercase letters, numbers, hyphens only).
• You must not include README.md, INSTALL.md, CHANGELOG.md, or similar files. They are explicitly forbidden.
• Only include files that are actually useful to the agent doing the work.

2. SKILL.md Structure (Most Important File)

The SKILL.md file has two parts:

A. YAML Frontmatter (Top of the file)

---
name: skill-name
description: One or two sentences describing exactly what this skill does and, more importantly, WHEN it should be used. Be very specific about triggers.
---The description field is critical — this is how the system decides whether to load your skill. Make it comprehensive.

B. Main Body (Markdown)

This should contain:

• When to use the skill (even though it's also in the description)
• Core workflow / step-by-step instructions
• Clear guidance on when to read files from references/ or run scripts
• Examples of good usage
• Any important constraints or best practices

3. Recommended Organization Patterns

Progressive Disclosure (very important):

• Keep SKILL.md relatively short (<500 lines if possible)
• Put detailed information, schemas, long examples, and reference material in references/
• Put repeatable code in scripts/
• Put templates, boilerplate, and output assets in assets/

Good example structure:

• references/api-specs.md
• references/workflow-examples.md
• scripts/generate-report.py
• assets/templates/report-template.docx

4. Best Practices Summary

1. Be concise — every token costs money and reduces available context for the actual task.
2. Write for another agent, not for a human. Use imperative language.
3. Clearly define triggers in the description field.
4. Separate concerns — don't put everything in SKILL.md.
5. Include clear navigation in SKILL.md that tells the agent when to read other files.
6. Test your skill — make sure the instructions actually work well in practice.
7. Use the skill-creator skill itself when creating new skills (it's designed to help with this process).

───

Would you like me to show you:

• A high-quality example of a complete SKILL.md?
• The recommended template to start from?
• How to properly package a skill once it's written?
