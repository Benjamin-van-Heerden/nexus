# Calculus: Differential Equations

Mathematical models of change. Differential equations relate a function to its derivatives and describe how quantities evolve over time.

---

## 1. First Order ODEs

### 1.1 Basic Concepts

A differential equation (DE) relates an unknown function $y(x)$ to its derivatives.

**Order:** Highest derivative appearing.

**Solution:** A function $y = f(x)$ that satisfies the DE.

**Initial Condition (IC):** $y(x_0) = y_0$ specifies value at a point.

**Initial Value Problem (IVP):** DE + IC.

### 1.2 Separable Equations

$$\frac{dy}{dx} = f(x)g(y)$$

**Solution Method:**
1. Separate variables: $\frac{1}{g(y)} \, dy = f(x) \, dx$
2. Integrate both sides: $\int \frac{1}{g(y)} \, dy = \int f(x) \, dx$
3. Solve for $y$ if possible

**Example:**
$$\frac{dy}{dx} = xy$$
$$\frac{1}{y} \, dy = x \, dx$$
$$\ln|y| = \frac{x^2}{2} + C$$
$$y = Ce^{x^2/2}$$

### 1.3 Linear First Order Equations

Standard form:
$$\frac{dy}{dx} + P(x)y = Q(x)$$

**Integrating Factor:**
$$\mu(x) = e^{\int P(x) \, dx}$$

**Solution:**
1. Compute $\mu(x)$
2. Multiply equation by $\mu(x)$
3. Recognize left side as $\frac{d}{dx}(\mu y)$
4. Integrate: $\mu y = \int \mu Q \, dx + C$
5. Solve for $y$

**Example:**
$$\frac{dy}{dx} + 2y = e^{-x}$$

Here $P(x) = 2$, so $\mu = e^{\int 2 \, dx} = e^{2x}$.

Multiply:
$$e^{2x}\frac{dy}{dx} + 2e^{2x}y = e^{2x}e^{-x}$$
$$\frac{d}{dx}(e^{2x}y) = e^{x}$$
$$e^{2x}y = \int e^{x} \, dx = e^{x} + C$$
$$y = e^{-2x}(e^{x} + C) = e^{-x} + Ce^{-2x}$$

### 1.4 Exact Equations

Form: $M(x, y) \, dx + N(x, y) \, dy = 0$

**Test for Exactness:**
$$\frac{\partial M}{\partial y} = \frac{\partial N}{\partial x}$$

**Solution:**
If exact, there exists $\psi(x, y)$ such that:
$$\frac{\partial \psi}{\partial x} = M, \quad \frac{\partial \psi}{\partial y} = N$$

Then $\psi(x, y) = C$ is the solution.

**Making Equation Exact:**
Sometimes multiplying by an integrating factor $\mu(x)$ or $\mu(y)$ makes a non-exact equation exact.

### 1.5 Homogeneous Equations

**Homogeneous Function:** $f(tx, ty) = t^n f(x, y)$

If $M$ and $N$ are homogeneous of same degree, substitute $y = vx$:
$$\frac{dy}{dx} = v + x\frac{dv}{dx}$$

### 1.6 Bernoulli Equation

$$\frac{dy}{dx} + P(x)y = Q(x)y^n$$

**Solution:**
1. Substitute $z = y^{1-n}$
2. This gives linear equation in $z$
3. Solve, then substitute back

---

## 2. Second Order ODEs

### 2.1 Linear Second Order Equations

Standard form:
$$\frac{d^2y}{dx^2} + P(x)\frac{dy}{dx} + Q(x)y = R(x)$$

**Homogeneous:** $R(x) = 0$
**Non-homogeneous:** $R(x) \neq 0$

**Superposition Principle:** If $y_1$ and $y_2$ are solutions of homogeneous equation, then $c_1y_1 + c_2y_2$ is also a solution.

### 2.2 Constant Coefficient Homogeneous Equations

Equation: $ay'' + by' + cy = 0$

