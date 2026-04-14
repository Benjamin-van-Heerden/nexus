# Math-Physics Topic

## Background

The user comes from a math and physics background but are rusty. Goals:
- Mathematics of Quantitative Finance
- Quantum Computing

## Exercise Types

- **practical** — 1-2 worked problems to solidify concepts
- **theoretical** — reading notes + reflection questions  
- **quiz** — multiple choice questions

All exercises should be in typst format and compiled to pdf.

## Diagrams and Charts: Typst

All diagrams and charts in this topic are created with **Typst** — a modern, open-source typesetting system written in Rust. It is far simpler than LaTeX while producing publication-quality PDFs with excellent math support.

### How It Works

1. Write a `.typ` file with markup + code
2. Compile to PDF: `typst compile file.typ` - any typst files *must* be compiled to pdfs before they are presented to Benjamin (this ensures they are valid and in working order)
NB: After creating *any* .typ file, it must be compiled to pdf (just point it at the file, it will create the pdf in the same location as the the .typ file). If it doesn't compile, use the warnings as a guide to fix the file and then compile to pdf again.
3. Always present the pdf file to the user in output, not the raw .typ file.

### Packages Used

This topic uses three Typst packages:

| Package | Purpose | Import |
|---------|---------|--------|
| **lilaq** | 2D charts (lines, bars, scatter, heatmaps, etc.) | `#import "@preview/lilaq:0.6.0" as lq` |
| **plotsy-3d** | 3D plots (surfaces, parametric curves, vector fields) | `#import "@preview/plotsy-3d:0.2.1": *` |
| **cetz** | General diagrams (state machines, trees, flowcharts, custom drawings) | `#import "@preview/cetz:0.5.0": *` |

Packages are auto-downloaded by Typst on first compile.

---

## 2D Charts: Lilaq

Lilaq is a comprehensive 2D plotting library. It produces vector-quality plots suitable for academic papers.

### Basic Syntax

```typst
#import "@preview/lilaq:0.6.0" as lq

#let xs = lq.linspace(0, 2 * calc.pi, num: 100)

#lq.diagram(
  xlabel: $x$,
  ylabel: $sin(x)$,
  lq.plot(xs, calc.sin, label: [$sin(x)$]),
  lq.plot(xs, calc.cos, label: [$cos(x)$]),
)
```

### Common Plot Types

| Function | Use Case |
|----------|----------|
| `lq.plot(xs, y_fn)` | Line plots, function plots |
| `lq.scatter(x, y)` | Scatter plots with variable size/color |
| `lq.fill-between(xs, y1, y2: y2)` | Shaded regions |
| `lq.bar(xs, ys)` | Bar charts |
| `lq.stem(xs, ys)` | Stem/lollipop plots (discrete data) |
| `lq.boxplot(data...)` | Box-and-whisker plots |
| `lq.contour(xs, ys, z_fn)` | Contour plots |
| `lq.colormesh(xs, ys, z_matrix)` | Heatmaps |
| `lq.quiver(xs, ys, (x,y) => (u,v))` | Vector fields |

### Axis Scales

```typst
lq.diagram(
  xscale: "linear",  // default
  yscale: "log",      // logarithmic (great for exponential growth)
  // or "symlog", "datetime"
)
```

### Logarithmic Scales Example (Finance)

```typst
#let ns = lq.linspace(1, 100, num: 200)

#lq.diagram(
  xlabel: $n$,
  ylabel: [Time],
  yscale: "log",  // critical for showing polynomial vs exponential
  lq.plot(ns, n => n, label: [$O(n)$]),
  lq.plot(ns, n => n * calc.log(n + 1), label: [$O(n log n)$]),
  lq.plot(ns, n => n * n, label: [$O(n^2)$]),
  lq.plot(ns, n => calc.pow(2, n / 10), label: [$O(2^n)$]),
)
```

### Bar Charts (Portfolio Allocation)

