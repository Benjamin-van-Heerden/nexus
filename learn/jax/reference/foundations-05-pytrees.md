# Pytrees

## What is a Pytree?

A pytree is any nested combination of Python containers (lists, tuples, dicts, namedtuples) with JAX arrays as leaves. This is JAX's native way of working with structured collections of arrays.

```python
# All of these are pytrees:
[array1, array2]
{'w': array, 'b': array}
{'layer1': {'w': array, 'b': array}, 'layer2': {'w': array, 'b': array}}
(array1, [array2, array3])
```

## Why Pytrees Matter

Neural network parameters are naturally tree-structured — layers contain weights and biases, networks contain layers. In PyTorch, you use `nn.Module` and `state_dict()` to manage this. In JAX, pytrees *are* the parameter structure. No special class needed.

All JAX transformations natively understand pytrees:
- `jax.grad(loss)(params, x, y)` returns a pytree of gradients with the same structure as `params`
- `jax.jit` traces through pytree inputs/outputs
- `jax.vmap` can batch over pytree leaves

## tree_map

Apply a function to every leaf in a pytree:

```python
# SGD update in one line
new_params = jax.tree.map(lambda p, g: p - lr * g, params, grads)
```

`tree_map` takes multiple pytrees and applies the function leaf-by-leaf. They must have the same structure.

## Other tree utilities

```python
jax.tree.leaves(tree)        # flat list of all leaf arrays
jax.tree.structure(tree)     # the tree structure without leaves
jax.tree.map(fn, tree)       # apply fn to every leaf
jax.tree.reduce(fn, tree)    # reduce all leaves
```

## Custom pytree nodes

By default, only standard Python containers are pytree nodes. Custom classes can be registered:

```python
from jax.tree_util import register_pytree_node_class

@register_pytree_node_class
class Params:
    def __init__(self, w, b):
        self.w = w
        self.b = b

    def tree_flatten(self):
        return (self.w, self.b), None  # (children, aux_data)

    @classmethod
    def tree_unflatten(cls, aux_data, children):
        return cls(*children)
```

## Mental Model

Pytrees replace PyTorch's `nn.Module` parameter management. Instead of a class hierarchy with `.parameters()` and `state_dict()`, you have plain nested dicts that every JAX function understands natively. This is simpler but requires a different way of thinking about parameter organization.

## What to Practice

- Build a parameter dict for a simple MLP
- Use `tree_map` to apply transformations (e.g., SGD update, L2 norm per param)
- Flatten and unflatten a pytree
- Pass pytree params through `jax.grad` and verify the gradient structure matches
