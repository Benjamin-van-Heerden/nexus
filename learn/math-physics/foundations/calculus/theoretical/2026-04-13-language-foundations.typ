#set page(paper: "a4", margin: 2cm)
#set text(font: "New Computer Modern", size: 11pt)
#set par(justify: true, leading: 0.65em)
#set heading(numbering: "1.")

#show math.equation: set text(font: "New Computer Modern Math")

= Calculus Language: Foundations

_The vocabulary of calculus — algebra, functions, and trigonometry. This refresher covers the essential patterns you'll use constantly._

== 1. Algebra: The Manipulation Rules

Calculus is 90% algebra in disguise. The derivative and integral rules are straightforward; the hard part is simplifying the result. Master these patterns.

=== Exponents and Logarithms

*Exponential Laws:*
- Product: $a^m dot a^n = a^(m+n)$ — adding exponents when multiplying same bases
- Power of power: $(a^m)^n = a^(m n)$ — multiply exponents when raising powers
- Negative: $a^(-n) = 1/a^n$ — flip to denominator
- Fractional: $a^(m/n) = root(n, a^m)$ — denominator is the root, numerator is the power

*Logarithm Laws:*
- Product: $log(a b) = log a + log b$ — logs turn multiplication into addition
- Quotient: $log(a/b) = log a - log b$ — division becomes subtraction  
- Power: $log(a^b) = b log a$ — exponents come out front
- Change of base: $log_a x = (log_b x)/(log_b a)$ — crucial for calculators

The natural logarithm $ln x = log_e x$ uses $e approx 2.71828$. In calculus, $e$ is special because $(e^x)' = e^x$ — the function is its own derivative.

=== Factoring Patterns

Recognize these instantly:
- *Difference of squares:* $a^2 - b^2 = (a-b)(a+b)$
- *Difference of cubes:* $a^3 - b^3 = (a-b)(a^2 + a b + b^2)$
- *Sum of cubes:* $a^3 + b^3 = (a+b)(a^2 - a b + b^2)$
- *Perfect square:* $a^2 + 2a b + b^2 = (a+b)^2$

The quadratic formula $x = (-b plus.minus sqrt(b^2 - 4a c))/(2a)$ solves $a x^2 + b x + c = 0$. The discriminant $Delta = b^2 - 4a c$ tells you: positive → two real roots, zero → one repeated root, negative → complex roots.

=== Summation and Series

The geometric series appears everywhere in finance and analysis:

$ sum_(i=0)^n r^i = (1 - r^(n+1))/(1 - r) $ for $r != 1$

For $|r| < 1$, as $n -> infinity$: $sum_(i=0)^infinity r^i = 1/(1-r)$

== 2. Functions: Mappings and Behavior

A function $f: A -> B$ assigns exactly one output to each input. In calculus, we care deeply about:
- *Domain:* valid inputs (where is the function defined?)
- *Range:* possible outputs (what values can it produce?)

=== Function Operations

*Composition:* $(f compose g)(x) = f(g(x))$ — apply $g$ first, then $f$. Order matters: $f(g(x)) != g(f(x))$ in general.

*Inverses:* $f^(-1)(f(x)) = x$ and $f(f^(-1)(y)) = y$. An inverse exists only if $f$ is *injective* (one-to-one): each output comes from exactly one input. The horizontal line test checks this visually.

=== Transformations (The "Inside vs Outside" Rule)

Given $y = f(x)$:

*Outside changes* (applied to output $f(x)$):
- $f(x) + c$: shift *up* by $c$
- $f(x) - c$: shift *down* by $c$
- $c f(x)$: vertical stretch by $c$ (or compression if $0 < c < 1$)
- $-f(x)$: reflect over *x-axis*

*Inside changes* (applied to input $x$):
- $f(x + c)$: shift *left* by $c$ (counterintuitive!)
- $f(x - c)$: shift *right* by $c$
- $f(c x)$: horizontal *compression* by $c$ (if $c > 1$)
- $f(-x)$: reflect over *y-axis*