**Characteristic Equation:**
$$ar^2 + br + c = 0$$

**Three Cases:**

1. **Two distinct real roots** $r_1, r_2$:
$$y = c_1e^{r_1x} + c_2e^{r_2x}$$

2. **Repeated real root** $r$:
$$y = e^{rx}(c_1 + c_2x)$$

3. **Complex roots** $r = \alpha \pm i\beta$:
$$y = e^{\alpha x}(c_1\cos\beta x + c_2\sin\beta x)$$

### 2.3 Method of Undetermined Coefficients

For non-homogeneous equation with particular form of $R(x)$:

1. Solve homogeneous equation
2. Guess form of particular solution based on $R(x)$
3. Determine coefficients by substituting
4. General solution = homogeneous + particular

**Forms of $R(x)$ and guesses:**

| $R(x)$ | Guess |
|--------|-------|
| $P_n(x)$ (degree $n$) | $A_0 + A_1x + \cdots + A_nx^n$ |
| $e^{kx}$ | $Ae^{kx}$ |
| $\sin(kx)$ or $\cos(kx)$ | $A\cos(kx) + B\sin(kx)$ |
| $e^{kx}\sin(kx)$ | $e^{kx}(A\cos(kx) + B\sin(kx))$ |
| Product of above | Multiply guesses |

**Modification rule:** If guess overlaps with homogeneous solution, multiply by $x$.

### 2.4 Variation of Parameters

For $y'' + P(x)y' + Q(x)y = R(x)$:

1. Find fundamental solutions $y_1, y_2$ of homogeneous equation
2. Compute Wronskian: $W = y_1y_2' - y_1'y_2$
3. Particular solution:
$$y_p = -y_1 \int \frac{y_2R}{W} \, dx + y_2 \int \frac{y_1R}{W} \, dx$$

### 2.5 Cauchy-Euler Equation

$$ax^2y'' + bxy' + cy = 0$$

**Solution Method:**
Assume $y = x^r$:
$$ar(r-1) + br + c = 0$$
Solve characteristic equation for $r$, then form solution based on whether roots are distinct, repeated, or complex.

---

## 3. Higher Order Linear ODEs

### 3.1 Constant Coefficient

For $a_n y^{(n)} + \cdots + a_1 y' + a_0 = 0$:

1. Form characteristic equation: $a_n r^n + \cdots + a_1 r + a_0 = 0$
2. Find roots $r_1, r_2, \ldots, r_n$
3. Build solution from basis:
   - Real root $r$: $e^{rx}$
   - Repeated root $r$ (multiplicity $k$): $e^{rx}, xe^{rx}, \ldots, x^{k-1}e^{rx}$
   - Complex root $\alpha \pm i\beta$: $e^{\alpha x}\cos\beta x, e^{\alpha x}\sin\beta x$

### 3.2 Reduction of Order

If one solution $y_1$ is known, second solution:
$$y_2 = y_1 \int \frac{e^{-\int P(x) dx}}{y_1^2} \, dx$$
for $y'' + P(x)y' + Q(x)y = 0$.

---

## 4. Systems of ODEs

### 4.1 Linear Systems

$$\mathbf{y}' = A\mathbf{y} + \mathbf{g}(t)$$

where $\mathbf{y} = \begin{pmatrix} y_1 \\ y_2 \end{pmatrix}$, $A = \begin{pmatrix} a & b \\ c & d \end{pmatrix}$

### 4.2 Homogeneous Systems

For $\mathbf{y}' = A\mathbf{y}$:

1. Find eigenvalues $\lambda$ and eigenvectors $\mathbf{v}$ from $(A - \lambda I)\mathbf{v} = 0$
2. For eigenvalue $\lambda$ with eigenvector $\mathbf{v}$: $\mathbf{y} = \mathbf{v}e^{\lambda t}$
3. Form general solution as linear combination

**Real distinct eigenvalues:** $\mathbf{y} = c_1\mathbf{v}_1 e^{\lambda_1 t} + c_2\mathbf{v}_2 e^{\lambda_2 t}$

