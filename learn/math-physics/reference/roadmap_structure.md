# Math-Physics Roadmap Structure

## Vision

Refresh rusty math/physics background to enable:
- Mathematics of Quantitative Finance
- Quantum Computing (down the line)

## Subtopics

### 1. Foundations (current)

Quick refresh of core prerequisites. The goal is rapid acceleration — get comfortable with the basics again so we can dive into more advanced material.

#### Phase 1: Calculus & Differential Equations

The language of change. Essential for both quantitative finance (modeling prices, rates of change) and physics.

| Phase | Content | Purpose |
|-------|---------|---------|
| language | Algebra, Functions, Trigonometry | Foundation vocabulary |
| change | Limits, Derivatives, Applications | Rate of change concepts |
| accumulation | Integrals, Applications, Sequences & Series | Area under curves, summation |
| flow | Vectors, Partial Derivatives, Multiple Integrals, Vector Calculus | Multidimensional calculus |
| differential-equations | First/Second order ODEs, Systems, Laplace transforms | Modeling dynamic systems |

#### Phase 2: Statistics & Probability

The language of uncertainty. Essential for quantitative finance (risk, pricing, time series) and quantum mechanics (probability amplitudes).

| Phase | Content | Purpose |
|-------|---------|---------|
| fundamentals | Probability axioms, Conditional probability, Bayes' theorem | Core probability |
| distributions | Discrete & Continuous distributions, Key distributions (Binomial, Poisson, Normal, Lognormal) | Common models |
| estimation | Point estimation, MLE, Confidence intervals | Inferring parameters |
| inference | Hypothesis testing, p-values, Decision theory | Testing claims |
| regression | Simple & Multiple linear regression, OLS, Diagnostics | Relationships between variables |
| time-series | Stationarity, ARMA/ARIMA, Volatility (ARCH/GARCH) | Temporal patterns |
| stochastic-processes | Markov chains, Poisson processes, Brownian motion | Random processes |

#### Phase 3: Quantum Mechanics (Mathematical Foundations)

The physics of the very small. Essential background for quantum computing.

| Phase | Content | Purpose |
|-------|---------|---------|
| mathematical-preliminaries | Vector spaces, Hilbert spaces, Dirac notation, Linear operators, Eigenvalues | Mathematical formalism |
| foundations | State vectors, Schrödinger equation, Measurement, Born rule, Time evolution | Core postulates |
| one-dimensional-systems | Infinite square well, Harmonic oscillator, Quantum tunneling | Simple quantum systems |
| angular-momentum | Spin-1/2, Pauli matrices, Stern-Gerlach | Quantum angular momentum |
| approximation-methods | Perturbation theory, Variational method | Approximate solutions |
| quantum-information | Qubits, Bloch sphere, Superposition, Entanglement, Bell states | Bridge to QC |

#### Phase 4: Theoretical Computer Science

The theory of computation. Essential for understanding quantum computing's advantages.

| Phase | Content | Purpose |
|-------|---------|---------|
| automata | DFA/NFA, Regular languages, Context-free grammars | Computation models |
| computability | Turing machines, Decidability, Halting problem | Limits of computation |
| complexity | P, NP, NP-completeness, Space complexity | Computational hardness |
| quantum-intro | Qubits, Quantum gates, Deutsch-Jozsa, Grover, Shor | Quantum algorithms intro |

---

### 2. Quantitative Finance (future)

Deep dive into mathematical finance.

- **Asset pricing** — Portfolio theory, CAPM, APT
- **Derivatives** — Options, Black-Scholes, Greeks
- **Risk management** — VaR, CVaR, hedging
- **Stochastic calculus** — Ito calculus, martingales
- **Volatility modeling** — GARCH, stochastic volatility
- **Credit risk** — Default probability, credit derivatives

### 3. Quantum Computing (future)

From foundations to algorithms.

- **Quantum algorithms** — Deutsch-Jozsa, Grover, Shor, Quantum Fourier Transform
- **Quantum error correction** — Codes, fault tolerance
- **Quantum information theory** — Entanglement, quantum channels
- **Physical implementations** — qubits, coherence, gates

---

## Phase Naming Convention

For each subtopic, phases follow a progression:
- `foundations` → `intermediate` → `advanced` (or domain-specific names)

Within each phase, goals are ordered to build mastery progressively.

## Dependencies

```
Foundations
├── Calculus & DE ──────────────────┐
├── Statistics & Probability ───────┤
├── Quantum Mechanics ──────────────┤
└── Theoretical CS ─────────────────┘
          │
          ▼
  Quantitative Finance ◄────────────┤
          │                         │
          ▼                         │
    Quantum Computing ───────────────┘
```

The four foundational tracks (calculus, stats, QM, TCS) can be done in parallel or sequentially. They provide the mathematical vocabulary needed for the advanced subtopics.
