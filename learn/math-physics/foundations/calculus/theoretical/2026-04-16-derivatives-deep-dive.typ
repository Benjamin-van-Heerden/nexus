#set page(paper: "a4", margin: 2cm)
#set text(font: "New Computer Modern", size: 11pt)
#set par(justify: true, leading: 0.65em)
#set heading(numbering: "1.")
#show math.equation: set text(font: "New Computer Modern Math")

#import "@preview/lilaq:0.6.0" as lq

= Derivatives: A Deeper Look

This reading reinforces the core derivative concepts and focuses on building intuition for the applications you found challenging.

== The Derivative as Rate of Change

The derivative $f'(x)$ measures the *instantaneous* rate of change of $f$ at $x$. Geometrically, it's the slope of the tangent line. But more importantly, it answers:

#quote[At this exact moment, how fast is the quantity changing?]

This interpretation is crucial for related rates problems.

== Related Rates: The Strategy

Related rates problems involve quantities that change *together* over time. The key insight:

1. Identify what you're given ($frac(d x, d t)$, known values)
2. Identify what you want ($frac(d y, d t)$)
3. Find a *geometric relationship* connecting $x$ and $y$
4. Differentiate that relationship with respect to time $t$
5. Substitute and solve

The hard part is often step 3 — finding the right equation. Common relationships:

- *Pythagorean:* $x^2 + y^2 = z^2$ (ladder, distance)
- *Volume:* $V = pi r^2 h$ (conical tank, cylinder)
- *Similar triangles:* Maintains proportions as things scale
- *Area:* $A = pi r^2$, $A = x y$

*Key insight:* Draw the diagram. Label what's changing and what's constant.

== Optimization: Finding Extrema

Optimization means finding maximum or minimum values of a function.

=== The Procedure

1. Identify the quantity to optimize (call it $Q$)
2. Express $Q$ as a function of *one variable* (use constraints to eliminate others)
3. Find critical points: $Q'(x) = 0$ or where $Q'(x)$ DNE
4. Classify critical points (first or second derivative test)
5. Check endpoints if on a closed interval
6. Verify your answer makes physical sense

=== Common Pitfalls

- Forgetting domain restrictions
- Not checking endpoints on closed intervals
- Finding critical points but not verifying they're max/min
- Algebraic errors when simplifying the objective function

== Building Intuition

=== Why the Chain Rule Matters

When variables depend on each other, changes propagate. The chain rule captures this:

$ frac(d y, d t) = frac(d y, d x) dot frac(d x, d t) $

In related rates, we're often given $frac(d x, d t)$ and need $frac(d y, d t)$. The chain rule bridges them.

=== Implicit Differentiation Recap

When $y$ is defined implicitly by $F(x,y) = 0$:
1. Differentiate both sides with respect to $x$
2. Remember: $frac(d, d x)[y] = frac(d y, d x)$ (chain rule!)
3. Collect $frac(d y, d x)$ terms and solve

*Example:* $x^2 + y^2 = 25$
- Differentiate: $2x + 2y frac(d y, d x) = 0$
- Solve: $frac(d y, d x) = -frac(x, y)$

== Reflection Questions

1. In related rates, why must we differentiate *before* substituting numerical values? What goes wrong if we substitute first?

2. A common optimization pattern: "Find the maximum area of a rectangle with fixed perimeter." Why does the solution always turn out to be a square? What does this tell you about symmetry in optimization?

3. The derivative $f'(x)$ gives the rate of change. What does $f''(x)$ tell you about how that rate itself is changing? How is this useful in curve sketching?

4. L'Hôpital's rule requires an indeterminate form. Why can't we apply it to $lim_(x arrow 0) frac(sin x, x+1)$? What is the actual limit?

5. Draw a function that is: (a) increasing and concave up, (b) increasing and concave down, (c) decreasing and concave up. How do $f'$ and $f''$ differ in each case?
