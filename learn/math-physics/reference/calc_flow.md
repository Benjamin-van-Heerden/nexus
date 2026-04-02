# Calculus: Flow

Multidimensional calculus — extending the concepts of calculus to functions of several variables. Covers vectors, partial derivatives, multiple integrals, and vector calculus.

---

## 1. Vectors and Geometry

### 1.1 Vectors in $\mathbb{R}^n$

A vector $\mathbf{v} = \langle v_1, v_2, \ldots, v_n \rangle$ represents a directed line segment from the origin to the point $(v_1, v_2, \ldots, v_n)$.

**Operations:**
- Addition: $\mathbf{u} + \mathbf{v} = \langle u_1+v_1, \ldots, u_n+v_n \rangle$
- Scalar multiplication: $c\mathbf{v} = \langle cv_1, \ldots, cv_n \rangle$
- Dot product: $\mathbf{u} \cdot \mathbf{v} = \sum_{i=1}^n u_i v_i$
- Cross product (in $\mathbb{R}^3$): $\mathbf{u} \times \mathbf{v}$

**Magnitude (Length):**
$$\|\mathbf{v}\| = \sqrt{v_1^2 + v_2^2 + \cdots + v_n^2}$$

**Unit Vector:**
$$\hat{\mathbf{v}} = \frac{\mathbf{v}}{\|\mathbf{v}\|}$$

### 1.2 Dot Product

$$\mathbf{u} \cdot \mathbf{v} = \|\mathbf{u}\| \|\mathbf{v}\| \cos \theta$$
where $\theta$ is the angle between $\mathbf{u}$ and $\mathbf{v}$.

**Properties:**
- $\mathbf{u} \cdot \mathbf{v} = \mathbf{v} \cdot \mathbf{u}$
- $\mathbf{u} \cdot (\mathbf{v} + \mathbf{w}) = \mathbf{u} \cdot \mathbf{v} + \mathbf{u} \cdot \mathbf{w}$
- $(c\mathbf{u}) \cdot \mathbf{v} = c(\mathbf{u} \cdot \mathbf{v})$
- $\mathbf{v} \cdot \mathbf{v} = \|\mathbf{v}\|^2$

**Perpendicular (Orthogonal):** $\mathbf{u} \cdot \mathbf{v} = 0$

**Projection of $\mathbf{u}$ onto $\mathbf{v}$:**
$$\text{proj}_{\mathbf{v}} \mathbf{u} = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{v}\|^2} \mathbf{v}$$

### 1.3 Cross Product

In $\mathbb{R}^3$:
$$\mathbf{u} \times \mathbf{v} = \langle u_2v_3 - u_3v_2, u_3v_1 - u_1v_3, u_1v_2 - u_2v_1 \rangle$$

**Properties:**
- $\mathbf{u} \times \mathbf{v}$ is perpendicular to both $\mathbf{u}$ and $\mathbf{v}$
- $\|\mathbf{u} \times \mathbf{v}\| = \|\mathbf{u}\| \|\mathbf{v}\| \sin \theta$
- $\mathbf{u} \times \mathbf{v} = -\mathbf{v} \times \mathbf{u}$
- $\mathbf{u} \times \mathbf{u} = \mathbf{0}$

**Geometric Interpretation:** Area of parallelogram spanned by $\mathbf{u}$ and $\mathbf{v}$ is $\|\mathbf{u} \times \mathbf{v}\|$.

### 1.4 Lines and Planes in $\mathbb{R}^3$

**Line through $\mathbf{r}_0$ with direction $\mathbf{v}$:**
$$\mathbf{r}(t) = \mathbf{r}_0 + t\mathbf{v}$$

**Plane through $\mathbf{r}_0$ with normal $\mathbf{n}$:**
$$\mathbf{n} \cdot (\mathbf{r} - \mathbf{r}_0) = 0$$
or $ax + by + cz = d$

**Distance from point to plane:**
$$\frac{|ax_0 + by_0 + cz_0 - d|}{\sqrt{a^2 + b^2 + c^2}}$$

