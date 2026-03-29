# JAX Mental Model and jax.numpy

## Core Idea

JAX is NumPy on accelerators with composable function transformations. The fundamental difference from PyTorch/TensorFlow: JAX transforms *functions*, not tensors. There is no computation graph attached to arrays — instead, you write pure functions and wrap them with `jit`, `grad`, `vmap`, etc.

## Functional Purity

JAX functions must be pure: same inputs always produce same outputs, no side effects.

- No global state mutation
- No in-place array modification
- No printing (inside jitted functions — it only fires during tracing)
- This is what enables all of JAX's transformations to work

## jax.numpy

`jax.numpy` mirrors NumPy's API almost exactly. Key differences:

- **Immutable arrays**: `x[0] = 5` raises an error. Use `x = x.at[0].set(5)` instead.
- **The `.at[]` API**: `.at[idx].set(val)`, `.at[idx].add(val)`, `.at[idx].mul(val)` — all return new arrays.
- **Device-resident**: JAX arrays live on device (GPU/TPU). Mixing `np` and `jnp` silently transfers data and is slow.
- **32-bit default**: JAX defaults to float32 (not float64 like NumPy). Use `jax.config.update("jax_enable_x64", True)` if needed.

## What to Practice

- Rewrite simple NumPy operations using `jax.numpy`
- Use `.at[].set()` for array updates
- Understand that every operation returns a new array
- Get comfortable with the idea that functions are the unit of composition, not tensors
