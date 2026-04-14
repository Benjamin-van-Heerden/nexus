#set page(paper: "a4", margin: 2cm)
#set text(font: "New Computer Modern", size: 11pt)
#set par(justify: true, leading: 0.65em)
#set heading(numbering: "1.")

#show math.equation: set text(font: "New Computer Modern Math")

#import "@preview/lilaq:0.6.0" as lq

= Practical: Limits and Derivatives

*Date:* 2026-04-14 \
*Topic:* Calculus — Change \
*Estimated Time:* 45–60 minutes

== Problem 1: Computing Limits

Evaluate the following limits. Show all steps and identify the technique used.

=== (a) Factoring

$ lim_(x -> 3) frac(x^2 - 9, x^2 - 5x + 6) $

*Hint:* Factor both numerator and denominator.

=== (b) Rationalizing

$ lim_(x -> 0) frac(sqrt(1 + x) - sqrt(1 - x), x) $

*Hint:* Multiply numerator and denominator by the conjugate.

=== (c) Special Limits

$ lim_(x -> 0) frac(sin 3x, tan 5x) $

*Hint:* Use the standard limit $lim_(theta -> 0) frac(sin theta, theta) = 1$ and express $tan$ in terms of $sin$ and $cos$.

=== (d) L'Hôpital's Rule

$ lim_(x -> 0^+) x ln x $

*Hint:* Rewrite as a quotient to get $frac(0, 0)$ or $frac(infinity, infinity)$ form.

=== (e) Limits at Infinity

$ lim_(x -> infinity) frac(3x^3 - 2x + 1, 5x^3 + 4x^2 - 7) $

*Hint:* Divide numerator and denominator by the highest power of $x$.

#pagebreak()

== Problem 2: Differentiation

Find the derivative of each function. Simplify your answers where possible.

=== (a) Power Rule + Chain Rule

$ f(x) = (3x^2 + 2x - 1)^5 $

=== (b) Product Rule

$ g(x) = x^2 e^(3x) $

=== (c) Quotient Rule

$ h(x) = frac(x^2 + 1, x^2 - 1) $

=== (d) Implicit Differentiation

Find $frac(d y, d x)$ given:

$ x^3 + y^3 = 6x y $

=== (e) Logarithmic Differentiation

$ y = x^(sin x) $

#pagebreak()

== Problem 3: Related Rates

A spherical balloon is being inflated such that its volume increases at a constant rate of $100 "cm"^3"/""s"$. Find the rate at which the radius is increasing when the radius is $5 "cm"$.

*Given:*
- Volume of sphere: $V = frac(4, 3) pi r^3$
- $frac(d V, d t) = 100 "cm"^3"/""s"$
- Find $frac(d r, d t)$ when $r = 5 "cm"$

*Visualization:*

#figure(
  lq.diagram(
    width: 8cm,
    height: 6cm,
    xlabel: [$r$ (cm)],
    ylabel: [$V$ (cm³)],
    xlim: (0, 10),
    ylim: (0, 4500),
    
    lq.plot(
      lq.linspace(0.1, 10, num: 100),
      r => (4/3) * calc.pi * r*r*r,
      stroke: blue + 1.5pt,
      label: [$V = frac(4,3)pi r^3$]
    ),
    
    lq.scatter(
      (5,),
      ((4/3) * calc.pi * 125,),
      mark: "o",
      stroke: red,
      label: [$(5, frac(500 pi, 3))$]
    )
  ),
  caption: [Volume vs. radius for a sphere. The red dot marks the point of interest.]
) <fig:sphere-volume>

== Problem 4: Optimization

Find the dimensions of the rectangle with maximum area that can be inscribed in a semicircle of radius $R$.

*Setup:* Place the semicircle with its diameter on the x-axis, centered at the origin. The semicircle has equation $y = sqrt(R^2 - x^2)$.

*Hint:* Express the area in terms of one variable, then find critical points.

---

== Solutions (Hidden — Work Through Problems First!)

#box(stroke: gray + 0.5pt, inset: 1em, radius: 4pt)[
  *Spoiler Warning:* Solutions follow on the next pages. Try each problem before checking the answer.
]

#pagebreak()

=== Solution 1(a): Factoring

Factor numerator: $x^2 - 9 = (x - 3)(x + 3)$

Factor denominator: $x^2 - 5x + 6 = (x - 2)(x - 3)$

$ lim_(x -> 3) frac((x-3)(x+3), (x-2)(x-3)) = lim_(x -> 3) frac(x+3, x-2) = frac(6, 1) = 6 $

*Technique:* Factoring to resolve the removable discontinuity at $x = 3$.

=== Solution 1(b): Rationalizing

Multiply by conjugate $sqrt(1+x) + sqrt(1-x)$:

