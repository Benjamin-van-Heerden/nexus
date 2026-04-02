# Calculus: Change

The study of rates of change. Limits formalize the concept of approaching a value, while derivatives quantify instantaneous rates of change.

---

## 1. Limits

### 1.1 Definition

The limit of $f(x)$ as $x$ approaches $a$ is $L$ if:
$$\lim_{x \to a} f(x) = L$$

This means $f(x)$ can be made arbitrarily close to $L$ by taking $x$ sufficiently close to $a$ (but not equal to $a$).

**One-sided Limits:**
- Left-hand: $\lim_{x \to a^-} f(x)$
- Right-hand: $\lim_{x \to a^+} f(x)$

**The limit exists iff both one-sided limits exist and are equal.**

### 1.2 Limit Laws

If $\lim f(x) = L$ and $\lim g(x) = M$:

$$\lim [f(x) \pm g(x)] = L \pm M$$
$$\lim [f(x) \cdot g(x)] = L \cdot M$$
$$\lim \frac{f(x)}{g(x)} = \frac{L}{M} \quad \text{if } M \neq 0$$
$$\lim c \cdot f(x) = c \cdot L$$
$$\lim [f(x)]^n = L^n$$

### 1.3 Computing Limits

**Direct Substitution:**
If $f$ is continuous at $a$, then $\lim_{x \to a} f(x) = f(a)$.

**Factoring:**
$$\lim_{x \to 2} \frac{x^2 - 4}{x - 2} = \lim_{x \to 2} \frac{(x-2)(x+2)}{x-2} = \lim_{x \to 2} (x+2) = 4$$

**Rationalizing:**
For limits with square roots:
$$\lim_{x \to 4} \frac{\sqrt{x} - 2}{x - 4} = \lim_{x \to 4} \frac{\sqrt{x} - 2}{x - 4} \cdot \frac{\sqrt{x} + 2}{\sqrt{x} + 2} = \lim_{x \to 4} \frac{x - 4}{(x - 4)(\sqrt{x} + 2)} = \frac{1}{4}$$

**Common Limits:**
$$\lim_{x \to 0} \frac{\sin x}{x} = 1$$
$$\lim_{x \to 0} \frac{1 - \cos x}{x} = 0$$
$$\lim_{x \to 0} \frac{1 - \cos x}{x^2} = \frac{1}{2}$$
$$\lim_{x \to \infty} \frac{\sin x}{x} = 0$$
$$\lim_{x \to 0} \frac{e^x - 1}{x} = 1$$
$$\lim_{x \to 0} \frac{\ln(1 + x)}{x} = 1$$

### 1.4 The Squeeze Theorem

If $g(x) \leq f(x) \leq h(x)$ near $a$ and $\lim g(x) = \lim h(x) = L$, then $\lim f(x) = L$.

**Application:** Proving $\lim_{x \to 0} \frac{\sin x}{x} = 1$

### 1.5 Continuity

A function is continuous at $x = a$ if:
1. $f(a)$ exists
2. $\lim_{x \to a} f(x)$ exists
3. $\lim_{x \to a} f(x) = f(a)$

**Types of Discontinuities:**
- **Removable**: hole in graph (can fill by redefining $f(a)$)
- **Jump**: finite jump in function values
- **Infinite**: vertical asymptote
- **Oscillatory**: infinite oscillations

**Intermediate Value Theorem:**
If $f$ is continuous on $[a, b]$ and $N$ is between $f(a)$ and $f(b)$, then there exists $c \in [a, b]$ such that $f(c) = N$.

**Important Consequence:** If $f(a)$ and $f(b)$ have opposite signs, then $f$ has at least one root in $(a, b)$.

### 1.6 Limits at Infinity

$$\lim_{x \to \infty} f(x) = L$$

**Horizontal Asymptote:** The line $y = L$ if the limit exists.

**Polynomial Behavior:**
$$\lim_{x \to \infty} \frac{a_n x^n + \cdots}{b_m x^m + \cdots} = \lim_{x \to \infty} \frac{a_n x^n}{b_m x^m}$$

**For rational functions:** Compare degrees:
- Degree equal: ratio of leading coefficients
- Numerator degree < denominator: limit is 0
- Numerator degree > denominator: limit is $\pm\infty$

---

## 2. Derivatives

### 2.1 Definition

The derivative of $f$ at $x = a$ is:
$$f'(a) = \lim_{h \to 0} \frac{f(a + h) - f(a)}{h} = \lim_{x \to a} \frac{f(x) - f(a)}{x - a}$$

**Geometric Interpretation:** Slope of the tangent line at $(a, f(a))$.

**Alternative Notation:**
- Leibniz: $\frac{df}{dx}$ or $\frac{dy}{dx}$
- Lagrange: $f'$
- Newton: $\dot{f}$ (physics)

