# Foundations

## What are we learning?

The **Foundations** subtopic is a rapid refresher of core mathematical and computational prerequisites. You have a background in math and physics but it's rusty — this subtopic gets you back up to speed quickly so we can tackle more advanced material.

We cover four parallel tracks:

1. **Calculus & Differential Equations** — The mathematics of change and accumulation. Limits, derivatives, integrals, multivariable calculus, and differential equations.

2. **Statistics & Probability** — The mathematics of uncertainty. Probability theory, distributions, estimation, hypothesis testing, regression, time series, and stochastic processes.

3. **Quantum Mechanics** — The physics of quantum computing. Mathematical formalism (vector spaces, operators), core postulates, and key results needed to understand quantum algorithms.

4. **Theoretical Computer Science** — The theory of what computers can and cannot do. Automata, computability, complexity, and an introduction to quantum computing.

## Why are we learning this?

These four areas form the mathematical vocabulary you'll need for your actual goals:

- **Quantitative Finance** uses calculus (modeling rates of change), statistics (risk, time series), and stochastic processes (Brownian motion, pricing models).
  
- **Quantum Computing** builds directly on linear algebra, quantum mechanics, and computational complexity theory.

Without this foundation, the advanced material won't make sense. The goal is not to become an expert — it's to get comfortable again so you can learn at pace when we reach the interesting stuff.

## How will we learn?

### Exercise Types

- **practical** — 1-2 worked problems per session. These are problems you work through to solidify concepts. For math topics, this means solving problems. For theoretical topics, it might mean working through algorithm examples or proving properties.

- **theoretical** — Reading notes. A markdown document summarizing the key concepts from the reference material, explained in your own words, with reflection questions.

- **quiz** — Multiple choice questions (5-10). Quick check of conceptual understanding. No calculation heavy-lifting — these test whether you understand the ideas.

### Session Structure

Each session focuses on one goal (typically one chapter/section from the reference material). The agent will:
1. Check your recent activity
2. Read the reference material for the current goal
3. Research and validate exercise ideas
4. Create one exercise (practical, theoretical, or quiz)
5. Register it as a task
6. Tell you what to do

### Diagrams and Charts

All visual elements (plots, charts, diagrams) are created with **Typst**. The topic_info.md file contains comprehensive documentation on using Typst with lilaq (2D charts), plotsy-3d (3D plots), and cetz (diagrams).

## Proposed Phases

We will create phases as we go. The initial structure:

1. **Calculus** — Language → Change → Accumulation → Flow → Differential Equations
2. **Statistics** — Fundamentals → Distributions → Estimation → Inference → Regression → Time Series → Stochastic Processes
3. **Quantum Mechanics** — Math Preliminaries → Foundations → 1D Systems → Angular Momentum → Approximation Methods → Quantum Information
4. **Theoretical CS** — Automata → Computability → Complexity → Quantum Intro

We don't need to complete all phases in one go. We can interleave — e.g., finish calculus before starting stats, or do them in parallel if you have time.

## Resources

The reference documents for each goal are stored in:
```
learn/math-physics/reference/
```

You will provide reference materials. The agent will use them to create exercises.

Key tools:
- **Typst** — For creating diagrams and charts (installed via setup.sh)
- **Python/NumPy/SciPy** — For numerical computation in exercises
- **Qiskit** — For quantum computing exercises (future phase)
