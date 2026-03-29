# From Scratch — JAX to Transformers to DeepSeek

## What are we learning?

JAX from the ground up: starting with core transformations (jit, grad, vmap) and the functional programming model, building through neural network primitives, and culminating in from-scratch implementations of a transformer and the DeepSeek mixture-of-experts architecture. Final phase reimplements with Flax to understand the library abstraction layer.

## Why are we learning this?

Deep understanding of the transformer and MoE architectures at the implementation level — not just using library APIs, but understanding every matrix multiply, every gradient, every routing decision. JAX's functional model forces explicit parameter management and pure functions, which builds a much stronger mental model than PyTorch's implicit state.

## How will we learn?

Bottom-up progression. Each phase builds on the previous one. Practical exercises are the core — small runnable Python scripts that implement concepts. Given existing NumPy/PyTorch/functional programming background, we can move quickly through foundations and focus time on the architecture phases.

## Proposed Phases

1. **foundations** — JAX mental model, jit/grad/vmap, PRNG keys, pytrees, device management
2. **neural-net-primitives** — dense layers, activations, loss functions, training loops, parameter management without a framework
3. **attention-and-transformers** — attention mechanism, multi-head attention, positional encoding, full transformer implementation
4. **deepseek-moe** — mixture-of-experts routing, expert networks, DeepSeek-specific innovations
5. **flax-rebuild** — reimplement transformer and DeepSeek with Flax, understand the abstraction trade-offs

## Resources

- JAX documentation: https://jax.readthedocs.io/
- JAX GitHub: https://github.com/jax-ml/jax
- Flax documentation: https://flax.readthedocs.io/
- "Attention Is All You Need" (Vaswani et al., 2017)
- DeepSeek-V2/V3 technical reports
- Thinking in JAX (official tutorial)
