# Quiz: PRNG and Randomness

## Question 1
What happens if you call `jax.random.normal(key, (3,))` twice with the **same** key?

- A) You get two different random arrays
- B) You get two identical arrays
- C) The second call raises an error
- D) JAX automatically advances the key

## Question 2
What is the correct pattern for generating independent random arrays?

- A) `x1 = random.normal(key, ...); x2 = random.normal(key, ...)`
- B) `key, k1, k2 = random.split(key, 3); x1 = random.normal(k1, ...); x2 = random.normal(k2, ...)`
- C) `x1 = random.normal(PRNGKey(0), ...); x2 = random.normal(PRNGKey(1), ...)`
- D) `x1 = random.normal(key); key = key + 1; x2 = random.normal(key)`

## Question 3
Why does JAX use explicit keys instead of global RNG state?

- A) It's more convenient for users
- B) Global mutable state breaks purity required by jit, grad, and vmap
- C) It's slower but more secure
- D) NumPy already uses global state, so JAX had to be different

## Question 4
In a training loop with dropout, how should you handle keys?

- A) Reuse the same key every step for reproducibility
- B) Split the key each step, using one subkey for dropout and keeping the rest for the next step
- C) Create a new PRNGKey(0) at every step
- D) Use a global random seed that increments each epoch

## Question 5
What algorithm does JAX use for its PRNG?

- A) Mersenne Twister (same as NumPy)
- B) Threefry (counter-based)
- C) Xorshift
- D) Cryptographically secure random (CSPRNG)

## Question 6
When initializing a neural network with multiple layers, what's the correct key pattern?

- A) Use the same key for every layer
- B) Split a key for each layer, giving each layer its own independent subkey
- C) Create a new PRNGKey with different seeds for each layer
- D) Use `random.split` only once at the beginning
