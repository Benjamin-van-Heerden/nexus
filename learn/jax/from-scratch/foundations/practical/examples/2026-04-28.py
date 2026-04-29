"""
JAX vmap and pmap Practical Exercise
=====================================

This exercise covers:
- vmap for automatic vectorization
- pmap for multi-device parallelism
- Composition with jit and grad
- Realistic patterns you'll use in neural network training

Estimated time: 45-60 minutes
"""

import time

import jax
import jax.numpy as jnp
from jax import random, vmap

# =============================================================================
# PART 1: vmap Fundamentals
# =============================================================================

print("=" * 60)
print("PART 1: vmap Fundamentals")
print("=" * 60)

# Setup
key = random.PRNGKey(42)
key, k1, k2 = random.split(key, 3)


# Single-example function
def predict(params, x):
    """Single example prediction."""
    W, b = params
    return jnp.dot(W, x) + b


# Generate data
batch_size = 32
input_dim = 10
output_dim = 5

W = random.normal(k1, (output_dim, input_dim))
b = random.normal(k2, (output_dim,))
params = (W, b)

X_batch = random.normal(random.PRNGKey(1), (batch_size, input_dim))

# TODO 1: Use vmap to create a batched version of predict.
# The params should be broadcast (not mapped over), and X should be mapped over axis 0.
# batched_predict = ...
# predictions = batched_predict(params, X_batch)
# print("Shape:", predictions.shape)  # Should be (32, 5)
batched_predict = jax.vmap(predict, (None, 0))
predictions = batched_predict(params, X_batch)
print("Shape:", predictions.shape)  # Should be (32, 5)


# TODO 2: Verify your vmap result matches a manual Python loop.
manual_preds = jnp.stack([predict(params, X_batch[i]) for i in range(batch_size)])
assert jnp.allclose(predictions, manual_preds)


# TODO 3: Create a function that computes per-example loss, then vmap it.
def mse_loss_single(params, x, y):
    """MSE for a single example."""
    pred = predict(params, x)
    return jnp.mean((pred - y) ** 2)


Y_batch = random.normal(random.PRNGKey(2), (batch_size, output_dim))

per_example_losses = jax.vmap(mse_loss_single, (None, 0, 0))(params, X_batch, Y_batch)
print("Per-example losses shape:", per_example_losses.shape)  # Should be (32,)
print("Mean loss:", jnp.mean(per_example_losses))


# =============================================================================
# PART 2: vmap + grad Composition
# =============================================================================

print("\n" + "=" * 60)
print("PART 2: vmap + grad Composition")
print("=" * 60)

# TODO 4: Compute per-example gradients using vmap(grad(...)).
grad_fn = jax.vmap(jax.grad(mse_loss_single), (None, 0, 0))
per_example_grads = grad_fn(params, X_batch, Y_batch)
# Inspect the shapes — W grad should be (32, 5, 10), b grad should be (32, 5)
print(
    f"Per-example grads shape: {per_example_grads[0].shape, per_example_grads[1].shape}"
)

# TODO 5: Average the per-example gradients to get a single gradient.
avg_grad_W = jnp.mean(per_example_grads[0], axis=0)
avg_grad_b = jnp.mean(per_example_grads[1], axis=0)
avg_grads = (avg_grad_W, avg_grad_b)
print(f"Avg grads: {avg_grad_W.shape, avg_grad_b.shape}")


# TODO 6: Verify this matches grad of the mean loss function.
def mse_loss_batch(params, X, Y):
    preds = vmap(predict, in_axes=(None, 0))(params, X)
    return jnp.mean((preds - Y) ** 2)


batch_grad = jax.grad(mse_loss_batch)(params, X_batch, Y_batch)
assert jnp.allclose(avg_grad_W, batch_grad[0])
assert jnp.allclose(avg_grad_b, batch_grad[1])


# =============================================================================
# PART 3: Nested vmap
# =============================================================================

print("\n" + "=" * 60)
print("PART 3: Nested vmap")
print("=" * 60)

# Scenario: batch of sequences (e.g., batch_size=8, seq_len=16)
batch_size = 8
seq_len = 16

X_seq = random.normal(random.PRNGKey(3), (batch_size, seq_len, input_dim))

# TODO 7: Use nested vmap to apply predict to each element in the batch AND each timestep.
# Inner vmap: over timesteps (axis 0 of each sequence)
# Outer vmap: over batch (axis 0 of the batch)
# Result shape should be (8, 16, 5)
over_seq = jax.vmap(predict, (None, 0))
over_batch = jax.vmap(over_seq, (None, 0))
seq_predictions = over_batch(params, X_seq)

print("Sequence predictions shape:", seq_predictions.shape)


# =============================================================================
# PART 4: vmap + PRNG Keys
# =============================================================================