```typst
#let categories = ("Equities", "Bonds", "Real Estate", "Cash")
#let values = (45, 30, 15, 10)

#lq.diagram(
  xlabel: [Asset Class],
  ylabel: [Allocation %],
  lq.bar(range(4), values, fill: blue),
)
```

### Box Plots (Statistical Comparison)

```typst
#lq.diagram(
  xlabel: [Group],
  ylabel: [Value],
  lq.boxplot(data1, data2, data3, fill: yellow),
)
```

### Scatter with Color Coding (Multivariate)

```typst
#lq.scatter(
  x, y,
  color: z_values,
  map: color.map.viridis,
)
```

### Filling Under a Curve (Integrals, Probabilities)

```typst
#lq.fill-between(
  xs,
  xs.map(x => x * x * calc.exp(-x)),
  label: [$x^2 e^{-x}$]
)
```

### Complete Example: Sine Waves

```typst
#import "@preview/lilaq:0.6.0" as lq

#let xs = lq.linspace(0, 2 * calc.pi, num: 150)

#lq.diagram(
  width: 10cm,
  height: 6cm,
  xlabel: $theta$,
  ylabel: $f(theta)$,
  xlim: (0, 2 * calc.pi),
  grid: (stroke: gray + 0.3pt),
  lq.plot(xs, calc.sin, label: [$sin theta$], stroke: blue + 1.5pt),
  lq.plot(xs, calc.cos, label: [$cos theta$], stroke: red + 1.5pt),
  lq.hlines(0, stroke: black + 0.5pt),
)
```

---

## 3D Plots: Plotsy-3d

For 3D surface plots, parametric surfaces, and vector fields.

### Import and Basic Surface

```typst
#import "@preview/plotsy-3d:0.2.1": plot-3d-surface

#let func(x, y) = calc.sin(x) * calc.cos(y)

#plot-3d-surface(
  func,
  xdomain: (-calc.pi, calc.pi),
  ydomain: (-calc.pi, calc.pi),
  subdivisions: 3,
)
```

### Parametric Surface (Sphere)

```typst
#import "@preview/plotsy-3d:0.2.1": plot-3d-parametric-surface

#let xfunc(u, v) = calc.sin(u) * calc.cos(v)
#let yfunc(u, v) = calc.sin(u) * calc.sin(v)
#let zfunc(u, v) = calc.cos(u)

#plot-3d-parametric-surface(
  xfunc, yfunc, zfunc,
  udomain: (0, calc.pi),
  vdomain: (0, 2 * calc.pi),
)
```

### Vector Field

```typst
#import "@preview/plotsy-3d:0.2.1": plot-3d-vector-field

#let i-func(x,y,z) = y
#let j-func(x,y,z) = -x
#let k-func(x,y,z) = z

#plot-3d-vector-field(i-func, j-func, k-func, subdivisions: 2)
```

---

## Diagrams: CeTZ

For custom diagrams not covered by lilaq — state machines, trees, flowcharts, Markov chains, Feynman diagrams, etc.

### Basic Canvas

```typst
#import "@preview/cetz:0.5.0"

#cetz.canvas({
  import cetz.draw: *
  
  // Drawing commands
  circle((0, 0), radius: 0.5)
  line((0, 0), (3, 0), mark: (end: ">"))
})
```

### Coordinates

| Format | Example | Description |
|--------|---------|-------------|
| Absolute | `(0, 0)` | 2D point |
| Relative | `(rel: (1, 0))` | Offset from previous |
| Polar | `(30deg, 2)` | Angle, radius |
| Named | `"state-A.east"` | Anchor on named element |

### State Machine / Markov Chain

```typst
#cetz.canvas({
  import cetz.draw: *

  // States
  circle((0, 0), radius: 0.5, name: "s0", fill: white)
  content("s0", [$S_0$])
  
  circle((4, 0), radius: 0.5, name: "s1", fill: white)
  content("s1", [$S_1$])

  // Transition with probability
  bezier("s0.north-east", "s1.north-west",
         (1.5, 1.2), (2.5, 1.2),
         mark: (end: ">"))
  content(("s0.north-east", 50%, "s1.north-west"), [$0.3$], anchor: "south")
  
  // Self-loop
  arc("s0.north", start: 120deg, stop: 60deg, radius: 0.6,
      mark: (end: ">"))
  content((0, 1.6), [$0.7$])
})
```

