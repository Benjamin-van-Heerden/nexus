# Calculus: Accumulation

The study of accumulation — integrals — and their applications. Also covers sequences and series, which extend the concept of summation to infinite processes.

---

## 1. Integrals

### 1.1 The Definite Integral

The definite integral of $f$ from $a$ to $b$:
$$\int_a^b f(x) \, dx = \lim_{n \to \infty} \sum_{i=1}^{n} f(x_i^*) \Delta x$$

where $\Delta x = \frac{b-a}{n}$ and $x_i^*$ is a sample point in the $i$th subinterval.

**Geometric Interpretation:**
- $\int_a^b f(x) \, dx$ = signed area between $y = f(x)$ and the x-axis from $x=a$ to $x=b$
- Area above x-axis counts positive, area below counts negative

**Properties:**
$$\int_a^b f(x) \, dx = -\int_b^a f(x) \, dx$$
$$\int_a^b [f(x) \pm g(x)] \, dx = \int_a^b f(x) \, dx \pm \int_a^b g(x) \, dx$$
$$\int_a^b c \cdot f(x) \, dx = c \int_a^b f(x) \, dx$$
$$\int_a^c f(x) \, dx = \int_a^b f(x) \, dx + \int_b^c f(x) \, dx$$

### 1.2 The Indefinite Integral

The antiderivative:
$$\int f(x) \, dx = F(x) + C$$
where $F'(x) = f(x)$ and $C$ is the constant of integration.

### 1.3 Basic Integration Rules

**Power Rule:**
$$\int x^n \, dx = \frac{x^{n+1}}{n+1} + C \quad \text{for } n \neq -1$$

**Special Case:**
$$\int \frac{1}{x} \, dx = \ln|x| + C$$

**Exponential:**
$$\int e^x \, dx = e^x + C$$
$$\int a^x \, dx = \frac{a^x}{\ln a} + C$$

**Trigonometric:**
$$\int \sin x \, dx = -\cos x + C$$
$$\int \cos x \, dx = \sin x + C$$
$$\int \sec^2 x \, dx = \tan x + C$$
$$\int \csc^2 x \, dx = -\cot x + C$$
$$\int \sec x \tan x \, dx = \sec x + C$$
$$\int \csc x \cot x \, dx = -\csc x + C$$

### 1.4 Integration Techniques

#### 1.4.1 Substitution (Chain Rule in Reverse)

$$\int f(g(x)) \cdot g'(x) \, dx = \int f(u) \, du \quad \text{where } u = g(x)$$

**Steps:**
1. Choose $u = g(x)$
2. Compute $du = g'(x) \, dx$
3. Rewrite integral in terms of $u$
4. Integrate
5. Substitute back: $u = g(x)$

**Definite Integrals:**
$$\int_a^b f(g(x)) \cdot g'(x) \, dx = \int_{g(a)}^{g(b)} f(u) \, du$$

#### 1.4.2 Integration by Parts

$$\int u \, dv = uv - \int v \, du$$

**LIATE Rule:** Choose $u$ in this order:
1. **L**ogarithmic
2. **I**nverse trig
3. **A**lgebraic
4. **T**rigonometric
5. **E**xponential

**Derivation:** From product rule: $\frac{d}{dx}[uv] = u'v + uv'$, so $\int u \, dv = uv - \int v \, du$

**Repeated Integration by Parts:**
For integrals like $\int x^n e^x \, dx$, apply repeatedly, or use tabular method.

**Reduction Formulas:**
$$\int \sin^n x \, dx = -\frac{\sin^{n-1} x \cos x}{n} + \frac{n-1}{n} \int \sin^{n-2} x \, dx$$

#### 1.4.3 Trigonometric Integrals

**Powers of $\sin x$ and $\cos x$:**

- If $m$ is odd: save one $\sin x$ (or $\cos x$) and convert rest using $\sin^2 x = 1 - \cos^2 x$
- If $n$ is odd: save one $\cos x$ and convert rest using $\cos^2 x = 1 - \sin^2 x$
- If both $m, n$ are even: use half-angle identities

**Products of $\sin(mx)$ and $\cos(nx)$:**
Use product-to-sum identities:
$$\sin A \cos B = \frac{1}{2}[\sin(A+B) + \sin(A-B)]$$
$$\sin A \sin B = \frac{1}{2}[\cos(A-B) - \cos(A+B)]$$
$$\cos A \cos B = \frac{1}{2}[\cos(A-B) + \cos(A+B)]$$