### 2.2 Differentiability

$f$ is differentiable at $a$ if the limit above exists.

**Implications:**
- Differentiable $\Rightarrow$ Continuous
- Continuous $\not\Rightarrow$ Differentiable (e.g., $f(x) = |x|$ at $x = 0$)

**One-sided Derivatives:**
- $f'_-(a) = \lim_{h \to 0^-} \frac{f(a+h) - f(a)}{h}$
- $f'_+(a) = \lim_{h \to 0^+} \frac{f(a+h) - f(a)}{h}$

$f$ is differentiable at $a$ iff $f'_-(a) = f'_+(a)$.

### 2.3 Differentiation Rules

**Constant Multiple:**
$$\frac{d}{dx}[c \cdot f] = c \cdot f'$$

**Sum/Difference:**
$$\frac{d}{dx}[f \pm g] = f' \pm g'$$

**Product Rule:**
$$\frac{d}{dx}[f \cdot g] = f' \cdot g + f \cdot g'$$

**Quotient Rule:**
$$\frac{d}{dx}\left[\frac{f}{g}\right] = \frac{f' \cdot g - f \cdot g'}{g^2}$$

**Chain Rule:**
$$\frac{d}{dx}[f(g(x))] = f'(g(x)) \cdot g'(x)$$

### 2.4 Derivatives of Common Functions

**Power Rule:**
$$\frac{d}{dx}[x^n] = n x^{n-1} \quad \text{for any real } n$$

**Trigonometric:**
$$\frac{d}{dx}[\sin x] = \cos x$$
$$\frac{d}{dx}[\cos x] = -\sin x$$
$$\frac{d}{dx}[\tan x] = \sec^2 x$$
$$\frac{d}{dx}[\sec x] = \sec x \tan x$$
$$\frac{d}{dx}[\csc x] = -\csc x \cot x$$
$$\frac{d}{dx}[\cot x] = -\csc^2 x$$

**Exponential:**
$$\frac{d}{dx}[e^x] = e^x$$
$$\frac{d}{dx}[a^x] = a^x \ln a$$

**Logarithmic:**
$$\frac{d}{dx}[\ln x] = \frac{1}{x}$$
$$\frac{d}{dx}[\log_a x] = \frac{1}{x \ln a}$$

**Inverse Functions:**
If $y = f^{-1}(x)$, then:
$$(f^{-1})'(x) = \frac{1}{f'(f^{-1}(x))}$$

**Inverse Trigonometric:**
$$\frac{d}{dx}[\arcsin x] = \frac{1}{\sqrt{1 - x^2}}$$
$$\frac{d}{dx}[\arccos x] = -\frac{1}{\sqrt{1 - x^2}}$$
$$\frac{d}{dx}[\arctan x] = \frac{1}{1 + x^2}$$

### 2.5 Implicit Differentiation

For equations $F(x, y) = 0$ defining $y$ as a function of $x$:

1. Differentiate both sides with respect to $x$
2. Treat $y$ as a function: $\frac{d}{dx}[y] = y'$
3. Solve for $y'$

**Example:**
$$x^2 + y^2 = 25$$
$$2x + 2y \cdot y' = 0$$
$$y' = -\frac{x}{y}$$

### 2.6 Logarithmic Differentiation

For functions of the form $y = f(x)^{g(x)}$:

