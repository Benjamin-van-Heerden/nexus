# Device Residency and dtype Defaults

## Reading

JAX arrays are **device-resident** — they live on GPU/TPU (or CPU if no accelerator is available). This has practical consequences that don't exist in NumPy.

### Silent host-device transfers

When you mix `numpy` and `jax.numpy`, data silently transfers between host (CPU) and device:

```python
import numpy as np
import jax.numpy as jnp

x_np = np.ones(1000)       # lives on CPU (host memory)
x_jnp = jnp.ones(1000)     # lives on device

# This works, but silently copies x_np to device first:
result = x_jnp + x_np
```

In a tight loop or training step, these invisible transfers can dominate runtime. The fix: convert once at the boundary, then stay in `jnp` land.

### 32-bit default

NumPy defaults to `float64`. JAX defaults to `float32`. This is deliberate — GPUs are often 2-8x faster at float32, and for ML workloads float64 is almost never needed.

```python
np.array([1.0]).dtype       # float64
jnp.array([1.0]).dtype      # float32
```

You can opt into float64 with `jax.config.update("jax_enable_x64", True)`, but this is rarely necessary and comes with a performance cost on accelerators.

### Checking where arrays live

```python
x = jnp.ones(3)
x.devices()     # {CpuDevice(id=0)} or {CudaDevice(id=0)}
```

## Reflect

1. You have a training loop that calls a Python function which uses `scipy` (NumPy-based) for one step, then passes the result to a JAX function. What happens to the data at each boundary, and why is this a problem?

2. In PyTorch, you explicitly call `.to(device)` or `.cuda()` to move tensors. How does JAX's approach differ, and what are the trade-offs? Which failure mode is more dangerous — PyTorch's explicit errors or JAX's silent transfers?

3. Why would float32 be sufficient for gradient-based optimization? Think about what gradients are used for (parameter updates) vs what float64 gives you (precision). When might you actually need float64?