#### 1.4.4 Trigonometric Substitution

For integrals containing $\sqrt{a^2 - x^2}$, $\sqrt{a^2 + x^2}$, or $\sqrt{x^2 - a^2}$:

| Expression | Substitution |
|------------|--------------|
| $\sqrt{a^2 - x^2}$ | $x = a \sin \theta$ |
| $\sqrt{a^2 + x^2}$ | $x = a \tan \theta$ |
| $\sqrt{x^2 - a^2}$ | $x = a \sec \theta$ |

**Procedure:**
1. Make substitution
2. Simplify integrand
3. Integrate
4. Convert back to $x$ using right triangle

#### 1.4.5 Partial Fractions

For rational functions $\frac{P(x)}{Q(x)}$ where $\deg(P) < \deg(Q)$:

1. Factor $Q(x)$ into linear and irreducible quadratic factors
2. Write as sum of partial fractions:
   - Linear factor $(ax + b)$: $\frac{A}{ax+b}$
   - Repeated linear: $\frac{A}{ax+b} + \frac{B}{(ax+b)^2}$
   - Quadratic $ax^2+bx+c$: $\frac{Ax+B}{ax^2+bx+c}$
3. Solve for coefficients
4. Integrate each term

### 1.5 Improper Integrals

**Type 1: Infinite Limits**
$$\int_a^\infty f(x) \, dx = \lim_{b \to \infty} \int_a^b f(x) \, dx$$
$$\int_{-\infty}^b f(x) \, dx = \lim_{a \to -\infty} \int_a^b f(x) \, dx$$
$$\int_{-\infty}^\infty f(x) \, dx = \int_{-\infty}^c f(x) \, dx + \int_c^\infty f(x) \, dx$$

**Type 2: Infinite Discontinuities**
If $f$ has a discontinuity at $c \in [a, b]$:
$$\int_a^b f(x) \, dx = \lim_{t \to c^-} \int_a^t f(x) \, dx + \lim_{t \to c^+} \int_t^b f(x) \, dx$$

**Convergence/Divergence:**
- The integral **converges** if the limit exists and is finite
- The integral **diverges** if the limit is $\infty$, $-\infty$, or does not exist

**Comparison Test:**
If $0 \leq f(x) \leq g(x)$ and $\int_a^\infty g(x) \, dx$ converges, then $\int_a^\infty f(x) \, dx$ converges.

---

## 2. Applications of Integration

### 2.1 Area Between Curves

**Between $y = f(x)$ and $y = g(x)$ from $a$ to $b$:**
$$A = \int_a^b |f(x) - g(x)| \, dx$$

Find intersection points to determine integration limits.

**Between $x = f(y)$ and $x = g(y)$:**
$$A = \int_c^d |f(y) - g(y)| \, dy$$

### 2.2 Volume: Disk Method

**About x-axis:**
$$V = \int_a^b \pi [f(x)]^2 \, dx$$

**About y-axis:**
$$V = \int_c^d \pi [g(y)]^2 \, dy$$

**Washers (between two curves):**
$$V = \int_a^b \pi \left([f(x)]^2 - [g(x)]^2\right) \, dx$$

### 2.3 Volume: Shell Method

**Vertical shells (about y-axis):**
$$V = \int_a^b 2\pi x \cdot f(x) \, dx$$

**Horizontal shells (about x-axis):**
$$V = \int_c^d 2\pi y \cdot g(y) \, dy$$

**When to Use Which:**
- Disk/washer: easier when integrating in $x$ (or $y$) direction
- Shell: easier when integrating in $y$ (or $x$) direction, especially for functions solving for $x$

### 2.4 Arc Length

