# XLA and Sharp Bits

## XLA Compilation

When you call `jax.jit(f)`, JAX traces `f` to produce an XLA computation graph (HLO — High Level Operations), which XLA then optimizes and compiles to native machine code for the target device (CPU/GPU/TPU).

### Operator fusion

XLA fuses chains of operations into single kernels, eliminating intermediate memory allocations. Writing a manual layer norm as a chain of simple ops is not a penalty in JAX — XLA will fuse them into one efficient kernel. This is fundamentally different from PyTorch where you'd want to use a fused kernel directly.

### First-call compilation cost

The first call to a jitted function is slow (compilation). Subsequent calls with matching shapes/dtypes hit the cache and are fast. Always warm up before benchmarking.

## Sharp Bits

### No in-place operations

```python
# WRONG — raises error inside jit
x[0] = 5

# CORRECT — returns a new array
x = x.at[0].set(5)
x = x.at[1:3].add(10)
x = x.at[mask].mul(2)
```

### Static shapes required under jit

Array shapes must be known at trace time. Data-dependent shapes cause errors:

```python
# WRONG — shape depends on runtime values
@jax.jit
def f(x):
    return x[x > 0]  # output shape depends on data

# CORRECT — use fixed-size alternatives
@jax.jit
def f(x):
    return jnp.where(x > 0, x, 0)  # same shape always
```

### Control flow inside jit

Python `if`/`for` are evaluated at trace time only. For data-dependent branching at runtime:

```python
# WRONG — only traces one branch
@jax.jit
def f(x):
    if x > 0:      # traced as a concrete bool at trace time
        return x
    return -x

# CORRECT — use lax primitives
@jax.jit
def f(x):
    return jax.lax.cond(x > 0, lambda: x, lambda: -x)
```

Available control flow primitives:
- `jax.lax.cond(pred, true_fn, false_fn)` — if/else
- `jax.lax.while_loop(cond_fn, body_fn, init_val)` — while loop
- `jax.lax.fori_loop(lower, upper, body_fn, init_val)` — for loop
- `jax.lax.scan(f, init, xs)` — sequential map with carry (like fold + map)

### Recompilation triggers

These cause XLA to recompile:
- Input shape changes
- Input dtype changes
- `static_argnums` values change

Avoid creating jitted functions inside loops (recompiles every iteration). Pad variable-length inputs to fixed sizes.

### Side effects and printing

`print()` inside a jitted function only executes during tracing (first call), not on subsequent calls. Use `jax.debug.print()` for runtime printing (useful for debugging but has performance cost).

### NumPy interop

Don't mix `numpy` and `jax.numpy` accidentally. `np.array` + `jnp.array` operations silently transfer data between host and device. Keep everything in `jnp` once you start.

## What to Practice

- Trigger and understand recompilation (change input shapes, observe timing)
- Rewrite Python control flow using `lax.cond`, `lax.fori_loop`, `lax.scan`
- Use `jax.debug.print()` inside jitted functions
- Time jitted vs non-jitted functions (remember `.block_until_ready()`)
- Practice the `.at[].set()` pattern until it's automatic