**Complex eigenvalues** $\lambda = \alpha \pm i\beta$:
$$\mathbf{y} = e^{\alpha t}(c_1\text{Re}(\mathbf{v}e^{i\beta t}) + c_2\text{Im}(\mathbf{v}e^{i\beta t}))$$

**Repeated eigenvalues:** If $A$ has repeated eigenvalue but insufficient eigenvectors, use second solution $\mathbf{y} = \mathbf{v}t e^{\lambda t}$.

### 4.3 Phase Portraits

| Eigenvalues | Behavior |
|-------------|-----------|
| Both positive | Unstable node (source) |
| Both negative | Stable node (sink) |
| Opposite signs | Saddle point |
| Complex with positive real part | Unstable spiral |
| Complex with negative real part | Stable spiral |
| Pure imaginary | Center |

### 4.4 Non-homogeneous Systems

For $\mathbf{y}' = A\mathbf{y} + \mathbf{g}(t)$:

**Method of undetermined coefficients:** Guess particular solution based on $\mathbf{g}(t)$.

**Variation of parameters:**
$$\mathbf{y}_p = Y(t)\int Y^{-1}(t)\mathbf{g}(t) \, dt$$
where $Y$ is matrix of homogeneous solutions (fundamental matrix).

---

## 5. Laplace Transforms

### 5.1 Definition

$$\mathcal{L}\{f(t)\} = F(s) = \int_0^\infty e^{-st} f(t) \, dt$$

**Region of Convergence:** Values of $s$ where integral converges.

### 5.2 Properties

**Linearity:**
$$\mathcal{L}\{af(t) + bg(t)\} = aF(s) + bG(s)$$

**First Translation (s-shift):**
$$\mathcal{L}\{e^{at}f(t)\} = F(s-a)$$

**Second Translation (t-shift):**
$$\mathcal{L}\{u(t-a)f(t-a)\} = e^{-as}F(s)$$
where $u$ is Heaviside step function.

