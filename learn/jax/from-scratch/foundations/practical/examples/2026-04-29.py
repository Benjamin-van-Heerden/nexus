"""
JAX Core Philosophy Drill: Write for One, Batch with vmap
==========================================================

The JAX way: write pure functions for a single example, then transform them.
This exercise drills that muscle through realistic patterns.

Estimated time: 30 minutes
"""

import jax
import jax.numpy as jnp
from jax import random, jit, grad, vmap

# =============================================================================
# SETUP
# =============================================================================

key = random.PRNGKey(42)
key, k1, k2, k3 = random.split(key, 4)

input_dim = 10
hidden_dim = 64
output_dim = 5

# Two-layer MLP params, single-example style
def init_mlp_params(key, input_dim, hidden_dim, output_dim):
    k1, k2 = random.split(key)
    return {
        'W1': random.normal(k1, (hidden_dim, input_dim)) * 0.01,
        'b1': jnp.zeros(hidden_dim),
        'W2': random.normal(k2, (output_dim, hidden_dim)) * 0.01,
        'b2': jnp.zeros(output_dim),
    }

params = init_mlp_params(k1, input_dim, hidden_dim, output_dim)

# =============================================================================
# EXERCISE 1: Single-Example Forward Pass
# =============================================================================

print("=" * 60)
print("EXERCISE 1: Single-Example Forward Pass")
print("=" * 60)

def mlp_forward(params, x):
    """
    TODO: Implement a 2-layer MLP forward pass for a SINGLE example.
    x has shape (input_dim,)
    Use jnp.dot, add biases, apply relu between layers.
    """
    pass  # YOUR CODE HERE

# Verify it works on one example
x_single = random.normal(k2, (input_dim,))
# out = mlp_forward(params, x_single)
# print("Single output shape:", out.shape)  # Should be (output_dim,)


# =============================================================================
# EXERCISE 2: Batch with vmap — Don't Rewrite, Transform
# =============================================================================

print("\n" + "=" * 60)
print("EXERCISE 2: Batch with vmap")
print("=" * 60)

batch_size = 32
X_batch = random.normal(k3, (batch_size, input_dim))

# TODO: Use vmap to create a batched version of mlp_forward.
# params is broadcast, X is mapped over axis 0.
# batched_mlp = ...
# Y_batch = batched_mlp(params, X_batch)
# print("Batched output shape:", Y_batch.shape)  # Should be (32, output_dim)

# TODO: Verify by comparing to a Python loop over the batch.
# manual = jnp.stack([mlp_forward(params, X_batch[i]) for i in range(batch_size)])
# assert jnp.allclose(Y_batch, manual)


# =============================================================================
# EXERCISE 3: Per-Example Loss → Mean Loss via vmap
# =============================================================================

print("\n" + "=" * 60)
print("EXERCISE 3: Loss Composition")
print("=" * 60)

Y_true = random.normal(random.PRNGKey(99), (batch_size, output_dim))

def mse_loss_single(params, x, y):
    """
    TODO: MSE loss for a single (x, y) pair.
    Use mlp_forward (the single-example version!).
    """
    pass  # YOUR CODE HERE

# TODO: Create a batched loss using vmap.
# The trick: vmap over (None, 0, 0) — broadcast params, map over x and y.
# batched_loss = ...
# per_example_losses = batched_loss(params, X_batch, Y_true)
# mean_loss = jnp.mean(per_example_losses)
# print("Mean loss:", mean_loss)


# =============================================================================
# EXERCISE 4: grad + vmap — Per-Example Gradients
# =============================================================================

print("\n" + "=" * 60)
print("EXERCISE 4: Per-Example Gradients")
print("=" * 60)

# TODO: Compute the gradient of mse_loss_single w.r.t. params.
# Then vmap that gradient function over the batch.
# per_example_grad_fn = ...
# grads = per_example_grad_fn(params, X_batch, Y_true)

# grads is now a pytree of arrays with an extra batch dimension.
# For example, grads['W1'] has shape (32, 64, 10)

