# Transformations: jit and grad

## jax.jit — Just-In-Time Compilation

Traces a function on first call, compiles it via XLA, caches the result. Subsequent calls skip Python and run compiled native code.

### How tracing works

When you call a jitted function, JAX replaces concrete array values with abstract **tracers** that record the operations. The trace produces an XLA computation graph (HLO) which gets compiled to native code.

Key implications:
- Python control flow (`if`, `for`) is evaluated at trace time, not runtime. Only the branch taken during tracing gets compiled.
- Use `jax.lax.cond`, `jax.lax.while_loop`, `jax.lax.fori_loop` for data-dependent control flow inside jitted functions.
- `static_argnums` / `static_argnames` marks arguments that trigger recompilation when they change (use for Python scalars, shapes, flags — not arrays).

### Recompilation

XLA compiles per input shape/dtype. Changing shapes causes recompilation. This is why padding to fixed shapes is best practice for variable-length inputs.

### Async dispatch

JAX dispatches computations asynchronously. A call returns immediately; the result is a future. Use `.block_until_ready()` for accurate timing.

## jax.grad — Automatic Differentiation

Returns a new function that computes the gradient of a scalar-valued function.

```python
def loss(params, x, y):
    pred = params @ x
    return jnp.mean((pred - y) ** 2)

grad_fn = jax.grad(loss)       # gradient w.r.t. first arg (params)
grads = grad_fn(params, x, y)  # same shape as params
```

Key points:
- `jax.grad(f)` differentiates w.r.t. the first argument by default. Use `argnums` to change.
- `jax.value_and_grad(f)` returns both the value and gradient in one pass — more efficient than calling both separately.
- Composable: `jax.grad(jax.grad(f))` gives second-order derivatives.
- For non-scalar outputs: `jax.jacfwd` (forward-mode), `jax.jacrev` (reverse-mode).
- For Jacobian-vector products: `jax.jvp` (forward), `jax.vjp` (reverse).

### Mental model difference from PyTorch

PyTorch: attach a tape to tensors, call `.backward()`, read `.grad` attributes.
JAX: transform the function itself. No tape, no `.backward()`, no mutable state.

## What to Practice

- Wrap functions with `jax.jit` and observe speedups
- Experiment with tracing: print inside jitted functions, try data-dependent branches
- Use `jax.grad` to differentiate simple mathematical functions
- Use `value_and_grad` in a training loop
- Compose `jit` and `grad` together
