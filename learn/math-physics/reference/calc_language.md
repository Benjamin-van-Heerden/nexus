# Calculus: Language

The foundational vocabulary of calculus — algebra, functions, and trigonometry. This material is prerequisite knowledge; we assume familiarity but provide a rapid refresher.

---

## 1. Algebra

### 1.1 Exponents and Logarithms

**Laws of Exponents:**
- $a^m \cdot a^n = a^{m+n}$
- $(a^m)^n = a^{mn}$
- $a^0 = 1$ for $a \neq 0$
- $a^{-n} = \frac{1}{a^n}$
- $a^{m/n} = \sqrt[n]{a^m} = (\sqrt[n]{a})^m$

**Laws of Logarithms:**
- $\log(ab) = \log a + \log b$
- $\log\left(\frac{a}{b}\right) = \log a - \log b$
- $\log(a^b) = b \log a$
- $\log_a x = \frac{\log_b x}{\log_b a}$ (change of base)

**Special Exponentials:**
- $e^x$ where $e \approx 2.71828$
- $\ln x = \log_e x$ (natural logarithm)

### 1.2 Factoring

**Common Factorization Patterns:**
- Difference of squares: $a^2 - b^2 = (a-b)(a+b)$
- Difference of cubes: $a^3 - b^3 = (a-b)(a^2 + ab + b^2)$
- Sum of cubes: $a^3 + b^3 = (a+b)(a^2 - ab + b^2)$
- Perfect square trinomials: $a^2 + 2ab + b^2 = (a+b)^2$

**Quadratic Formula:**
For $ax^2 + bx + c = 0$:
$$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$

**Completing the Square:**
To convert $ax^2 + bx + c$ to vertex form:
1. Divide by $a$ (if $a \neq 1$)
2. Add $(b/2a)^2$ to both sides
3. Factor the left side as a perfect square

### 1.3 Rational Expressions

**Simplifying:**
$$\frac{x^2 - 4}{x - 2} = \frac{(x-2)(x+2)}{x-2} = x + 2 \quad \text{for } x \neq 2$$

**Partial Fractions:**
Decompose $\frac{P(x)}{Q(x)}$ where $\deg(P) < \deg(Q)$:
1. Factor the denominator
2. Express as sum of simpler fractions
3. Solve for coefficients

### 1.4 Summation Notation

$$\sum_{i=1}^{n} a_i = a_1 + a_2 + \cdots + a_n$$

**Common Sums:**
- $\sum_{i=1}^{n} i = \frac{n(n+1)}{2}$
- $\sum_{i=1}^{n} i^2 = \frac{n(n+1)(2n+1)}{6}$
- $\sum_{i=1}^{n} i^3 = \left(\frac{n(n+1)}{2}\right)^2$
- $\sum_{i=0}^{n} r^i = \frac{1 - r^{n+1}}{1-r}$ for $r \neq 1$ (geometric series)

---

## 2. Functions

### 2.1 Function Basics

A function $f: A \to B$ maps each element of domain $A$ to exactly one element of range $B$.

**Notation:**
- $f(x)$ denotes the output at input $x$
- Domain: all valid inputs
- Range: all possible outputs

**Composition:**
$$(f \circ g)(x) = f(g(x))$$

**Inverse Functions:**
$$f^{-1}(f(x)) = x \quad \text{and} \quad f(f^{-1}(y)) = y$$
The inverse exists iff $f$ is one-to-one (injective).

### 2.2 Common Function Families

**Polynomial Functions:**
- Degree $n$: $f(x) = a_n x^n + a_{n-1} x^{n-1} + \cdots + a_0$
- End behavior determined by leading term $a_n x^n$
- Roots/zeros: solutions to $f(x) = 0$

**Rational Functions:**
$$f(x) = \frac{P(x)}{Q(x)}$$
- Vertical asymptotes: where $Q(x) = 0$
- Horizontal asymptote: behavior as $x \to \pm\infty$

**Exponential Functions:**
$$f(x) = a^x \quad \text{where } a > 0, a \neq 1$$
- Always positive
- $a^x \cdot a^y = a^{x+y}$
- If $a > 1$: increasing; if $0 < a < 1$: decreasing

**Logarithmic Functions:**
$$f(x) = \log_a x$$
- Domain: $x > 0$
- Inverse of exponential: $\log_a(a^x) = x$
- $\ln x$ uses base $e$

**Trigonometric Functions:**
- $\sin x, \cos x$ (period $2\pi$)
- $\tan x = \sin x / \cos x$ (period $\pi$)
- $\sec x = 1/\cos x, \csc x = 1/\sin x, \cot x = \cos x/\sin x$

### 2.3 Function Properties

**Even/Odd:**
- Even: $f(-x) = f(x)$ (symmetric about y-axis)
- Odd: $f(-x) = -f(x)$ (symmetric about origin)

**Periodic:**
$$f(x + T) = f(x)$$
$T$ is the period.

**Continuity:**
A function is continuous at $x=a$ if:
1. $f(a)$ exists
2. $\lim_{x \to a} f(x)$ exists
3. $\lim_{x \to a} f(x) = f(a)$

### 2.4 Transformations

