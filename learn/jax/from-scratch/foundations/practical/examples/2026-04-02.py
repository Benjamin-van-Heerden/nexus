"""
Axes and Shapes — Quick Reinforcement

Focus: understanding which axis does what, and how reductions/operations
behave across different axes. 3 short exercises.

Run: uv run python practical/examples/2026-04-02.py
"""

import jax.numpy as jnp


# --- Exercise 1: Axis intuition ---
# Given a (3, 4) matrix where each row is a student and each column is a test score,
# compute:
#   a) The average score per student (should be shape (3,))
#   b) The highest score on each test (should be shape (4,))
#   c) The overall average (scalar)

def per_student_avg(scores):
    """Return mean score per student."""
    raise NotImplementedError()

def per_test_max(scores):
    """Return max score on each test."""
    raise NotImplementedError()

def overall_avg(scores):
    """Return scalar overall average."""
    raise NotImplementedError()


# --- Exercise 2: Broadcasting + axis alignment ---
# Given a (3, 4) matrix, subtract the row-mean from every element
# (i.e., center each row to have mean ~0).

def center_rows(x):
    """Subtract each row's mean from that row. Return same shape as input."""
    raise NotImplementedError()


# --- Exercise 3: scatter_add use case ---
# You have 5 data points belonging to 3 groups (group_ids below).
# Compute the sum of values in each group using jnp.zeros + .at[].add().
# This is what scatter_add is for: accumulating values into buckets by index.

def group_sum(values, group_ids, num_groups):
    """
    values: (5,) array of floats
    group_ids: (5,) array of ints in [0, num_groups)
    num_groups: int
    Returns: (num_groups,) array where result[g] = sum of values where group_ids == g
    """
    raise NotImplementedError()


if __name__ == "__main__":
    # Exercise 1
    scores = jnp.array([
        [80.0, 90.0, 70.0, 85.0],
        [60.0, 75.0, 80.0, 65.0],
        [95.0, 85.0, 90.0, 100.0],
    ])
    assert per_student_avg(scores).shape == (3,)
    assert jnp.allclose(per_student_avg(scores), jnp.array([81.25, 70.0, 92.5]))
    assert per_test_max(scores).shape == (4,)
    assert jnp.allclose(per_test_max(scores), jnp.array([95.0, 90.0, 90.0, 100.0]))
    assert overall_avg(scores).shape == ()
    assert jnp.allclose(overall_avg(scores), jnp.float32(81.25))
    print("Exercise 1 passed!")

    # Exercise 2
    x = jnp.array([[10.0, 20.0, 30.0, 40.0],
                    [1.0, 2.0, 3.0, 4.0],
                    [100.0, 200.0, 300.0, 400.0]])
    centered = center_rows(x)
    assert centered.shape == x.shape
    assert jnp.allclose(centered.mean(axis=1), jnp.zeros(3), atol=1e-5)
    print("Exercise 2 passed!")

    # Exercise 3
    values = jnp.array([1.0, 3.0, 5.0, 2.0, 4.0])
    group_ids = jnp.array([0, 1, 2, 0, 1])
    result = group_sum(values, group_ids, 3)
    assert result.shape == (3,)
    assert jnp.allclose(result, jnp.array([3.0, 7.0, 5.0]))
    print("Exercise 3 passed!")

    print("\nAll checks passed!")