**Derivative:**
$$\mathcal{L}\{f'(t)\} = sF(s) - f(0)$$
$$\mathcal{L}\{f''(t)\} = s^2F(s) - sf(0) - f'(0)$$

**Integral:**
$$\mathcal{L}\left\{\int_0^t f(\tau) \, d\tau\right\} = \frac{F(s)}{s}$$

**Convolution:**
$$\mathcal{L}\{(f * g)(t)\} = F(s)G(s)$$
where $(f * g)(t) = \int_0^t f(\tau)g(t-\tau) \, d\tau$$

### 5.3 Common Transforms

| $f(t)$ | $F(s) = \mathcal{L}\{f(t)\}$ |
|--------|------------------------------|
| $1$ | $\frac{1}{s}$ |
| $t^n$ | $\frac{n!}{s^{n+1}}$ |
| $e^{at}$ | $\frac{1}{s-a}$ |
| $\sin(at)$ | $\frac{a}{s^2 + a^2}$ |
| $\cos(at)$ | $\frac{s}{s^2 + a^2}$ |
| $e^{bt}\sin(at)$ | $\frac{a}{(s-b)^2 + a^2}$ |
| $e^{bt}\cos(at)$ | $\frac{s-b}{(s-b)^2 + a^2}$ |
| $\delta(t-a)$ | $e^{-as}$ |
| $u(t-a)$ | $\frac{e^{-as}}{s}$ |

### 5.4 Inverse Laplace Transform

Use partial fractions, completing squares, and shifting theorems.

**Key Formulas:**
$$\mathcal{L}^{-1}\left\{\frac{1}{s-a}\right\} = e^{at}$$
$$\mathcal{L}^{-1}\left\{\frac{1}{s^2 + a^2}\right\} = \frac{1}{a}\sin(at)$$
$$\mathcal{L}^{-1}\left\{\frac{s}{s^2 + a^2}\right\} = \cos(at)$$

### 5.5 Solving ODEs with Laplace Transforms

**Procedure:**
1. Take Laplace transform of both sides
2. Use properties to simplify (including ICs!)
3. Solve algebraically for $Y(s)$
4. Take inverse transform to find $y(t)$

### 5.6 Discontinuous Forcing

**Heaviside Step Function:**
$$u(t-a) = \begin{cases} 0 & t < a \\ 1 & t \geq a \end{cases}$$

**Representing piecewise functions:**
$$f(t) = f_1(t)u(t-a) + f_2(t)u(t-b) + \cdots$$

### 5.7 Convolution

For solving ODEs with convolution terms:
$$y * f = \int_0^t y(\tau)f(t-\tau) \, d\tau$$

If $\mathcal{L}\{y\} = Y(s)$ and $\mathcal{L}\{f\} = F(s)$, then:
$$\mathcal{L}\{(y * f)(t)\} = Y(s)F(s)$$

---

## 6. Series Solutions (Frobenius Method)

### 6.1 Power Series Solutions

For $y'' + P(x)y' + Q(x)y = 0$:

Assume $y = \sum_{n=0}^\infty a_n x^n$, substitute, and find recurrence relation.

### 6.2 Frobenius Method

For regular singular points (where $xP(x)$ and $x^2Q(x)$ are analytic):

Assume $y = \sum_{n=0}^\infty a_n x^{n+r}$, substitute, find indicial equation for $r$, then solve for coefficients.

---

## 7. Quick Reference

### 7.1 First Order Methods

| Type | Method |
|------|--------|
| Separable | $\frac{1}{g(y)}dy = f(x)dx$ |
| Linear | Integrating factor $\mu = e^{\int P(x)dx}$ |
| Exact | Check $\partial M/\partial y = \partial N/\partial x$ |
| Bernoulli | Substitute $z = y^{1-n}$ |

### 7.2 Second Order Homogeneous

Characteristic equation $ar^2 + br + c = 0$:

| Roots | Solution |
|-------|----------|
| $r_1 \neq r_2$ real | $c_1e^{r_1x} + c_2e^{r_2x}$ |
| $r$ repeated | $e^{rx}(c_1 + c_2x)$ |
| $\alpha \pm i\beta$ | $e^{\alpha x}(c_1\cos\beta x + c_2\sin\beta x)$ |

### 7.3 Laplace Transform Properties

$$\mathcal{L}\{f'\} = sF - f(0)$$
$$\mathcal{L}\{f''\} = s^2F - sf(0) - f'(0)$$
$$\mathcal{L}\{e^{at}f(t)\} = F(s-a)$$
$$\mathcal{L}\{u(t-a)f(t-a)\} = e^{-as}F(s)$$
$$\mathcal{L}\{(f * g)(t)\} = F(s)G(s)$$

### 7.4 Common Laplace Transforms

$$\mathcal{L}\{1\} = \frac{1}{s}, \quad \mathcal{L}\{t^n\} = \frac{n!}{s^{n+1}}$$
$$\mathcal{L}\{e^{at}\} = \frac{1}{s-a}, \quad \mathcal{L}\{\sin at\} = \frac{a}{s^2+a^2}$$
$$\mathcal{L}\{\cos at\} = \frac{s}{s^2+a^2}$$

---

## 8. Exercises Guidance

For this material, create exercises requiring:

1. **First Order ODEs** — Separable, linear, exact, homogeneous, Bernoulli equations. Include applications (population models, cooling, circuits).

2. **Second Order ODEs** — Constant coefficient homogeneous and non-homogeneous (undetermined coefficients, variation of parameters), Cauchy-Euler equations.

3. **Systems** — Solving linear systems, analyzing phase portraits (stability of equilibrium points).

4. **Laplace Transforms** — Computing transforms, solving ODEs with initial conditions, handling step functions and discontinuous forcing, convolution.

Include word problems modeling real phenomena (population growth/decay, mechanical vibrations, electrical circuits, mixing problems).
