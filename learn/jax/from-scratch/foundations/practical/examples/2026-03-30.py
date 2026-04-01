"""JAX Mental Model and jax.numpy — practical exercises.

Rewrite basic NumPy operations using jax.numpy: array creation, slicing,
and .at[].set() updates. Each function has a docstring explaining what to
implement. Run this file and all assertions should pass.

Usage:
    uv run python practical/examples/2026-03-30.py
"""

import jax.numpy as jnp


def create_identity(n: int) -> jnp.ndarray:
    """Create an n×n identity matrix using jax.numpy."""
    return jnp.eye(n)


def linspace_sum(start: float, stop: float, num: int) -> float:
    """Create a linspace array and return its sum as a Python float."""
    return float(jnp.sum(jnp.linspace(start, stop, num)))


def reverse_slice(x: jnp.ndarray) -> jnp.ndarray:
    """Return the array reversed along the first axis using slicing."""
    return x[::-1]


def set_diagonal_to_value(x: jnp.ndarray, val: float) -> jnp.ndarray:
    """Return a new array with all diagonal elements set to `val`.

    Use .at[].set() — do NOT mutate in place (JAX arrays are immutable).
    """
    return x.at[jnp.diag_indices_from(x)].set(val)


def increment_row(x: jnp.ndarray, row: int, amount: float) -> jnp.ndarray:
    """Return a new array with `amount` added to every element in `row`.

    Use .at[].add().
    """
    return x.at[row, :].add(amount)


def outer_product(a: jnp.ndarray, b: jnp.ndarray) -> jnp.ndarray:
    """Compute the outer product of two 1-D arrays using jax.numpy."""
    return jnp.outer(a, b)


if __name__ == "__main__":
    eye = create_identity(3)
    assert eye.shape == (3, 3)
    assert jnp.allclose(eye, jnp.eye(3))

    s = linspace_sum(0.0, 10.0, 5)
    assert isinstance(s, float)
    assert abs(s - 25.0) < 1e-5

    x = jnp.array([1, 2, 3, 4, 5])
    assert jnp.array_equal(reverse_slice(x), jnp.array([5, 4, 3, 2, 1]))

    m = jnp.zeros((4, 4))
    m2 = set_diagonal_to_value(m, 7.0)
    assert jnp.allclose(jnp.diag(m2), jnp.array([7.0, 7.0, 7.0, 7.0]))
    assert jnp.allclose(m, jnp.zeros((4, 4)))  # original unchanged

    m3 = jnp.ones((3, 4))
    m4 = increment_row(m3, 1, 5.0)
    assert jnp.allclose(m4[1], jnp.array([6.0, 6.0, 6.0, 6.0]))
    assert jnp.allclose(m3[1], jnp.array([1.0, 1.0, 1.0, 1.0]))  # original unchanged

    a = jnp.array([1.0, 2.0, 3.0])
    b = jnp.array([4.0, 5.0])
    op = outer_product(a, b)
    assert op.shape == (3, 2)
    assert jnp.allclose(op, jnp.array([[4.0, 5.0], [8.0, 10.0], [12.0, 15.0]]))

    print("All checks passed!")