Given $y = f(x)$:
- $f(x - c)$: shift right by $c$
- $f(x + c)$: shift left by $c$
- $f(x) + c$: shift up by $c$
- $f(x) - c$: shift down by $c$
- $cf(x)$: vertical stretch by $c$
- $f(cx)$: horizontal compression by $c$ (if $c > 1$)
- $f(-x)$: reflect about y-axis
- $-f(x)$: reflect about x-axis

---

## 3. Trigonometry

### 3.1 Fundamental Identities

**Pythagorean Identities:**
$$\sin^2 x + \cos^2 x = 1$$
$$1 + \tan^2 x = \sec^2 x$$
$$1 + \cot^2 x = \csc^2 x$$

**Quotient Identities:**
$$\tan x = \frac{\sin x}{\cos x}$$
$$\cot x = \frac{\cos x}{\sin x}$$

**Reciprocal Identities:**
$$\csc x = \frac{1}{\sin x}, \quad \sec x = \frac{1}{\cos x}, \quad \cot x = \frac{1}{\tan x}$$

### 3.2 Angle Sum and Difference

$$\sin(a \pm b) = \sin a \cos b \pm \cos a \sin b$$
$$\cos(a \pm b) = \cos a \cos b \mp \sin a \sin b$$
$$\tan(a \pm b) = \frac{\tan a \pm \tan b}{1 \mp \tan a \tan b}$$

### 3.3 Double and Half Angle

**Double Angle:**
$$\sin(2x) = 2 \sin x \cos x$$
$$\cos(2x) = \cos^2 x - \sin^2 x = 2\cos^2 x - 1 = 1 - 2\sin^2 x$$
$$\tan(2x) = \frac{2\tan x}{1 - \tan^2 x}$$

**Half Angle:**
$$\sin^2 x = \frac{1 - \cos(2x)}{2}$$
$$\cos^2 x = \frac{1 + \cos(2x)}{2}$$

**Half-angle formula for tangent:**
$$\tan\left(\frac{x}{2}\right) = \frac{\sin x}{1 + \cos x} = \frac{1 - \cos x}{\sin x}$$

### 3.4 Law of Sines and Cosines

**Law of Sines:**
$$\frac{a}{\sin A} = \frac{b}{\sin B} = \frac{c}{\sin C}$$

**Law of Cosines:**
$$c^2 = a^2 + b^2 - 2ab \cos C$$
$$a^2 = b^2 + c^2 - 2bc \cos A$$
$$b^2 = a^2 + c^2 - 2ac \cos B$$

### 3.5 Common Values

| degrees | radians | $\sin$ | $\cos$ | $\tan$ |
|---------|---------|--------|--------|--------|
| 0 | 0 | 0 | 1 | 0 |
| 30° | $\pi/6$ | $1/2$ | $\sqrt{3}/2$ | $1/\sqrt{3}$ |
| 45° | $\pi/4$ | $\sqrt{2}/2$ | $\sqrt{2}/2$ | 1 |
| 60° | $\pi/3$ | $\sqrt{3}/2$ | $1/2$ | $\sqrt{3}$ |
| 90° | $\pi/2$ | 1 | 0 | undefined |
| 180° | $\pi$ | 0 | -1 | 0 |
| 270° | $3\pi/2$ | -1 | 0 | undefined |

### 3.6 Inverse Trigonometric Functions

- $\arcsin x$: domain $[-1, 1]$, range $[-\pi/2, \pi/2]$
- $\arccos x$: domain $[-1, 1]$, range $[0, \pi]$
- $\arctan x$: domain $\mathbb{R}$, range $(-\pi/2, \pi/2)$

**Important Relationships:**
$$\arcsin x + \arccos x = \frac{\pi}{2}$$
$$\arctan x + \arctan\left(\frac{1}{x}\right) = \frac{\pi}{2} \quad \text{for } x > 0$$

---

## 4. Quick Reference

### 4.1 Common Graphs

| Function | Shape |
|----------|-------|
| $y = x$ | Straight line through origin, slope 1 |
| $y = x^2$ | Parabola, opens up |
| $y = x^3$ | Cubic, odd symmetry |
| $y = 1/x$ | Hyperbola, asymptotes on axes |
| $y = e^x$ | Exponential growth |
| $y = \ln x$ | Logarithm, passes through (1,0) |
| $y = \sin x$ | Wave, period $2\pi$ |
| $y = \cos x$ | Wave, period $2\pi$ |

### 4.2 Domain Restrictions

| Function | Domain |
|----------|--------|
| $1/x$ | $x \neq 0$ |
| $\sqrt{x}$ | $x \geq 0$ |
| $\ln x$ | $x > 0$ |
| $\arcsin x$ | $-1 \leq x \leq 1$ |
| $\arccos x$ | $-1 \leq x \leq 1$ |
| $\tan x$ | $x \neq \pi/2 + n\pi$ |

---

## 5. Exercises Guidance

When creating exercises for this material:

1. **Algebra** — Focus on manipulating expressions, solving equations, and recognizing patterns. Include problems requiring completion of squares and partial fractions.

2. **Functions** — Emphasize understanding domain/range, composition, and inverses. Graph transformations are important.

3. **Trigonometry** — Require memorization of key identities. Problems should require simplification using identities, solving trigonometric equations, and application of laws of sines/cosines.

4. **Integration** — Many integral problems reduce to algebraic or trigonometric manipulations, so this language section is essential foundation.
