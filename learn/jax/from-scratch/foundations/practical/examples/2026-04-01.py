"""JAX Mental Model — functional purity and pure function composition.

JAX's transformations (jit, grad, vmap) require functions to be pure:
same inputs → same outputs, no side effects. This exercise builds
intuition for writing JAX-compatible pure functions.

Usage:
    uv run python practical/examples/2026-04-01.py
"""

import jax
import jax.numpy as jnp


def normalize_rows(x: jnp.ndarray) -> jnp.ndarray:
    """Normalize each row of a 2D array to sum to 1.

    Must be a pure function — no mutation, no global state.
    Handle rows of all zeros by leaving them as zeros.
    """
    raise NotImplementedError()


def running_max(x: jnp.ndarray) -> jnp.ndarray:
    """Return the cumulative maximum along a 1D array.

    Example: [3, 1, 4, 1, 5] → [3, 3, 4, 4, 5]

    In NumPy you might reach for a loop with mutation.
    In JAX, think about what existing operations give you
    cumulative results. jax.lax.associative_scan or
    jnp.maximum.accumulate are worth looking into.
    """
    raise NotImplementedError()


def scatter_add(target: jnp.ndarray, indices: jnp.ndarray, values: jnp.ndarray) -> jnp.ndarray:
    """Add `values` into `target` at the given `indices`.

    If an index appears multiple times, the values should accumulate.
    For example:
        target = [0, 0, 0, 0]
        indices = [1, 1, 3]
        values = [10, 20, 5]
        result = [0, 30, 0, 5]

    Use the .at[] API. Remember: returns a new array.
    """
    raise NotImplementedError()


def pure_batch_stats(batch: jnp.ndarray) -> tuple[jnp.ndarray, jnp.ndarray]:
    """Compute per-feature mean and standard deviation for a batch.

    batch shape: (N, features)
    Returns: (mean, std) each of shape (features,)

    This is the kind of operation you'll write constantly in JAX
    neural net code. Must be pure — no in-place updates.
    """
    raise NotImplementedError()


def compose_transforms(x: jnp.ndarray, w1: jnp.ndarray, b1: jnp.ndarray,
                       w2: jnp.ndarray, b2: jnp.ndarray) -> jnp.ndarray:
    """Apply two linear transformations with ReLU activation between them.

    out = relu(x @ w1 + b1) @ w2 + b2

    This is a simple 2-layer forward pass written as a pure function.
    All state (weights, biases) is passed explicitly — no class attributes,
    no global variables. This is the JAX way.
    """
    raise NotImplementedError()


if __name__ == "__main__":
    # normalize_rows
    m = jnp.array([[1.0, 2.0, 3.0], [4.0, 4.0, 4.0], [0.0, 0.0, 0.0]])
    normed = normalize_rows(m)
    assert jnp.allclose(normed[0], jnp.array([1 / 6, 2 / 6, 3 / 6]))
    assert jnp.allclose(normed[1], jnp.array([1 / 3, 1 / 3, 1 / 3]))
    assert jnp.allclose(normed[2], jnp.array([0.0, 0.0, 0.0]))
    print("normalize_rows ✓")

    # running_max
    x = jnp.array([3.0, 1.0, 4.0, 1.0, 5.0, 2.0])
    rm = running_max(x)
    assert jnp.array_equal(rm, jnp.array([3.0, 3.0, 4.0, 4.0, 5.0, 5.0]))
    print("running_max ✓")

    # scatter_add
    target = jnp.zeros(5)
    indices = jnp.array([1, 1, 3, 0])
    values = jnp.array([10.0, 20.0, 5.0, 1.0])
    result = scatter_add(target, indices, values)
    assert jnp.allclose(result, jnp.array([1.0, 30.0, 0.0, 5.0, 0.0]))
    print("scatter_add ✓")

    # pure_batch_stats
    key = jax.random.PRNGKey(42)
    batch = jax.random.normal(key, (1000, 4))
    mean, std = pure_batch_stats(batch)
    assert mean.shape == (4,)
    assert std.shape == (4,)
    assert jnp.allclose(mean, jnp.mean(batch, axis=0))
    assert jnp.allclose(std, jnp.std(batch, axis=0))
    print("pure_batch_stats ✓")

    # compose_transforms
    x = jnp.array([[1.0, 2.0]])  # (1, 2)
    w1 = jnp.array([[0.5, -0.5, 0.3], [0.2, 0.8, -0.1]])  # (2, 3)
    b1 = jnp.array([0.1, 0.0, 0.0])  # (3,)
    w2 = jnp.array([[1.0], [1.0], [1.0]])  # (3, 1)
    b2 = jnp.array([0.0])  # (1,)
    out = compose_transforms(x, w1, b1, w2, b2)
    hidden = jnp.maximum(x @ w1 + b1, 0)  # ReLU
    expected = hidden @ w2 + b2
    assert jnp.allclose(out, expected)
    print("compose_transforms ✓")

    print("\nAll checks passed!")