*Memory aid:* "Inside changes behave opposite to intuition." Adding inside shifts left; multiplying inside compresses horizontally.

=== Function Families

*Polynomials:* $f(x) = a_n x^n + dots.h.c + a_1 x + a_0$
- Degree $n$ determines end behavior
- Leading coefficient $a_n$ determines direction (positive → right end goes to $+infinity$ for even degree)

*Exponentials:* $f(x) = a^x$ with $a > 0, a != 1$
- Always positive
- Pass through $(0, 1)$ since $a^0 = 1$
- Growth if $a > 1$, decay if $0 < a < 1$

*Logarithms:* $f(x) = log_a x$
- Domain: $x > 0$ only
- Pass through $(1, 0)$ since $log_a 1 = 0$
- Inverse of exponentials: $log_a(a^x) = x$

== 3. Trigonometry: The Circular Functions

Calculus lives and breathes sine and cosine. You must know their derivatives, integrals, and identities cold.

=== The Pythagorean Identity

$ sin^2 x + cos^2 x = 1 $

This is the foundation. Divide by $cos^2 x$ to get: $1 + tan^2 x = sec^2 x$
Divide by $sin^2 x$ to get: $1 + cot^2 x = csc^2 x$

=== Angle Sum and Difference

$ sin(a plus.minus b) = sin a cos b plus.minus cos a sin b $
$ cos(a plus.minus b) = cos a cos b minus.plus sin a sin b $

Notice the pattern: sine keeps the same sign, cosine flips it. These are crucial for integration techniques later.

=== Double Angle Formulas

$ sin(2x) = 2 sin x cos x $
$ cos(2x) = cos^2 x - sin^2 x = 2cos^2 x - 1 = 1 - 2sin^2 x $

The multiple forms of $cos(2x)$ are useful for different situations — learn to recognize when each applies.

=== Half-Angle Formulas

$ sin^2 x = (1 - cos(2x))/2 $
$ cos^2 x = (1 + cos(2x))/2 $

These are *power-reduction* formulas. They convert squared trig functions into linear ones — essential for integrating $sin^2 x$ or $cos^2 x$.

=== Common Values (Know Cold)

#table(
  columns: (1fr, 1fr, 1fr, 1fr, 1fr),
  align: center,
  table.header[Degrees][Radians][$sin$][$cos$][$tan$],
  [0°], [$0$], [$0$], [$1$], [$0$],
  [30°], [$pi/6$], [$1/2$], [$sqrt(3)/2$], [$1/sqrt(3)$],
  [45°], [$pi/4$], [$sqrt(2)/2$], [$sqrt(2)/2$], [$1$],
  [60°], [$pi/3$], [$sqrt(3)/2$], [$1/2$], [$sqrt(3)$],
  [90°], [$pi/2$], [$1$], [$0$], [undefined],
)

== 4. Domain Restrictions in Calculus

These restrictions appear constantly:

- $1/x$: undefined at $x = 0$ (vertical asymptote)
- $sqrt(x)$: requires $x >= 0$ (domain restriction)
- $ln x$: requires $x > 0$ (asymptotic at 0)
- $tan x$: undefined at $x = pi/2 + n pi$ (vertical asymptotes)
- $arcsin x, arccos x$: domain $[-1, 1]$ only

== Reflection Questions

1. *Why is $e$ special in calculus?* (Hint: think about derivatives)

2. *If you compose $f(x) = x^2$ and $g(x) = x + 1$, what's $f(g(x))$ vs $g(f(x))$?* Calculate both and compare.

3. *Explain in your own words:* Why does $f(x + c)$ shift left instead of right?

4. *Derive the identity:* $tan^2 x + 1 = sec^2 x$ starting from $sin^2 x + cos^2 x = 1$.

5. *When would you use the power-reduction formulas?* Give an example where they're necessary.

---

*File: `/home/benjamin/Documents/nexus/learn/math-physics/foundations/calculus/theoretical/2026-04-13-language-foundations.typ`*