1. Take $\ln$ of both sides: $\ln y = g(x) \ln f(x)$
2. Differentiate: $\frac{y'}{y} = g'(x) \ln f(x) + g(x) \cdot \frac{f'(x)}{f(x)}$
3. Solve for $y'$

**Useful for:** Products of many functions, functions with variables in exponent

### 2.7 Higher Order Derivatives

$$f''(x) = \frac{d}{dx}[f'(x)]$$
$$f^{(n)}(x) = \frac{d}{dx}[f^{(n-1)}(x)]$$

---

## 3. Applications of Derivatives

### 3.1 Related Rates

Given a relationship between variables that depend on time $t$, find the rate of change of one variable given the rate of change of another.

**Procedure:**
1. Identify all variables and their rates ($\frac{dx}{dt}, \frac{dy}{dt}$)
2. Write equation relating variables
3. Differentiate with respect to $t$
4. Substitute known values and solve

**Classic Examples:**
- Expanding circle: $\frac{dA}{dt} = 2\pi r \frac{dr}{dt}$
- Sliding ladder: $\frac{dx}{dt}$ relates to $\frac{dy}{dt}$ via $x^2 + y^2 = L^2$
- Conical tank: $\frac{dV}{dt}$ relates to $\frac{dh}{dt}$ via $V = \frac{1}{3}\pi r^2 h$

### 3.2 Linear Approximation

**Tangent Line Approximation:**
$$f(x) \approx f(a) + f'(a)(x - a)$$

**Linearization:**
$$L(x) = f(a) + f'(a)(x - a)$$

**Error Estimate:**
$$|R_n(x)| \leq \frac{M}{(n+1)!}|x - a|^{n+1}$$
where $|f^{(n+1)}(t)| \leq M$ for $t$ between $x$ and $a$

### 3.3 The Mean Value Theorem

If $f$ is continuous on $[a, b]$ and differentiable on $(a, b)$, then there exists $c \in (a, b)$ such that:
$$f'(c) = \frac{f(b) - f(a)}{b - a}$$

**Interpretation:** There exists a point where the instantaneous slope equals the average slope.

**Consequences:**
- If $f'(x) = 0$ for all $x \in (a, b)$, then $f$ is constant on $(a, b)$
- If $f'(x) > 0$ for all $x \in (a, b)$, then $f$ is increasing on $(a, b)$
- If $f'(x) < 0$ for all $x \in (a, b)$, then $f$ is decreasing on $(a, b)$

### 3.4 L'Hôpital's Rule

For indeterminate forms $\frac{0}{0}$ or $\frac{\infty}{\infty}$:

$$\lim_{x \to a} \frac{f(x)}{g(x)} = \lim_{x \to a} \frac{f'(x)}{g'(x)}$$

**Requirements:**
- Limit is of form $\frac{0}{0}$ or $\frac{\infty}{\infty}$
- $f'$ and $g'$ exist near $a$ (except possibly at $a$)
- $g'(x) \neq 0$ near $a$

**Can apply repeatedly.** May need to combine with other techniques.

**Other Indeterminate Forms:**
- $0 \cdot \infty$: rewrite as $\frac{\infty}{\infty}$ or $\frac{0}{0}$
- $\infty - \infty$: combine into single fraction
- $0^0, \infty^0, 1^\infty$: take $\ln$ first

### 3.5 Curve Sketching

**Using First Derivative:**
- $f'(x) > 0$: increasing
- $f'(x) < 0$: decreasing
- $f'(x) = 0$: critical points (potential local extrema)

**Using Second Derivative:**
- $f''(x) > 0$: concave up
- $f''(x) < 0$: concave down
- $f''(x) = 0$: inflection points (where concavity changes)

**Key Features to Find:**
1. Domain
2. Intercepts (x and y)
3. Symmetry (even/odd/periodic)
4. Asymptotes (vertical, horizontal, slant)
5. Critical points and intervals of increase/decrease
6. Inflection points and intervals of concavity
7. End behavior

### 3.6 Optimization

**Finding Maximum/Minimum:**

1. **Closed Interval:** Evaluate at endpoints and critical points
2. **Open Interval:** Use first/second derivative tests

**First Derivative Test:**
- $f'$ changes from + to -: local maximum
- $f'$ changes from - to +: local minimum
- $f'$ does not change: neither (or test fails)

**Second Derivative Test:**
- If $f'(c) = 0$ and $f''(c) > 0$: local minimum
- If $f'(c) = 0$ and $f''(c) < 0$: local maximum
- If $f''(c) = 0$: test inconclusive

**Absolute Extrema:**
On closed interval $[a, b]$: check $f(a), f(b)$, and critical points in $(a, b)$.

---

## 4. Quick Reference

### 4.1 Derivative Rules Summary

| Function | Derivative |
|----------|------------|
| $c$ | 0 |
| $x^n$ | $n x^{n-1}$ |
| $e^x$ | $e^x$ |
| $a^x$ | $a^x \ln a$ |
| $\ln x$ | $1/x$ |
| $\sin x$ | $\cos x$ |
| $\cos x$ | $-\sin x$ |
| $\tan x$ | $\sec^2 x$ |
| $\arcsin x$ | $1/\sqrt{1-x^2}$ |
| $\arctan x$ | $1/(1+x^2)$ |

### 4.2 Common Missteps

- Forgetting chain rule when differentiating compositions
- Not simplifying after differentiating
- Applying L'Hôpital incorrectly to non-indeterminate forms
- Confusing concave up (f'' > 0) with increasing (f' > 0)
- Missing domain restrictions when finding absolute extrema

---

## 5. Exercises Guidance

For this material, create exercises requiring:

1. **Limits** — Computing limits using various techniques (substitution, factoring, rationalizing, special limits), determining continuity, and identifying types of discontinuities.

2. **Derivatives** — Applying all differentiation rules (power, product, quotient, chain), implicit differentiation, and logarithmic differentiation.

3. **Applications** — Related rates problems, linear approximation, using the Mean Value Theorem, L'Hôpital's rule for indeterminate forms, curve sketching, and optimization problems.

Include problems that combine multiple techniques and require clear step-by-step reasoning.
