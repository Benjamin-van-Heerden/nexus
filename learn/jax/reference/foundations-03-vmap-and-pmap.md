# Transformations: vmap and pmap

## jax.vmap — Automatic Vectorization

Transforms a function written for a single example into one that operates over a batch. Eliminates manual broadcasting and batch dimension bookkeeping.

```python
def predict(params, x):
    return jnp.dot(params, x)

# Without vmap: manually batch
predictions = jnp.stack([predict(params, x_i) for x_i in batch_x])

# With vmap: automatic batching
batched_predict = jax.vmap(predict, in_axes=(None, 0))
predictions = batched_predict(params, batch_x)
```

### in_axes and out_axes

- `in_axes` specifies which axis of each argument to map over. `None` means broadcast (don't map).
- `out_axes` specifies where the batch axis appears in the output.
- `in_axes=(None, 0)` means "don't batch first arg, batch second arg along axis 0."

### Why this matters

In PyTorch, you write batch-aware code from the start — every tensor has a batch dimension and you think about it constantly. In JAX, you write code for a single example and vmap handles batching. This is simpler to reason about and less error-prone.

### Composability

`vmap` composes with everything:
- `jax.vmap(jax.grad(f))` — per-example gradients
- `jax.jit(jax.vmap(f))` — compiled batched function
- `jax.vmap(jax.vmap(f))` — nested batching (e.g., batch of sequences)

## jax.pmap — Parallel Map Across Devices

Like `vmap`, but distributes across multiple XLA devices (GPUs/TPUs).

- Leading axis of inputs must equal device count
- Each device gets one slice
- Cross-device communication via `jax.lax.pmean`, `jax.lax.psum`

Note: for modern multi-device work, `jax.sharding` + `jax.Array` + `jax.jit` is increasingly preferred over `pmap`. But understanding `pmap` builds the mental model for distributed computation.

## What to Practice

- Write a function for a single example, then vmap it
- Experiment with different `in_axes` configurations
- Compute per-example gradients with `vmap(grad(loss))`
- Nest vmap calls for multi-dimensional batching
