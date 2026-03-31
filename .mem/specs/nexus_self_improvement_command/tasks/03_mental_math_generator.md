---
title: Mental math generator
status: completed
created_at: '2026-03-31T11:22:10.313720'
updated_at: '2026-03-31T15:52:09.958834'
completed_at: '2026-03-31T15:52:09.958827'
---
Create src/commands/self_improvement/math_generator.py — a standalone module that reads self/math/config.toml and generates math problems.

IMPORTANT CONTEXT: This generator is called by the onboard command to print problems inline. It is also available as a standalone CLI command. The problems are printed for the user to solve on paper or in their head — they are NOT stored anywhere. Only the user's self-reported time and accuracy are logged.

**How it works:**
1. Read MathConfig from self/math/config.toml
2. Select problem_types based on weights (e.g. multiplication weight=3 means 3x more likely than weight=1). Use random.choices() with weights to pick N problem types where N = config.general.problems_per_day
3. For each problem type, generate operands:
   - Random integers with digit count between min_digits and max_digits
   - After generating, randomly append 1 or 2 trailing zeros with probability trailing_zeros_chance (e.g. 47 might become 470 or 4700). Roll once for whether to add zeros, if yes, roll for 1 or 2 zeros (equal chance)
   - For division: generate a and b first (within digit ranges), compute product = a * b, then present 'product ÷ b = '. This guarantees whole number results. Apply trailing zeros to b before multiplication so the dividend is larger (e.g. b=47 becomes 470, product = a * 470)
   - For subtraction: ensure first operand >= second operand (no negative results)
4. Format output as numbered list with proper symbols:
   
5. Return both the formatted string AND the list of problem type names (needed for logging)

**Function signature:**
- generate_problems(config: MathConfig | None = None) -> tuple[str, list[str]]
  - If config is None, load from disk
  - Returns (formatted_problem_string, list_of_problem_type_names)

**Symbols:** use × for multiplication, ÷ for division, + for addition, - for subtraction (unicode, not ASCII x or /)

## Completion Notes

Created math_generator.py with weighted problem selection, trailing zeros, whole-number division, unicode symbols