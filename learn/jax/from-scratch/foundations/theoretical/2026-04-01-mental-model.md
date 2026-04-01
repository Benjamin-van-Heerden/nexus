# JAX Mental Model — Theoretical Reading

## Functions, Not Tensors

The biggest shift from PyTorch/TensorFlow to JAX is what gets transformed. In PyTorch, tensors carry computation graphs — you call `.backward()` on a tensor. In JAX, there is no state attached to arrays at all. Instead, you write plain Python functions and wrap them with transformations like `jit`, `grad`, `vmap`.

This means the **function** is the fundamental unit, not the tensor. A JAX array is just data — it doesn't know how it was computed or what should happen next.

Consider a PyTorch pattern:

```python
# PyTorch — state lives on the tensor
loss = model(x)
loss.backward()  # the tensor knows its graph
```

vs. JAX:

```python
# JAX — state is external, functions are transformed
def loss_fn(params, x):
    return model(params, x)

grads = jax.grad(loss_fn)(params, x)  # the function is what gets differentiated
```

Parameters are passed explicitly. There is no `self.weight` — everything the function needs is an argument. This is what makes JAX's transformations composable: `jit(grad(vmap(f)))` works because each transformation takes a function and returns a function.

## Functional Purity

For these transformations to work, functions must be **pure**:

- **Same inputs → same outputs**: no reading from global variables that might change, no random state (JAX has its own explicit PRNG system for this).
- **No side effects**: no mutating arrays, no appending to lists, no printing (inside `jit` — `print` fires during tracing, not execution, which is a common source of confusion).

Why does purity matter? Because `jit` traces your function once with abstract values to build an XLA computation. If your function's behavior depends on anything other than its inputs' shapes and dtypes, the compiled version will be wrong. Similarly, `grad` needs to replay your function symbolically — side effects would either be lost or duplicated.

An impure function might "work" in eager mode but silently break under `jit`:

```python
results = []

def bad_fn(x):
    y = x * 2
    results.append(y)  # side effect — lost under jit
    return y
```

## Immutable Arrays

JAX arrays cannot be modified in place. This is a direct consequence of functional purity — if arrays were mutable, functions could have hidden side effects through aliased references.

```python
x = jnp.array([1, 2, 3])
# x[0] = 10  ← raises an error

x_new = x.at[0].set(10)  # returns a NEW array
# x is unchanged, x_new is [10, 2, 3]
```

The `.at[]` API supports: `.set()`, `.add()`, `.mul()`, `.min()`, `.max()`, `.apply()`. All return new arrays. Under `jit`, JAX can often optimize away the copy when the original is no longer used.

## Device Residency and dtypes

JAX arrays live on device (CPU/GPU/TPU). NumPy arrays live on CPU. Mixing them works but involves implicit transfers:

```python
np_arr = np.array([1.0, 2.0])
jnp_arr = jnp.array([3.0, 4.0])
result = jnp_arr + jnp.array(np_arr)  # np_arr silently transferred to device
```

JAX defaults to **float32**, not float64 like NumPy. This catches people off guard when comparing results:

```python
np.array([1.0]).dtype    # float64
jnp.array([1.0]).dtype   # float32
```

This is intentional — accelerators are much faster at float32, and for ML workloads the extra precision rarely matters.

---

## Reflect

After reading the above, answer these in your own words:

1. Why does JAX transform functions rather than attaching computation graphs to tensors? What does this enable?

2. What would go wrong if you used a global Python list inside a `jit`-compiled function to accumulate intermediate results?

3. In PyTorch, `model.parameters()` returns the weights. In JAX, where do parameters live and how are they passed around?

4. Why does JAX default to float32? When might you actually want float64?
