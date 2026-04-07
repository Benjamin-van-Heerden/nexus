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