print("\n" + "=" * 60)
print("PART 4: vmap + PRNG Keys")
print("=" * 60)

# TODO 8: Generate batch_size independent random vectors using vmap.
# Each element should use a different key.
batch_size = 32
keys = random.split(random.PRNGKey(4), batch_size)


def gen_random_vector(key):
    return jax.random.normal(key, (10,))


random_vectors = jax.vmap(gen_random_vector)(keys)
print("Random vectors shape:", random_vectors.shape)  # Should be (32, 10)

# TODO 9: Verify they're actually different (not all identical).
print("All identical?", jnp.allclose(random_vectors[0], random_vectors[1]))


# =============================================================================
# PART 5: pmap (Multi-Device)
# =============================================================================

print("\n" + "=" * 60)
print("PART 5: pmap (Multi-Device)")
print("=" * 60)

# Check available devices
print("Available devices:", jax.devices())
print("Device count:", jax.device_count())


def simple_matmul(A, B):
    return jnp.dot(A, B)


# TODO 10: If you have multiple devices, use pmap to parallelize a computation.
# Create an array with leading axis equal to device count.
# For single-device systems, this will still work (just on one device).

devices = jax.devices()
if len(devices) > 1:
    print(f"Running pmap across {len(devices)} devices...")
    # Create data: leading axis = device count
    n_devices = len(devices)
    A_sharded = random.normal(random.PRNGKey(5), (n_devices, 256, 256))
    B_sharded = random.normal(random.PRNGKey(6), (n_devices, 256, 256))

    # pmapped_matmul = ...
    # result = pmapped_matmul(A_sharded, B_sharded)
    # print("Result shape:", result.shape)  # Should be (n_devices, 256, 256)
else:
    print("Only one device available — pmap will run on CPU/GPU as single device.")
    # Still try pmap for learning
    A_single = random.normal(random.PRNGKey(5), (1, 256, 123))
    B_single = random.normal(random.PRNGKey(6), (1, 123, 456))

    pmapped_matmul = jax.pmap(simple_matmul)
    result = pmapped_matmul(A_single, B_single)
    print("Result shape:", result.shape)


# =============================================================================
# PART 6: The Full Pipeline — jit + vmap + grad
# =============================================================================

print("\n" + "=" * 60)
print("PART 6: Full Pipeline — jit + vmap + grad")
print("=" * 60)

# TODO 11: Build a complete training step that uses all three transformations.
# 1. vmap to compute per-example predictions
# 2. Compute mean loss
# 3. grad to get gradients
# 4. jit to compile the whole thing


def loss_fn(params, X, Y):
    preds = vmap(predict, in_axes=(None, 0))(params, X)
    return jnp.mean((preds - Y) ** 2)


compiled_grad_fn = jax.jit(jax.grad(loss_fn))

# Time the compiled version vs uncompiled
X_large = random.normal(random.PRNGKey(7), (1024, input_dim))
Y_large = random.normal(random.PRNGKey(8), (1024, output_dim))

# Warmup
_ = compiled_grad_fn(params, X_large, Y_large)
jax.block_until_ready(_)

# Time compiled
start = time.time()
for _ in range(100):
    grads = compiled_grad_fn(params, X_large, Y_large)
    jax.block_until_ready(grads)
compiled_time = time.time() - start

# Time uncompiled
raw_grad_fn = jax.grad(loss_fn)
start = time.time()
for _ in range(100):
    grads = raw_grad_fn(params, X_large, Y_large)
    jax.block_until_ready(grads)
raw_time = time.time() - start

print(
    f"Compiled: {compiled_time:.4f}s, Raw: {raw_time:.4f}s, Speedup: {raw_time / compiled_time:.1f}x"
)


# =============================================================================
# PART 7: Sharp Edge — vmap with Data-Dependent Control Flow
# =============================================================================

print("\n" + "=" * 60)
print("PART 7: Sharp Edge — Control Flow in vmap")
print("=" * 60)

# TODO 12: Try vmapping a function with Python if-statement.
# Observe what happens when different batch elements take different branches.


def bad_relu(x):
    if x > 0:
        return x
    return 0.0


# vmap(bad_relu)(jnp.array([1.0, -1.0, 2.0, -2.0]))
# What happens? Why?


# TODO 13: Fix it using jax.lax.cond.
def good_relu(x):
    # return jax.lax.cond(...)
    return jax.lax.cond(x > 0, lambda: x, lambda: 0.0)


vmapped_good = jax.vmap(good_relu)
print("Good relu result:", vmapped_good(jnp.array([1.0, -1.0, 2.0, -2.0])))


print("\n" + "=" * 60)
print("Exercise complete! Fill in all TODOs and verify your understanding.")
print("=" * 60)
