# Functions vs Tensors — The JAX Mental Model

## Reading

The deepest difference between JAX and PyTorch isn't syntax — it's what the framework *transforms*.

### PyTorch: transforms tensors

In PyTorch, the tensor is the central object. It carries:
- Data (the actual numbers)
- A computation graph (autograd history)
- Device placement
- Gradient state (`.grad`, `.requires_grad`)

When you call `loss.backward()`, PyTorch walks the graph *attached to the tensor* to compute gradients. The graph is built implicitly as operations execute (eager mode).

```python
# PyTorch — state lives on the tensor
x = torch.tensor([1.0, 2.0], requires_grad=True)
y = (x ** 2).sum()
y.backward()       # walks x's computation graph
x.grad              # gradients stored ON the tensor
```

### JAX: transforms functions

In JAX, arrays are just data — no graph, no grad state, no device transfer methods. Instead, you write **pure functions** and apply **transformations** to them:

```python
# JAX — transformations operate on functions
def f(x):
    return (x ** 2).sum()

grad_f = jax.grad(f)       # grad_f is a NEW function
grad_f(jnp.array([1.0, 2.0]))   # returns gradients
```

`jax.grad(f)` doesn't execute `f` — it returns a *new function* that computes the gradient of `f`. This is function transformation, not tensor mutation.

### Why this matters

Because JAX transforms functions (not tensors), it can compose transformations arbitrarily:

```python
# Gradient of a gradient (Hessian-vector product)
jax.grad(jax.grad(f))

# Vectorize a gradient across a batch
jax.vmap(jax.grad(f))

# Compile the vectorized gradient
jax.jit(jax.vmap(jax.grad(f)))
```

Each transformation wraps the previous one. This only works if the inner function is **pure** — no hidden state means each transformation can reason about the function in isolation.

In PyTorch, computing a per-sample gradient across a batch requires workarounds (e.g., `torch.func.vmap` was added much later, inspired by JAX). In JAX, it's a natural consequence of the design.

### The trade-off

JAX's model is more composable but more explicit. You manage parameters yourself (as pytrees), you thread state through function arguments, and you must think about what's a static argument vs a traced argument when JIT compiling.

PyTorch's model is more ergonomic for standard training loops but less composable for non-standard patterns (per-sample gradients, higher-order derivatives, custom parallelism strategies).

## Reflect

1. In PyTorch, `model.parameters()` gives you all trainable tensors and the optimizer updates them in-place. How would you represent a model's parameters in JAX, and how would a training step work without in-place mutation? (Think about what data structure holds parameters, and what the training step function's signature looks like.)

2. Consider `jax.jit(jax.vmap(jax.grad(loss_fn)))`. Read this inside-out and describe what each layer does. What does the final composed function compute? Why would this be useful in ML?

3. JAX's design forces purity. Can you think of a scenario in PyTorch where impurity (hidden state on tensors) leads to a subtle bug? For example: what happens if you accidentally call `loss.backward()` twice without zeroing gradients?
