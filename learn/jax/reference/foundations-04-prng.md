# PRNG and Randomness

## The Problem with Global RNG State

NumPy and PyTorch use global implicit random state. Call `np.random.randn()` and the global RNG silently advances. This is convenient but incompatible with JAX's functional model:

- Jitted functions must be pure (same inputs → same outputs)
- Global mutable state breaks reproducibility under `jit` and `vmap`
- Parallel execution (vmap, pmap) with shared RNG state would produce correlated samples

## JAX's Solution: Explicit PRNG Keys

Every random operation requires an explicit key:

```python
key = jax.random.PRNGKey(42)          # create a root key
x = jax.random.normal(key, shape=(3,))  # use it
```

Calling the same function with the same key always returns the same result. This is intentional — it's what makes JAX reproducible.

## Splitting Keys

To get multiple independent random streams, you **split** a key:

```python
key, subkey = jax.random.split(key)      # split into 2
keys = jax.random.split(key, num=5)      # split into N
```

The pattern: split before use, treat each key as single-use.

```python
key = jax.random.PRNGKey(0)

key, k1, k2 = jax.random.split(key, 3)
w = jax.random.normal(k1, shape=(784, 256))
b = jax.random.normal(k2, shape=(256,))
```

## Threading Keys Through Code

Since there's no global state, you must pass keys explicitly:

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

## JAX uses Threefry

JAX's PRNG is counter-based (Threefry), not Mersenne Twister like NumPy. This means:
- Splitting is cheap (no state to copy)
- Results are device-independent
- Parallelism-friendly

## What to Practice

- Create keys, split them, use them for random array generation
- Write a function that takes a key parameter and threads it through multiple random calls
- Initialize a simple neural network's weights using key splitting
- Verify reproducibility: same key → same output
