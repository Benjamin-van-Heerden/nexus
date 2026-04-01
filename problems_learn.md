"""
You have 2 incomplete tasks from today for the **JAX Mental Model and jax.numpy** goal:

1. **[practical]** Pure functions and composition — normalize rows, running max, scatter add, batch stats, two-layer forward pass
   - File: `/Users/benjamin/Documents/Personal/nexus/learn/jax/from-scratch/foundations/practical/examples/2026-04-01.py`

2. **[theoretical]** Theoretical reading — JAX mental model: functions vs tensors, purity, immutability, device/dtype
   - File: `/Users/benjamin/Documents/Personal/nexus/learn/jax/from-scratch/foundations/theoretical/2026-04-01-mental-model.md`

Want to pick up where you left off? Which one would you like to tackle first — the practical exercise or the theoretical reading?
""" --> The agent shouldn't ask, "What would you like to do", it should simply state, "You have these things to do, let me know when you have completed them". The agent's job is to compose new exercises, handle administration (based on my feedback), record interactions and occasionally set up new learning tracks. It is *my job* to actually do the exercises.


-----------------------

"""
nexus learn task complete "Pure functions and composition — normalize rows, running max, scatter add, batch stats, two-layer forward pass"
...
nexus learn task complete "Theoretical reading — JAX mental model: functions vs tensors, purity, immutability, device/dtype"
...
Both tasks marked complete. How long did they take you roughly, and was there anything you found tricky or straightforward? I'll log a record for the session.
""" --> We should add an output of the relevant_files so the agent knows what the user worked on. Does this make sense? If not ask so I can clarify.

-----------------------

In general: we should add hints that "record" files should be more descriptive than they currently are. it's ok as is, but we can tell the agent that they can ask follow up questions the user, records are how the agent will guage comprehension so they are important.

-----------------------

In general: we should make sure that tasks *must* have relevant_files section, we can't be having random open ended tasks that attach to nothing

-----------------------

"""
...
2. Quiz (~5 min)** — 3 questions on tracing, immutability, and axis semantics. Fill in your answers and check against the hidden answers at the bottom.
...
""" --> Don't put the answers at the bottom of the same file, that just makes it way too easy to look at. We should create a separate file with the answers, maybe under quiz/answers I think would be best