### Decision Tree / Parse Tree

```typst
#cetz.canvas({
  import cetz.draw: *

  tree.tree(
    ([$S$],
      ([$A$], [$a_1$], [$a_2$]),
      ([$B$], [$b_1$])),
    draw-node: (node, ..) => {
      circle((), radius: 0.35, fill: blue.lighten(70%))
      content((), node.content)
    },
    draw-edge: (from, to, ..) => {
      line(from, to, mark: (end: ">"))
    },
    grow: 1.5,
    spread: 1.2,
  )
})
```

### Flowchart

```typst
#cetz.canvas({
  import cetz.draw: *

  // Start
  content((0, 0), [Start], frame: "rect", name: "start",
          padding: 0.2, fill: green.lighten(80%))
  
  // Decision
  content((0, -2), [$x > 0$?], frame: "rect", name: "dec",
          padding: 0.2, fill: yellow.lighten(70%))
  
  // Branches
  content((-2, -4), [Yes], name: "yes")
  content((2, -4), [No], name: "no")
  
  // End
  content((0, -6), [End], frame: "rect", name: "end",
          padding: 0.2, fill: green.lighten(80%))
  
  // Arrows
  line("start", "dec")
  line("dec", "yes", bend: -30deg)
  line("dec", "no", bend: 30deg)
  line("yes", "end")
  line("no", "end")
})
```

---

## Practical Exercise Workflow

When creating a **practical** exercise:

1. Create a `.typ` file in `practical/`
2. Write the problem statement in markdown at the top
3. Include a complete, runnable Typst document with:
   - Necessary imports
   - Any diagrams/charts that illustrate the problem or solution
   - Step-by-step solution with reasoning
4. Compile locally to verify: `typst compile practical/YYYY-MM-DD-slug.typ`
5. Tell the user the absolute path and what to do

### Example File Structure

```
practical/
├── 2026-04-02-derivative-basics.md    # The exercise description
├── 2026-04-02-derivative-basics.typ   # Typst source for diagrams
└── 2026-04-02-derivative-basics.pdf  # Compiled output (optional)
```

### Key Guidelines

- Always verify the Typst compiles before handing to user
- Keep diagrams simple and clear — they illustrate concepts, not replace them
- Use appropriate plot types:
  - Function behavior → `lq.plot` with lines
  - Data comparison → `lq.bar` or `lq.boxplot`
  - Continuous vs discrete → `lq.plot` vs `lq.stem`
  - 3D functions → `plot-3d-surface`
  - State/transition systems → CeTZ
- Label all axes
- Include units where applicable
- Use log scales when showing exponential/polynomial growth

---

## Quick Reference

### Compile Typst
```bash
typst compile file.typ          # → file.pdf
typst watch file.typ            # live preview
```

### Package Imports
```typst
# 2D charts
#import "@preview/lilaq:0.6.0" as lq

# 3D plots  
#import "@preview/plotsy-3d:0.2.1": plot-3d-surface, plot-3d-parametric-surface

# Diagrams
#import "@preview/cetz:0.5.0"
```

### Common lilaq Functions
- `lq.linspace(start, end)` — 50 evenly spaced points
- `lq.plot(xs, y_fn)` — line plot
- `lq.bar(xs, ys)` — bar chart
- `lq.boxplot(data...)` — box plot
- `lq.fill-between(xs, y1, y2: y2)` — shaded region

### Common CeTZ Functions
- `circle(pos, radius: n)` — circle
- `rect((x1,y1), (x2,y2))` — rectangle
- `line(from, to)` — straight line
- `bezier(from, to, c1, c2)` — cubic bezier
- `arc(pos, start, stop, radius)` — arc
- `content(pos, [text])` — place text
- `tree.tree(data, ...)` — tree layout

