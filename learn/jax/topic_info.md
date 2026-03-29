# JAX

## Background

Benjamin has extensive Python experience with NumPy, and has built many models in PyTorch and TensorFlow. He is also proficient in functional programming languages, so JAX's pure-function, no-side-effects paradigm should feel natural.

JAX is Google's numerical computing library that combines NumPy-like APIs with automatic differentiation, XLA compilation, and functional transformations (jit, grad, vmap, pmap). It is lower-level than PyTorch/TF — you compose primitives rather than using high-level abstractions.

## End Goal

Build up from JAX fundamentals to implementing production-grade deep learning architectures from scratch:

1. **Transformer from scratch** — implement multi-head attention, positional encoding, encoder/decoder stacks, and training loop using only JAX primitives
2. **DeepSeek mechanism from scratch** — implement mixture-of-experts routing, expert networks, and the DeepSeek-specific innovations in pure JAX
3. **Library-backed implementations** — reimplement both architectures using Flax (or similar JAX ecosystem library) to understand the ergonomic layer on top of raw JAX

## Learning Approach

Bottom-up: start with JAX's core transformations and mental model, build fluency with the functional paradigm as applied to ML, then progressively tackle more complex architectures. Leverage existing NumPy/PyTorch knowledge as anchoring points — many concepts transfer, but the functional patterns are different.