# TODO: Average the per-example gradients to get a single gradient update.
# avg_grads = jax.tree_map(...)

# TODO: Verify this matches taking grad of the mean loss directly.
def mean_loss(params, X, Y):
    losses = vmap(mse_loss_single, in_axes=(None, 0, 0))(params, X, Y)
    return jnp.mean(losses)

# direct_grad = grad(mean_loss)(params, X_batch, Y_true)
# assert jnp.allclose(avg_grads['W1'], direct_grad['W1'])


# =============================================================================
# EXERCISE 5: jit + vmap + grad — The Standard Training Step
# =============================================================================

print("\n" + "=" * 60)
print("EXERCISE 5: Compiled Training Step")
print("=" * 60)

# TODO: Build a single compiled function that:
# 1. Takes (params, X, Y)
# 2. Computes mean loss via vmap
# 3. Computes gradients via grad
# 4. Is wrapped in jit

# @jit
# def train_step(params, X, Y):
#     loss, grads = ...
#     return loss, grads

# Run it once to compile
# loss, grads = train_step(params, X_batch, Y_true)
# print("Compiled loss:", loss)


# =============================================================================
# EXERCISE 6: vmap over Multiple Axes — Image Batch
# =============================================================================

print("\n" + "=" * 60)
print("EXERCISE 6: Nested vmap (Image Batch)")
print("=" * 60)

# Simulate a conv-like operation written for a single spatial location
def apply_kernel(kernel, patch):
    """Single patch, single kernel. Both are 1D for simplicity."""
    return jnp.sum(kernel * patch)

# A "batch" of images: (batch, height, width, channels)
# For this exercise, flatten spatial: (batch, spatial, channels)
batch_size = 8
spatial = 16
channels = 4
kernel_size = 4

patches = random.normal(random.PRNGKey(7), (batch_size, spatial, channels))
kernel = random.normal(random.PRNGKey(8), (kernel_size,))

# We want to apply the kernel to EVERY patch in EVERY image.
# Inner vmap: over spatial locations (axis 0 of a single image)
# Outer vmap: over batch (axis 0 of the batch)

# TODO: Write the nested vmap.
# result = ...
# print("Result shape:", result.shape)  # Should be (8, 16)


# =============================================================================
# EXERCISE 7: The Philosophy in Action — Drop-in Replacement
# =============================================================================

print("\n" + "=" * 60)
print("EXERCISE 7: vmap as Drop-in Batching")
print("=" * 60)

# Here's a pattern you'll see constantly in JAX libraries:
# A function is written for one example, then the user decides batching.

def attention_single(Q, K, V):
    """
    Single-head attention for ONE sequence.
    Q, K, V each have shape (seq_len, head_dim)
    """
    scores = jnp.dot(Q, K.T) / jnp.sqrt(Q.shape[-1])
    weights = jax.nn.softmax(scores, axis=-1)
    return jnp.dot(weights, V)

seq_len = 10
head_dim = 16

Q = random.normal(random.PRNGKey(9), (seq_len, head_dim))
K = random.normal(random.PRNGKey(10), (seq_len, head_dim))
V = random.normal(random.PRNGKey(11), (seq_len, head_dim))

# Single example
# out = attention_single(Q, K, V)
# print("Single attention output:", out.shape)  # (10, 16)

# TODO: Now suppose we have a BATCH of attention computations.
# batch_size = 4
# Q_batch = random.normal(..., (4, 10, 16))
# K_batch = random.normal(..., (4, 10, 16))
# V_batch = random.normal(..., (4, 10, 16))

# batched_attention = ...
# out_batch = batched_attention(Q_batch, K_batch, V_batch)
# print("Batched attention output:", out_batch.shape)  # (4, 10, 16)

# Notice: attention_single knows nothing about batching.
# The batching decision is made at the call site. This is the JAX way.


print("\n" + "=" * 60)
print("Done! The core philosophy: write for one, transform for many.")
print("=" * 60)