For $y = f(x)$ from $a$ to $b$:
$$s = \int_a^b \sqrt{1 + [f'(x)]^2} \, dx$$

For parametric curves $(x(t), y(t))$:
$$s = \int_{t_1}^{t_2} \sqrt{\left(\frac{dx}{dt}\right)^2 + \left(\frac{dy}{dt}\right)^2} \, dt$$

### 2.5 Surface Area

**Surface of revolution about x-axis:**
$$S = \int_a^b 2\pi f(x) \sqrt{1 + [f'(x)]^2} \, dx$$

### 2.6 Work

**Variable Force:**
$$W = \int_a^b F(x) \, dx$$

**Spring Force (Hooke's Law):** $F = kx$:
$$W = \int_0^d kx \, dx = \frac{1}{2} k d^2$$

**Pumping Fluid:**
$$W = \int_a^b \rho g \cdot A(y) \cdot d(y) \, dy$$
where $\rho$ is fluid density, $g$ is gravity, $A(y)$ is cross-sectional area, $d(y)$ is distance pumped.

### 2.7 Center of Mass

** lamina (thin plate) with density $\rho(x,y)$:**

**Moments:**
$$M_x = \int \int_R y \rho(x,y) \, dA$$
$$M_y = \int \int_R x \rho(x,y) \, dA$$

**Center of Mass:**
$$\bar{x} = \frac{M_y}{M}, \quad \bar{y} = \frac{M_x}{M}$$
where $M = \int \int_R \rho(x,y) \, dA$ (total mass)

---

## 3. Sequences and Series

### 3.1 Sequences

A sequence $\{a_n\}$ is an ordered list of numbers $a_1, a_2, a_3, \ldots$

**Limit of a Sequence:**
$$\lim_{n \to \infty} a_n = L$$
If the limit exists, the sequence converges to $L$; otherwise, it diverges.

**Monotonic Sequences:**
- Increasing: $a_{n+1} \geq a_n$
- Decreasing: $a_{n+1} \leq a_n$

**Bounded Sequences:**
- Bounded above: $a_n \leq M$ for all $n$
- Bounded below: $a_n \geq m$ for all $n$

**Monotonic Convergence Theorem:**
A bounded monotonic sequence converges.

### 3.2 Infinite Series

An infinite series:
$$\sum_{n=1}^\infty a_n = a_1 + a_2 + a_3 + \cdots$$

**Partial Sums:**
$$S_N = \sum_{n=1}^N a_n$$

**Convergence:**
$$\sum_{n=1}^\infty a_n = S \quad \text{if} \quad \lim_{N \to \infty} S_N = S$$

### 3.3 Geometric Series

$$\sum_{n=0}^\infty ar^n = a + ar + ar^2 + \cdots$$

**Sum:**
- If $|r| < 1$: converges to $\frac{a}{1-r}$
- If $|r| \geq 1$: diverges

### 3.4 Tests for Convergence

#### Integral Test
If $f$ is positive, continuous, decreasing, and $a_n = f(n)$:
$$\sum_{n=1}^\infty a_n \text{ converges } \iff \int_1^\infty f(x) \, dx \text{ converges}$$

#### Comparison Test
For positive terms:
- If $a_n \leq b_n$ and $\sum b_n$ converges, then $\sum a_n$ converges
- If $a_n \geq b_n$ and $\sum b_n$ diverges, then $\sum a_n$ diverges

#### Limit Comparison Test
If $\lim_{n \to \infty} \frac{a_n}{b_n} = L$ where $0 < L < \infty$:
Then $\sum a_n$ and $\sum b_n$ either both converge or both diverge.

#### Ratio Test
$$\lim_{n \to \infty} \left|\frac{a_{n+1}}{a_n}\right| = L$$
- If $L < 1$: converges absolutely
- If $L > 1$: diverges
- If $L = 1$: test inconclusive

#### Root Test
$$\lim_{n \to \infty} \sqrt[n]{|a_n|} = L$$
- If $L < 1$: converges absolutely
- If $L > 1$: diverges
- If $L = 1$: test inconclusive

### 3.5 Alternating Series

$$\sum_{n=1}^\infty (-1)^{n-1} b_n = b_1 - b_2 + b_3 - b_4 + \cdots$$
where $b_n > 0$

**Alternating Series Test:**
If $b_{n+1} \leq b_n$ for all $n$ and $\lim_{n \to \infty} b_n = 0$, then the series converges.

**Alternating Series Estimation:**
$$|R_N| \leq b_{N+1}$$
The error is at most the magnitude of the first omitted term.

### 3.6 Power Series

$$\sum_{n=0}^\infty c_n (x-a)^n = c_0 + c_1(x-a) + c_2(x-a)^2 + \cdots$$

**Radius of Convergence:** $R$ where series converges for $|x-a| < R$

**Interval of Convergence:** $(a-R, a+R)$, possibly including endpoints

### 3.7 Taylor Series

If $f$ has derivatives of all orders at $a$:
$$f(x) = \sum_{n=0}^\infty \frac{f^{(n)}(a)}{n!} (x-a)^n$$

**Maclaurin Series:** Taylor series about $x = 0$

**Common Maclaurin Series:**
$$e^x = \sum_{n=0}^\infty \frac{x^n}{n!} = 1 + x + \frac{x^2}{2!} + \frac{x^3}{3!} + \cdots$$
$$\sin x = \sum_{n=0}^\infty \frac{(-1)^n x^{2n+1}}{(2n+1)!} = x - \frac{x^3}{3!} + \frac{x^5}{5!} - \cdots$$
$$\cos x = \sum_{n=0}^\infty \frac{(-1)^n x^{2n}}{(2n)!} = 1 - \frac{x^2}{2!} + \frac{x^4}{4!} - \cdots$$
$$\ln(1+x) = \sum_{n=1}^\infty \frac{(-1)^{n-1} x^n}{n} = x - \frac{x^2}{2} + \frac{x^3}{3} - \cdots \quad \text{for } |x| < 1$$
$$\frac{1}{1-x} = \sum_{n=0}^\infty x^n = 1 + x + x^2 + \cdots \quad \text{for } |x| < 1$$

### 3.8 Taylor's Remainder

$$R_n(x) = \frac{f^{(n+1)}(c)}{(n+1)!} (x-a)^{n+1}$$
for some $c$ between $x$ and $a$.

**Error Bound:**
$$|R_n(x)| \leq \frac{M}{(n+1)!} |x-a|^{n+1}$$
where $|f^{(n+1)}(t)| \leq M$ for $t$ between $x$ and $a$.

---

## 4. Quick Reference

### 4.1 Integration Formulas

| Integral | Result |
|----------|--------|
| $\int x^n \, dx$ | $\frac{x^{n+1}}{n+1} + C$ (n ≠ -1) |
| $\int \frac{1}{x} \, dx$ | $\ln\|x\| + C$ |
| $\int e^x \, dx$ | $e^x + C$ |
| $\int a^x \, dx$ | $\frac{a^x}{\ln a} + C$ |
| $\int \sin x \, dx$ | $-\cos x + C$ |
| $\int \cos x \, dx$ | $\sin x + C$ |
| $\int \sec^2 x \, dx$ | $\tan x + C$ |
| $\int \frac{1}{1+x^2} \, dx$ | $\arctan x + C$ |
| $\int \frac{1}{\sqrt{1-x^2}} \, dx$ | $\arcsin x + C$ |

### 4.2 Convergence Tests

| Test | Series Type | Key Condition |
|------|-------------|---------------|
| Geometric | Any | $\|r\| < 1$ converges |
| Integral | Positive, decreasing | $\int_1^\infty f(x)$ converges |
| Comparison | Positive | Compare to known series |
| Ratio | Any | $L < 1$ converges |
| Root | Any | $L < 1$ converges |
| Alternating | Alternating | $b_n$ decreasing to 0 |

### 4.3 Common Maclaurin Series (converges for |x| < 1 unless noted)

- $e^x = \sum \frac{x^n}{n!}$
- $\sin x = \sum \frac{(-1)^n x^{2n+1}}{(2n+1)!}$
- $\cos x = \sum \frac{(-1)^n x^{2n}}{(2n)!}$
- $\ln(1+x) = \sum \frac{(-1)^{n-1} x^n}{n}$
- $\frac{1}{1-x} = \sum x^n$

---

## 5. Exercises Guidance

For this material, create exercises requiring:

1. **Integration** — All techniques: substitution, integration by parts, trigonometric integrals, trigonometric substitution, partial fractions, and handling improper integrals.

2. **Applications** — Area between curves, volumes (disk, washer, shell methods), arc length, surface area, work, and center of mass.

3. **Sequences** — Determining convergence/divergence, finding limits.

4. **Series** — Applying all convergence tests, working with geometric series, finding radius/interval of convergence for power series, constructing Taylor/Maclaurin series, using Taylor's remainder theorem for error estimation.

Include problems requiring choice of appropriate technique (e.g., which integration method to use, which convergence test to apply).