---

## 2. Partial Derivatives

### 2.1 Functions of Several Variables

$z = f(x, y)$ defines a surface in $\mathbb{R}^3$.

**Domain:** Set of all $(x, y)$ where $f$ is defined.

**Level Curves:** Curves where $f(x, y) = k$ for constant $k$.

### 2.2 Limits and Continuity

**Limit:**
$$\lim_{(x,y) \to (a,b)} f(x, y) = L$$

The limit must be the same along all paths.

**Continuity:** $f$ is continuous at $(a,b)$ if $\lim_{(x,y) \to (a,b)} f(x,y) = f(a,b)$.

### 2.3 Partial Derivatives

**With respect to $x$:**
$$f_x = \frac{\partial f}{\partial x} = \lim_{h \to 0} \frac{f(x+h, y) - f(x,y)}{h}$$

Treat $y$ as constant and differentiate with respect to $x$.

**With respect to $y$:**
$$f_y = \frac{\partial f}{\partial y} = \lim_{h \to 0} \frac{f(x, y+h) - f(x,y)}{h}$$

Treat $x$ as constant and differentiate with respect to $y$.

### 2.4 Higher Order Derivatives

$$f_{xx} = \frac{\partial^2 f}{\partial x^2}, \quad f_{yy} = \frac{\partial^2 f}{\partial y^2}$$
$$f_{xy} = \frac{\partial}{\partial y}\left(\frac{\partial f}{\partial x}\right) = \frac{\partial^2 f}{\partial y \partial x}$$
$$f_{yx} = \frac{\partial}{\partial x}\left(\frac{\partial f}{\partial y}\right) = \frac{\partial^2 f}{\partial x \partial y}$$

**Clairaut's Theorem:** If $f_{xy}$ and $f_{yx}$ are continuous, then $f_{xy} = f_{yx}$.

### 2.5 Differentials and Linear Approximation

**Total Differential:**
$$dz = f_x \, dx + f_y \, dy$$

**Linear Approximation:**
$$L(x, y) = f(a, b) + f_x(a,b)(x-a) + f_y(a,b)(y-b)$$

**Differential of $f$:**
$$df = f_x \, dx + f_y \, dy$$

### 2.6 The Chain Rule

**Case 1:** $z = f(x, y)$, where $x = g(t), y = h(t)$
$$\frac{dz}{dt} = \frac{\partial f}{\partial x}\frac{dx}{dt} + \frac{\partial f}{\partial y}\frac{dy}{dt}$$

**Case 2:** $z = f(x, y)$, where $x = g(s, t), y = h(s, t)$
$$\frac{\partial z}{\partial s} = \frac{\partial f}{\partial x}\frac{\partial x}{\partial s} + \frac{\partial f}{\partial y}\frac{\partial y}{\partial s}$$
$$\frac{\partial z}{\partial t} = \frac{\partial f}{\partial x}\frac{\partial x}{\partial t} + \frac{\partial f}{\partial y}\frac{\partial y}{\partial t}$$

### 2.7 Implicit Differentiation

For $F(x, y, z) = 0$ defining $z = f(x, y)$:
$$\frac{\partial z}{\partial x} = -\frac{F_x}{F_z}, \quad \frac{\partial z}{\partial y} = -\frac{F_y}{F_z}$$

### 2.8 Directional Derivatives

The rate of change of $f$ in direction of unit vector $\mathbf{u} = \langle u_1, u_2 \rangle$:
$$D_{\mathbf{u}} f = \nabla f \cdot \mathbf{u}$$

where $\nabla f$ (gradient) is:
$$\nabla f = \langle f_x, f_y \rangle$$

**Properties:**
- $\nabla f$ points in the direction of maximum increase
- The maximum directional derivative is $\|\nabla f\|$
- The minimum directional derivative is $-\|\nabla f\|$
- $\nabla f \cdot \mathbf{u} = 0$ when $\mathbf{u}$ is perpendicular to level curves

### 2.9 Gradient and Tangent Planes

