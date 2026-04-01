# Quiz: JAX Mental Model

3 quick questions covering the foundations so far.

---

**Q1 (code prediction):** What happens when you run this inside a `jit`-compiled function?

```python
def f(x):
    acc = []
    acc.append(x.sum())
    return acc[0]

f_jit = jax.jit(f)
f_jit(jnp.ones(3))  # works?
f_jit(jnp.ones(5))  # works? same result?
```

Your answer:

> This actually works since acc is local state and jax jit can handle it. Not a good pattern to follow though. If the accumulator were a global variable it not do what we want at all.

---

**Q2 (multiple choice):** Why does `x = x.at[0].set(99)` return a new array instead of modifying in place?

- A) JAX arrays are stored on CPU and copying is cheap
- B) In-place mutation would break functional purity, which jit/grad/vmap depend on
- C) It's a Python limitation — NumPy arrays can't be subclassed for mutation
- D) XLA requires all arrays to be the same size

Your answer:

> B)

---

**Q3 (short answer):** You have a `(batch, features)` shaped array. You want to normalize each sample so its features sum to 1. Which axis do you sum over, and what shape does the sum need to be for broadcasting to work?

Your answer:

> Over axis 1 (batch axis), the sum should have shape (batch,)

---

<details>
<summary>Answers</summary>

**Q1:** Both calls work. The first traces and compiles, the second triggers a re-trace (different shape). `acc.append` is a Python side effect that only happens during tracing — it builds the list at trace time, but the returned `acc[0]` is a traced JAX value, so the compiled function correctly returns `x.sum()`. The key insight: Python-level side effects execute during tracing, not at runtime.

**Q2:** B. Immutability is required for functional purity. If arrays could be mutated, `jit` couldn't safely cache compiled functions, `grad` couldn't replay computations, and `vmap` couldn't parallelize across batches.

**Q3:** Sum over axis=1 (the features axis). The sum has shape `(batch,)` — you need to keep dims (`keepdims=True`) to get shape `(batch, 1)` so it broadcasts against `(batch, features)`.

</details>