$ lim_(x -> 0) frac((1+x) - (1-x), x(sqrt(1+x) + sqrt(1-x))) = lim_(x -> 0) frac(2x, x(sqrt(1+x) + sqrt(1-x))) $

$ = lim_(x -> 0) frac(2, sqrt(1+x) + sqrt(1-x)) = frac(2, 1 + 1) = 1 $

=== Solution 1(c): Special Limits

$ lim_(x -> 0) frac(sin 3x, tan 5x) = lim_(x -> 0) frac(sin 3x, frac(sin 5x, cos 5x)) = lim_(x -> 0) frac(sin 3x cos 5x, sin 5x) $

Multiply and divide by appropriate terms:

$ = lim_(x -> 0) frac(sin 3x, 3x) dot frac(5x, sin 5x) dot frac(3x, 5x) dot cos 5x = 1 dot 1 dot frac(3, 5) dot 1 = frac(3, 5) $

=== Solution 1(d): L'Hôpital's Rule

Rewrite: $x ln x = frac(ln x, 1/x)$

As $x -> 0^+$: $ln x -> -infinity$ and $1/x -> +infinity$, so we have $frac(-infinity, +infinity)$.

Apply L'Hôpital:

$ lim_(x -> 0^+) frac(1/x, -1/x^2) = lim_(x -> 0^+) (-x) = 0 $

=== Solution 1(e): Limits at Infinity

Divide by $x^3$:

$ lim_(x -> infinity) frac(3 - 2/x^2 + 1/x^3, 5 + 4/x - 7/x^3) = frac(3, 5) $

All terms with $x$ in denominator approach 0.

#pagebreak()

=== Solution 2(a): Chain Rule

$ f'(x) = 5(3x^2 + 2x - 1)^4 dot (6x + 2) = 10(3x + 1)(3x^2 + 2x - 1)^4 $

=== Solution 2(b): Product Rule

$ g'(x) = 2x dot e^(3x) + x^2 dot 3e^(3x) = x e^(3x)(2 + 3x) $

=== Solution 2(c): Quotient Rule

$ h'(x) = frac(2x(x^2-1) - (x^2+1)(2x), (x^2-1)^2) = frac(2x^3 - 2x - 2x^3 - 2x, (x^2-1)^2) = frac(-4x, (x^2-1)^2) $

=== Solution 2(d): Implicit Differentiation

Differentiate: $3x^2 + 3y^2 y' = 6y + 6x y'$

Solve: $3y^2 y' - 6x y' = 6y - 3x^2$

$ y'(3y^2 - 6x) = 6y - 3x^2 $

$ y' = frac(6y - 3x^2, 3y^2 - 6x) = frac(2y - x^2, y^2 - 2x) $

=== Solution 2(e): Logarithmic Differentiation

$ ln y = sin x ln x $

$ frac(y', y) = cos x ln x + frac(sin x, x) $

$ y' = x^(sin x) (cos x ln x + frac(sin x, x)) $

#pagebreak()

=== Solution 3: Related Rates

Given: $V = frac(4, 3) pi r^3$

Differentiate with respect to $t$:

$ frac(d V, d t) = 4 pi r^2 frac(d r, d t) $

Solve for $frac(d r, d t)$:

$ frac(d r, d t) = frac(1, 4 pi r^2) frac(d V, d t) = frac(100, 4 pi (25)) = frac(100, 100 pi) = frac(1, pi) "cm""/""s" $

The radius is increasing at $frac(1, pi) approx 0.318 "cm""/""s"$ when $r = 5 "cm"$.

=== Solution 4: Optimization

Let the rectangle have width $2x$ (from $-x$ to $x$) and height $y = sqrt(R^2 - x^2)$.

Area: $A = 2x dot sqrt(R^2 - x^2) = 2x(R^2 - x^2)^(1/2)$

Find $frac(d A, d x)$:

$ frac(d A, d x) = 2(R^2 - x^2)^(1/2) + 2x dot 1/2 (R^2 - x^2)^(-1/2) (-2x) $

$ = 2sqrt(R^2 - x^2) - frac(2x^2, sqrt(R^2 - x^2)) = frac(2(R^2 - x^2) - 2x^2, sqrt(R^2 - x^2)) $

$ = frac(2R^2 - 4x^2, sqrt(R^2 - x^2)) $

Set equal to 0: $2R^2 - 4x^2 = 0 arrow x = R/sqrt(2)$

Height: $y = sqrt(R^2 - R^2/2) = sqrt(R^2/2) = R/sqrt(2)$

*Maximum area rectangle:*
- Width: $2x = R sqrt(2)$
- Height: $y = R/sqrt(2)$

The optimal rectangle has width $sqrt(2)R$ and height $R/sqrt(2)$, giving maximum area $A = R^2$.

---

*Exercise complete. When finished, mark this task as complete to continue.*