**Tangent Plane to $z = f(x, y)$ at $(a, b, f(a,b))$:**
$$z - f(a,b) = f_x(a,b)(x-a) + f_y(a,b)(y-b)$$

**For $F(x, y, z) = 0$:**
$$F_x(a,b,c)(x-a) + F_y(a,b,c)(y-b) + F_z(a,b,c)(z-c) = 0$$

### 2.10 Maxima and Minima

**Critical Points:** Where $f_x = 0$ and $f_y = 0$, or where derivatives don't exist.

**Second Derivatives Test:**
Let $D = f_{xx}f_{yy} - f_{xy}^2$ at critical point $(a, b)$.

- If $D > 0$ and $f_{xx} > 0$: local minimum
- If $D > 0$ and $f_{xx} < 0$: local maximum
- If $D < 0$: saddle point
- If $D = 0$: test inconclusive

**Absolute Extrema:** On a closed bounded region, check:
1. Critical points in interior
2. Boundary extrema

### 2.11 Lagrange Multipliers

For optimizing $f(x, y, z)$ subject to constraint $g(x, y, z) = k$:

Solve:
$$\nabla f = \lambda \nabla g$$
$$g(x, y, z) = k$$

**Interpretation:** At extrema, $\nabla f$ is parallel to $\nabla g$.

---

## 3. Multiple Integrals

### 3.1 Double Integrals over Rectangles

$$\iint_R f(x, y) \, dA = \lim_{m,n \to \infty} \sum_{i=1}^m \sum_{j=1}^n f(x_{ij}^*, y_{ij}^*) \Delta x \Delta y$$

