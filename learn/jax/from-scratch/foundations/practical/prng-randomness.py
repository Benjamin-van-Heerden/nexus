"""
PRNG and Randomness — Practical Exercise
=========================================

Practice JAX's explicit key model through real scenarios.
"""

import jax
import jax.numpy as jnp
from jax import random

# =============================================================================
# PART 1: Key Basics
# =============================================================================

def exercise_1_key_basics():
    """
    Create a PRNG key, generate random values, and observe determinism.
    """
    # TODO: Create a key with seed 42
    key = None
    
    # TODO: Generate a (3, 3) normal array
    x1 = None
    
    # TODO: Generate another (3, 3) normal array using the SAME key
    x2 = None
    
    # TODO: Verify x1 and x2 are identical (they should be!)
    # Print whether jnp.allclose(x1, x2)
    
    # TODO: Now split the key, generate two (3, 3) arrays with subkeys
    # Verify they are DIFFERENT


# =============================================================================
# PART 2: Initialize a Small Neural Network
# =============================================================================

def init_dense(key, in_features, out_features):
    """
    Initialize weights (He init) and biases for a dense layer.
    
    Weights: random normal scaled by sqrt(2 / in_features)
    Biases: zeros
    
    Must split the key for weights and biases.
    """
    # TODO: Implement
    pass


def init_mlp(key, layer_sizes):
    """
    Initialize an MLP with given layer sizes.
    
    layer_sizes: list of ints, e.g., [784, 256, 10]
    Returns: list of parameter dicts [{'w': ..., 'b': ...}, ...]
    
    Must split the key for each layer.
    """
    # TODO: Implement
    pass


# =============================================================================
# PART 3: Batch Key Splitting
# =============================================================================

def generate_batch(key, batch_size, shape):
    """
    Generate `batch_size` random arrays of given `shape`.
    
    Each array in the batch must be independent.
    Return: (batch_size, *shape) array
    """
    # TODO: Split the key into batch_size subkeys
    # TODO: Use jax.vmap with jax.random.normal over the subkeys
    pass


# =============================================================================
# PART 4: Data Augmentation Keys
# =============================================================================

def augment_batch(key, images, noise_scale=0.1):
    """
    Add random Gaussian noise to a batch of images.
    
    images: (batch, height, width, channels)
    Must use the same noise key for all images (systematic noise),
    but you should split the key for potential future augmentations.
    
    Return: noisy images
    """
    # TODO: Split key for noise generation
    # TODO: Generate noise and add to images
    pass


# =============================================================================
# PART 5: Reproducible Dropout
# =============================================================================

def dropout(key, x, rate=0.5):
    """
    Apply dropout mask to x.
    
    x: array of any shape
    rate: probability of dropping (setting to zero)
    
    Must be reproducible: same key + same x → same mask.
    Return: (dropped_x, keep_mask)
    """
    # TODO: Generate mask using jax.random.bernoulli
    # TODO: Scale kept values by 1 / (1 - rate)
    pass


# =============================================================================
# PART 6: Key Tracking in Training Loop
# =============================================================================

def training_step(key, params, x, y, learning_rate):
    """
    Simulate a training step that needs randomness (e.g., dropout).
    
    Split the key into:
    - one for forward pass dropout
    - one for the next step (return this)
    
    Return: (updated_params, next_key)
    """
    # TODO: Split key for dropout and continuation
    # TODO: Apply dropout to x (using your dropout function)
    # TODO: Return params (mock update) and continuation key
    pass


# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("PRNG and Randomness — Practical Exercise")
    print("=" * 60)
    
    # Exercise 1
    print("\n--- Exercise 1: Key Basics ---")
    exercise_1_key_basics()
    
    # Exercise 2
    print("\n--- Exercise 2: Initialize MLP ---")
    key = jax.random.PRNGKey(0)
    params = init_mlp(key, [784, 256, 128, 10])
    print(f"Number of layers: {len(params)}")
    for i, p in enumerate(params):
        print(f"  Layer {i}: w={p['w'].shape}, b={p['b'].shape}")
    
    # Exercise 3
    print("\n--- Exercise 3: Batch Generation ---")
    key = jax.random.PRNGKey(1)
    batch = generate_batch(key, 4, (3, 3))
    print(f"Batch shape: {batch.shape}")
    
    # Exercise 4
    print("\n--- Exercise 4: Augmentation ---")
    key = jax.random.PRNGKey(2)
    images = jnp.ones((2, 28, 28, 1))
    noisy = augment_batch(key, images, noise_scale=0.1)
    print(f"Noisy images shape: {noisy.shape}")
    print(f"Mean difference: {jnp.mean(jnp.abs(noisy - images)):.4f}")
    
    # Exercise 5
    print("\n--- Exercise 5: Dropout ---")
    key = jax.random.PRNGKey(3)
    x = jnp.ones((5,))
    dropped, mask = dropout(key, x, rate=0.5)
    print(f"Original: {x}")
    print(f"Dropped:  {dropped}")
    print(f"Mask:     {mask}")
    
    # Exercise 6
    print("\n--- Exercise 6: Training Step Keys ---")
    key = jax.random.PRNGKey(4)
    params = init_mlp(key, [10, 5, 1])
    x = jnp.ones((10,))
    y = jnp.array(1.0)
    key, next_key = jax.random.split(key)
    updated, next_key = training_step(next_key, params, x, y, 0.01)
    print(f"Next key is different from input: {not jnp.allclose(key, next_key)}")
    
    print("\n" + "=" * 60)
    print("Done! Fill in all TODOs to complete the exercise.")
    print("=" * 60)
