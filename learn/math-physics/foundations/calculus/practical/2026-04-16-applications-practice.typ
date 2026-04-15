#set page(paper: "a4", margin: 2cm)
#set text(font: "New Computer Modern", size: 11pt)
#set par(justify: true, leading: 0.65em)
#set heading(numbering: "1.")
#show math.equation: set text(font: "New Computer Modern Math")

#import "@preview/lilaq:0.6.0" as lq

= Applications Practice: Related Rates & Optimization

This set focuses on the applications you found challenging. Each problem includes strategy hints — use them if you get stuck.

== Problem 1: Shadow Length (Related Rates)

A 2-meter tall man walks away from a 6-meter tall street lamp at a speed of 1.5 m/s. How fast is the length of his shadow increasing when he is 10 meters from the lamp?

*Strategy hint:* Draw the diagram. You'll have two similar right triangles. The lamp, the man, and the ground form one; the man, his shadow, and the ground form another.

#v(8cm)

== Problem 2: Draining Tank (Related Rates)

A conical tank with height 12 m and radius 4 m at the top is draining at 2 m³/min. How fast is the water level falling when the water is 6 m deep?

*Key relationship:* For a cone, $V = frac(1, 3) pi r^2 h$. But $r$ and $h$ are related by similar triangles: $frac(r, h) = frac(4, 12) = frac(1, 3)$, so $r = frac(h, 3)$. Substitute to get $V$ in terms of $h$ only.

#v(8cm)

== Problem 3: Maximum Volume Box (Optimization)

A rectangular sheet of cardboard measures 20 cm by 30 cm. Equal squares are cut from each corner, and the sides are folded up to form an open-top box. What size squares should be cut to maximize the volume?

*Strategy hint:* If the square cut from each corner has side $x$, what are the dimensions of the box? What's the constraint on $x$?

#v(8cm)

== Problem 4: Closest Point on a Curve (Optimization)

Find the point on the curve $y = sqrt(x)$ that is closest to the point $(4, 0)$.

*Strategy hint:* Minimize the *distance squared* (it's easier than minimizing distance, and gives the same answer). Distance squared from $(x, sqrt(x))$ to $(4, 0)$ is $D^2 = (x-4)^2 + (sqrt(x) - 0)^2$.

#v(8cm)

== Problem 5: Limit with L'Hôpital's Rule

Evaluate: $lim_(x arrow 0^+) x ln x$

*Strategy hint:* This is an indeterminate form $0 dot (-infinity)$. Rewrite as a fraction to apply L'Hôpital's rule. Which way should you rewrite: $frac(ln x, 1/x)$ or $frac(x, 1/ln x)$? Try both mentally — which looks easier to differentiate?

#v(8cm)

== Solutions

*Solution 1:* Let $x$ = distance from man to lamp, $s$ = shadow length. By similar triangles: $frac(6, x+s) = frac(2, s)$. Solve for relationship, differentiate with respect to $t$, substitute $frac(d x, d t) = 1.5$ and $x = 10$. Shadow grows at 0.75 m/s (independent of $x$!).

*Solution 2:* Substitute $r = h/3$ into volume: $V = frac(pi, 27) h^3$. Differentiate: $frac(d V, d t) = frac(pi, 9) h^2 frac(d h, d t)$. With $frac(d V, d t) = -2$ and $h = 6$: $frac(d h, d t) = -frac(1, 2 pi) approx -0.159$ m/min.

*Solution 3:* Box dimensions: $(20-2x) times (30-2x) times x$. Volume $V(x) = 4x^3 - 100x^2 + 600x$. Constraint: $0 < x < 10$. Critical point: $V'(x) = 12x^2 - 200x + 600 = 0$. Solving: $x = frac(25 - 5sqrt(7), 3) approx 3.92$ cm (other root is outside domain).

*Solution 4:* $D^2 = (x-4)^2 + x$. Derivative: $2(x-4) + 1 = 0$, so $x = 7/2 = 3.5$. Closest point: $(3.5, sqrt(3.5))$.

*Solution 5:* Rewrite: $lim_(x arrow 0^+) frac(ln x, 1/x)$. This is $-infinity / +infinity$, so apply L'Hôpital: $lim frac(1/x, -1/x^2) = lim (-x) = 0$.