### Full Example

```typst
#import "@preview/lilaq:0.6.0" as lq
#import "@preview/physica:0.9.8": *
#import "@preview/plotsy-3d:0.2.1": plot-3d-surface

#set page(paper: "a4", margin: 2cm)
#set text(font: "New Computer Modern", size: 11pt)
#set par(justify: true, leading: 0.65em)
#set heading(numbering: "1.")

#show math.equation: set text(font: "New Computer Modern Math")

= Typst + Lilaq + Physica: Scientific Document Example

This single file demonstrates high-quality typesetting for mathematics, quantum mechanics, statistics, and finance-related visualizations.

== Quantum Mechanics Equations

The time-independent Schrödinger equation in one dimension reads:

$ -frac(hbar^2, 2m) frac(d^2, d x^2) psi(x) + V(x) psi(x) = E psi(x) $

A common normalized Gaussian wave packet is:

$ psi(x) = frac(1, (sigma sqrt(2 pi))^(1/2)) exp(-frac(x^2, 4 sigma^2)) $

Using Dirac notation (imported from physica):

$ ket(psi) = alpha ket(0) + beta ket(1) quad text("with") quad |alpha|^2 + |beta|^2 = 1 $

The inner product is:

$ bra(phi) ket(psi) = integral phi^*(x) psi(x) , d x $

== 2D Charts with Lilaq

=== Line Plots of Mathematical Functions

#figure(
  lq.diagram(
    title: [Mathematical Functions],
    xlabel: $x$,
    ylabel: $y$,
    width: 85%,

    lq.plot(
      range(-5, 6),
      x => x*x / 5,
      mark: "o",
      label: [Quadratic $x^2/5$]
    ),
    lq.plot(
      lq.linspace(-5, 5, num: 150),
      x => 4 * calc.cos(2*x) + 1,
      mark: none,
      label: [Cosine wave]
    )
  ),
  caption: [Line plots created with Lilaq. Functions are evaluated directly inside Typst.]
) <fig:line-plots>

=== Contour Plot (2D Wave-like Function)

#figure(
  lq.diagram(
    title: [Contour Plot of 2D Function],
    xlabel: $x$,
    ylabel: $y$,
    width: 85%,

    lq.contour(
      lq.linspace(-4, 4, num: 50),
      lq.linspace(-4, 4, num: 50),
      (x, y) => calc.cos(x) * calc.sin(y) * calc.exp(-(x*x + y*y)/5),
      levels: 12,
      map: color.map.viridis
    )
  ),
  caption: [Contour plot using Lilaq. Useful for quantum mechanics probability densities or potential surfaces.]
) <fig:contour>

=== Quiver Plot (Vector Field)

#figure(
  lq.diagram(
    title: [Vector Field (Quiver)],
    xlabel: $x$,
    ylabel: $y$,
    width: 85%,

    lq.quiver(
      lq.linspace(-3, 3, num: 12),
      lq.linspace(-3, 3, num: 12),
      (x, y) => (-y/2, x/2)
    )
  ),
  caption: [Quiver plot showing a rotational vector field with Lilaq.]
) <fig:quiver>

== 3D Surface Plot with plotsy-3d (Smaller Size)

A compact 3D surface of the function $z = sin(x) cos(y) exp(-(x^2 + y^2)/8)$.

#figure(
  {
    let size = 3          // integer domain to avoid type errors
    let scale-factor = 0.3
    let (xscale, yscale, zscale) = (0.35, 0.35, 0.25)
    let scale-dim = (
      xscale * scale-factor,
      yscale * scale-factor,
      zscale * scale-factor
    )

    plot-3d-surface(
      (x, y) => calc.sin(x) * calc.cos(y) * calc.exp(-(x*x + y*y)/8),
      xdomain: (-size, size),
      ydomain: (-size, size),
      subdivisions: 25,
      scale-dim: scale-dim
    )
  },
  caption: [3D surface plot with plotsy-3d]
) <fig:3d-surface>
```