**Iterated Integration (Fubini's Theorem):**
$$\iint_R f(x, y) \, dA = \int_a^b \int_c^d f(x, y) \, dy \, dx = \int_c^d \int_a^b f(x, y) \, dx \, dy$$

### 3.2 Double Integrals over General Regions

**Type I (vertical slices):**
$$D = \{(x, y): a \leq x \leq b, g_1(x) \leq y \leq g_2(x)\}$$
$$\iint_D f(x, y) \, dA = \int_a^b \int_{g_1(x)}^{g_2(x)} f(x, y) \, dy \, dx$$

**Type II (horizontal slices):**
$$D = \{(x, y): c \leq y \leq d, h_1(y) \leq x \leq h_2(y)\}$$
$$\iint_D f(x, y) \, dA = \int_c^d \int_{h_1(y)}^{h_2(y)} f(x, y) \, dx \, dy$$

### 3.3 Double Integrals in Polar Coordinates

$$x = r \cos \theta, \quad y = r \sin \theta$$
$$dA = r \, dr \, d\theta$$

$$\iint_D f(x, y) \, dA = \int_{\theta_1}^{\theta_2} \int_{r_1(\theta)}^{r_2(\theta)} f(r \cos \theta, r \sin \theta) \, r \, dr \, d\theta$$

### 3.4 Triple Integrals

$$\iiint_E f(x, y, z) \, dV$$

**In rectangular coordinates:**
$$\int_a^b \int_{y_1(x)}^{y_2(x)} \int_{z_1(x,y)}^{z_2(x,y)} f(x, y, z) \, dz \, dy \, dx$$

**Order matters:** Choose based on region shape and integration ease.

### 3.5 Triple Integrals in Cylindrical Coordinates

$$x = r \cos \theta, \quad y = r \sin \theta, \quad z = z$$
$$dV = r \, dr \, d\theta \, dz$$

### 3.6 Triple Integrals in Spherical Coordinates

$$x = \rho \sin \phi \cos \theta$$
$$y = \rho \sin \phi \sin \theta$$
$$z = \rho \cos \phi$$

where:
- $\rho \geq 0$ (distance from origin)
- $0 \leq \phi \leq \pi$ (angle from positive z-axis)
- $0 \leq \theta < 2\pi$ (angle in xy-plane from positive x-axis)

$$dV = \rho^2 \sin \phi \, d\rho \, d\phi \, d\theta$$

**Useful for:** Spheres, cones, and spherical shells.

### 3.7 Applications of Multiple Integrals

**Area of Region $D$:**
$$A = \iint_D 1 \, dA$$

**Volume:**
$$V = \iiint_E 1 \, dV$$

**Mass with density $\rho(x, y)$:**
$$M = \iint_D \rho(x, y) \, dA$$

**Center of Mass:**
$$\bar{x} = \frac{1}{M}\iint_D x \rho(x, y) \, dA, \quad \bar{y} = \frac{1}{M}\iint_D y \rho(x, y) \, dA$$

---

## 4. Vector Calculus

### 4.1 Vector Fields

A vector field assigns a vector to each point:
$$\mathbf{F}(x, y) = \langle P(x, y), Q(x, y) \rangle$$
$$\mathbf{F}(x, y, z) = \langle P(x, y, z), Q(x, y, z), R(x, y, z) \rangle$$

**Conservative Fields:** If $\mathbf{F} = \nabla f$ for some scalar potential function $f$.

**Test for conservativeness (simply connected region):**
- 2D: $\frac{\partial P}{\partial y} = \frac{\partial Q}{\partial x}$
- 3D: $\nabla \times \mathbf{F} = \mathbf{0}$

### 4.2 Line Integrals

**Line integral of scalar function:**
$$\int_C f(x, y) \, ds = \int_a^b f(\mathbf{r}(t)) \|\mathbf{r}'(t)\| \, dt$$
where $ds = \|\mathbf{r}'(t)\| \, dt$ is arc length.

**Line integral of vector field:**
$$\int_C \mathbf{F} \cdot d\mathbf{r} = \int_a^b \mathbf{F}(\mathbf{r}(t)) \cdot \mathbf{r}'(t) \, dt$$

**Work done by force $\mathbf{F}$ along $C$:**
$$W = \int_C \mathbf{F} \cdot d\mathbf{r}$$

**Fundamental Theorem for Line Integrals:**
If $\mathbf{F}$ is conservative, then $\int_C \mathbf{F} \cdot d\mathbf{r} = f(\text{end}) - f(\text{start})$

### 4.3 Green's Theorem

For a positively oriented, simple closed curve $C$ bounding region $D$:
$$\oint_C \mathbf{F} \cdot d\mathbf{r} = \iint_D \left(\frac{\partial Q}{\partial x} - \frac{\partial P}{\partial y}\right) \, dA$$

where $\mathbf{F} = \langle P, Q \rangle$.

**Interpretation:** Line integral around closed curve equals double integral of curl over region.

**Alternative form (area):**
$$A = \frac{1}{2} \oint_C (x \, dy - y \, dx)$$

### 4.4 Curl and Divergence

**Curl (2D):**
$$\text{curl } \mathbf{F} = \frac{\partial Q}{\partial x} - \frac{\partial P}{\partial y}$$

**Curl (3D):**
$$\nabla \times \mathbf{F} = \begin{vmatrix} \mathbf{i} & \mathbf{j} & \mathbf{k} \\ \frac{\partial}{\partial x} & \frac{\partial}{\partial y} & \frac{\partial}{\partial z} \\ P & Q & R \end{vmatrix}$$

**Interpretation:** Curl measures rotation (vorticity) of the field.

**Divergence:**
$$\nabla \cdot \mathbf{F} = \frac{\partial P}{\partial x} + \frac{\partial Q}{\partial y} + \frac{\partial R}{\partial z}$$

**Interpretation:** Divergence measures "source strength" at a point.

### 4.5 Surface Integrals

**Surface integral of scalar function:**
$$\iint_S f(x, y, z) \, dS$$

where $dS$ is surface area element.

**For $z = g(x, y)$:**
$$dS = \sqrt{1 + g_x^2 + g_y^2} \, dA$$

**Surface integral of vector field:**
$$\iint_S \mathbf{F} \cdot d\mathbf{S} = \iint_S \mathbf{F} \cdot \mathbf{n} \, dS$$

where $\mathbf{n}$ is unit normal.

**Flux:** The net amount of fluid flowing through surface per unit time.

### 4.6 Stokes' Theorem

For surface $S$ with boundary curve $C$:
$$\oint_C \mathbf{F} \cdot d\mathbf{r} = \iint_S (\nabla \times \mathbf{F}) \cdot \mathbf{n} \, dS$$

**Interpretation:** Line integral around boundary equals surface integral of curl.

### 4.7 The Divergence Theorem

For solid region $E$ with boundary surface $S$:
$$\iint_S \mathbf{F} \cdot \mathbf{n} \, dS = \iiint_E (\nabla \cdot \mathbf{F}) \, dV$$

**Interpretation:** Total flux outward through boundary equals triple integral of divergence.

---

## 5. Quick Reference

### 5.1 Vector Operations

| Operation | Formula |
|-----------|---------|
| Magnitude | $\|\mathbf{v}\| = \sqrt{v_1^2 + v_2^2 + v_3^2}$ |
| Dot product | $\mathbf{u} \cdot \mathbf{v} = u_1v_1 + u_2v_2 + u_3v_3$ |
| Cross product | $\mathbf{u} \times \mathbf{v}$ (perpendicular to both) |
| Projection | $\text{proj}_{\mathbf{v}} \mathbf{u} = \frac{\mathbf{u} \cdot \mathbf{v}}{\\|\mathbf{v}\\|^2} \mathbf{v}$ |

### 5.2 Gradient, Divergence, Curl

| Operation | 2D | 3D |
|-----------|-----|-----|
| Gradient | $\nabla f = \langle f_x, f_y \rangle$ | $\nabla f = \langle f_x, f_y, f_z \rangle$ |
| Divergence | $P_x + Q_y$ | $P_x + Q_y + R_z$ |
| Curl | $Q_x - P_y$ | $\langle R_y - Q_z, P_z - R_x, Q_x - P_y \rangle$ |

### 5.3 Integration Theorems

| Theorem | Statement |
|---------|-----------|
| Fubini | Double integral = iterated integral |
| Fundamental (line integrals) | Conservative field: $\int_C \nabla f \cdot d\mathbf{r} = f(B) - f(A)$ |
| Green | $\oint_C \mathbf{F} \cdot d\mathbf{r} = \iint_D (\text{curl } \mathbf{F}) \, dA$ |
| Stokes | $\oint_C \mathbf{F} \cdot d\mathbf{r} = \iint_S (\nabla \times \mathbf{F}) \cdot \mathbf{n} \, dS$ |
| Divergence | $\iint_S \mathbf{F} \cdot \mathbf{n} \, dS = \iiint_E (\nabla \cdot \mathbf{F}) \, dV$ |

### 5.4 Coordinate Transformations

| Coordinate | Relationships | Jacobian |
|------------|---------------|----------|
| Polar | $x = r\cos\theta, y = r\sin\theta$ | $r$ |
| Cylindrical | $x = r\cos\theta, y = r\sin\theta, z = z$ | $r$ |
| Spherical | $x = \rho\sin\phi\cos\theta, y = \rho\sin\phi\sin\theta, z = \rho\cos\phi$ | $\rho^2\sin\phi$ |

---

## 6. Exercises Guidance

For this material, create exercises requiring:

1. **Vectors** — Vector operations (dot product, cross product, projections), equations of lines and planes, distances.

2. **Partial Derivatives** — Computing partials, mixed derivatives, chain rule, directional derivatives, gradient, tangent planes, optimization (critical points, Lagrange multipliers).

3. **Multiple Integrals** — Setting up and evaluating double and triple integrals in various coordinate systems, changing order of integration, application to area, volume, mass, center of mass.

4. **Vector Calculus** — Line integrals of scalar functions and vector fields, work, flux, applying Green's theorem, computing curl and divergence, surface integrals, Stokes' theorem, divergence theorem.

Include problems that combine multiple concepts and require careful setup of integrals.
