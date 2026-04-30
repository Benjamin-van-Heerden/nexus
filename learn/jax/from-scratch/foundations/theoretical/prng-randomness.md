# PRNG and Randomness in JAX

## The Core Problem

NumPy and PyTorch use **global implicit random state**. Every call to `np.random.randn()` silently advances a global RNG. This is convenient but fundamentally incompatible with JAX's functional model.

### Why Global State Breaks JAX

1. **Jit purity requirement**: Jitted functions must be pure — same inputs → same outputs. Global RNG state makes this impossible.
2. **Reproducibility**: Under `vmap` or `pmap`, shared RNG state would produce correlated or identical samples across batch elements.
3. **Parallelism**: Multiple devices or vectorized operations cannot safely share mutable state.

## JAX's Solution: Explicit PRNG Keys

Every random operation requires an explicit key:

```python
import jax
import jax.numpy as jnp

key = jax.random.PRNGKey(42)          # create a root key
x = jax.random.normal(key, shape=(3,))  # use it — deterministic!
```

**Crucial**: Calling `jax.random.normal(key, ...)` with the same key always returns the same array. This is intentional and necessary for reproducibility.

## Splitting Keys: The Key Pattern

To get multiple independent random streams, you **split** a key:

```python
key, subkey = jax.random.split(key)      # split into 2
keys = jax.random.split(key, num=5)      # split into N
```

The golden rule: **split before use, treat each key as single-use**.

```python
key = jax.random.PRNGKey(0)

key, k1, k2 = jax.random.split(key, 3)
w = jax.random.normal(k1, shape=(784, 256))
b = jax.random.normal(k2, shape=(256,))
```

After splitting, `key` is the "continuation" key for future splits, while `k1`, `k2` are consumed by random operations.

## Threading Keys Through Code

No global state means explicit passing:

```python
def init_layer(key, in_dim, out_dim):
    k1, k2 = jax.random.split(key)
    w = jax.random.normal(k1, (in_dim, out_dim)) * 0.01
    b = jnp.zeros(out_dim)
    return {'w': w, 'b': b}

def init_network(key, sizes):
    params = []
    for in_d, out_d in zip(sizes[:-1], sizes[1:]):
        key, subkey = jax.random.split(key)
        params.append(init_layer(subkey, in_d, out_d))
    return params
```

## Threefry: JAX's Counter-Based PRNG

JAX uses Threefry, not Mersenne Twister. This means:
- **Splitting is cheap** — no state to copy, just a hash
- **Device-independent** — same key → same result on CPU, GPU, TPU
- **Parallelism-friendly** — counter-based design scales naturally

## Common Pitfalls

1. **Reusing a key**: `jax.random.normal(key, ...); jax.random.normal(key, ...)` — both calls return identical values
2. **Forgetting to split**: Passing the same key to multiple independent operations creates correlated weights
3. **Not threading through**: Hard-coding `PRNGKey(0)` everywhere loses reproducibility and independence

## Best Practices

- Start with one root key at the program entry point
- Split at every branching point (multiple layers, multiple samples)
- Return the continuation key from functions that consume keys
- Use `jax.random.split(key, n)` for vectorized operations
