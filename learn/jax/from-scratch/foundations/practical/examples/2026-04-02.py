import jax
import jax.numpy as jnp
import time

"""
JAX Transformations: jit and grad

This exercise covers:
- jax.jit for compilation and speedup
- Understanding tracing behavior
- jax.grad for automatic differentiation
- jax.value_and_grad for efficiency
- Composing jit and grad together

Run with: uv run python practical/examples/2026-04-02.py
"""


def slow_function(x):
    """
    A deliberately slow function to demonstrate jit speedup.
    Computes: sum of element-wise squares with a loop.
    
    Args:
        x: JAX array of any shape
        
    Returns:
        Scalar sum of squares
    """
    result = 0.0
    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            result += x[i, j] ** 2
    return result


def demonstrate_jit_speedup():
    """
    TODO: Implement this function to demonstrate jit speedup.
    
    Steps:
    1. Create a 1000x1000 random array
    2. Time the slow_function (call it once first to compile, then time 10 calls)
    3. Create a jitted version using jax.jit
    4. Time the jitted version (call it once first to compile, then time 10 calls)
    5. Print the speedup ratio
    
    HINT: Use .block_until_ready() for accurate timing
    """
    raise NotImplementedError("Implement demonstrate_jit_speedup()")


def safe_exp(x, threshold=5.0):
    """
    TODO: Implement a "safe" exponential that caps the input.
    
    This function should:
    - Return jnp.exp(x) when x < threshold
    - Return jnp.exp(threshold) when x >= threshold
    
    This naive Python implementation has a problem with jit.
    
    Args:
        x: Scalar or array input
        threshold: The cap value (Python float)
        
    Returns:
        Capped exponential
    """
    # TODO: Implement using regular Python if statement
    # This will demonstrate the tracing issue!
    raise NotImplementedError("Implement safe_exp()")


def safe_exp_jax(x, threshold=5.0):
    """
    TODO: Implement the same safe_exp but using jax.lax.cond
    
    This version should work correctly inside a jitted function.
    
    Args:
        x: Scalar or array input
        threshold: The cap value (Python float)
        
    Returns:
        Capped exponential
    """
    raise NotImplementedError("Implement safe_exp_jax()")


def quadratic(x):
    """
    A simple quadratic function: f(x) = 3x^2 + 2x + 1
    
    Args:
        x: Scalar input
        
    Returns:
        Scalar output
    """
    return 3 * x ** 2 + 2 * x + 1


def compute_gradient():
    """
    TODO: Use jax.grad to compute the gradient of quadratic at x=5.0
    
    Analytically: f'(x) = 6x + 2, so f'(5) = 32
    
    Returns:
        The gradient value (should be 32.0)
    """
    raise NotImplementedError("Implement compute_gradient()")


def compute_second_derivative():
    """
    TODO: Compute the second derivative of quadratic at x=5.0
    
    Analytically: f''(x) = 6, so f''(5) = 6
    
    HINT: Compose grad(grad(...))
    
    Returns:
        The second derivative value (should be 6.0)
    """
    raise NotImplementedError("Implement compute_second_derivative()")


def mse_loss(params, x, y):
    """
    Mean squared error for linear regression: y_pred = params[0] * x + params[1]
    
    Args:
        params: Tuple/array of (slope, intercept)
        x: Input features
        y: True targets
        
    Returns:
        Scalar MSE loss
    """
    predictions = params[0] * x + params[1]
    return jnp.mean((predictions - y) ** 2)


def training_step(params, x, y, lr=0.01):
    """
    TODO: Implement a single training step using value_and_grad.
    
    Steps:
    1. Compute loss and gradients w.r.t. params using value_and_grad
    2. Update params: params_new = params - lr * grads
    3. Return (loss, new_params)
    
    Args:
        params: Current parameters (slope, intercept)
        x: Input features
        y: True targets  
        lr: Learning rate
        
    Returns:
        Tuple of (loss_value, new_params)
    """
    raise NotImplementedError("Implement training_step()")


def create_fast_training_step(lr=0.01):
    """
    TODO: Create a jitted version of the training step.
    
    Return a jitted function that takes (params, x, y) and returns (loss, new_params).
    The learning rate should be baked in (hint: use static_argnums or partial).
    
    Args:
        lr: Learning rate to use
        
    Returns:
        Jitted training step function
    """
    raise NotImplementedError("Implement create_fast_training_step()")


if __name__ == "__main__":
    print("=" * 60)
    print("JAX Transformations: jit and grad")
    print("=" * 60)
    
    # Test 1: JIT Speedup
    print("\n1. Testing JIT speedup...")
    try:
        demonstrate_jit_speedup()
        print("   ✓ demonstrate_jit_speedup() completed")
    except NotImplementedError:
        print("   ⏸ demonstrate_jit_speedup() not implemented yet")
    
    # Test 2: Tracing behavior with Python control flow
    print("\n2. Testing tracing behavior...")
    try:
        x_test = jnp.array([1.0, 6.0, 3.0])
        
        # Test naive version
        print("   Testing safe_exp (Python if)...")
        result_naive = safe_exp(x_test, threshold=5.0)
        print(f"   Input: {x_test}")
        print(f"   Output: {result_naive}")
        
        # This will likely fail or behave unexpectedly with jit
        try:
            jitted_safe_exp = jax.jit(safe_exp, static_argnums=(1,))
            result_jitted = jitted_safe_exp(x_test, 5.0)
            print(f"   Jitted output: {result_jitted}")
        except Exception as e:
            print(f"   Note: Jitted version may have issues: {type(e).__name__}")
        
        # Test JAX version
        print("\n   Testing safe_exp_jax (jax.lax.cond)...")
        result_jax = safe_exp_jax(x_test, threshold=5.0)
        print(f"   Input: {x_test}")
        print(f"   Output: {result_jax}")
        
        # This should work correctly
        jitted_safe_exp_jax = jax.jit(safe_exp_jax, static_argnums=(1,))
        result_jitted_jax = jitted_safe_exp_jax(x_test, 5.0)
        print(f"   Jitted output: {result_jitted_jax}")
        
        # Verify correctness
        expected = jnp.array([jnp.exp(1.0), jnp.exp(5.0), jnp.exp(3.0)])
        assert jnp.allclose(result_jitted_jax, expected), "safe_exp_jax produced incorrect results"
        print("   ✓ safe_exp tests passed")
    except NotImplementedError:
        print("   ⏸ safe_exp functions not implemented yet")
    except AssertionError as e:
        print(f"   ✗ safe_exp test failed: {e}")
    except Exception as e:
        print(f"   ? safe_exp test had error: {e}")
    
    # Test 3: Gradients
    print("\n3. Testing gradients...")
    try:
        grad_result = compute_gradient()
        assert jnp.isclose(grad_result, 32.0), f"Expected 32.0, got {grad_result}"
        print(f"   f'(5.0) = {grad_result} (expected 32.0)")
        print("   ✓ compute_gradient() passed")
    except NotImplementedError:
        print("   ⏸ compute_gradient() not implemented yet")
    except AssertionError as e:
        print(f"   ✗ compute_gradient() failed: {e}")
    
    # Test 4: Second derivatives
    print("\n4. Testing second derivatives...")
    try:
        second_deriv = compute_second_derivative()
        assert jnp.isclose(second_deriv, 6.0), f"Expected 6.0, got {second_deriv}"
        print(f"   f''(5.0) = {second_deriv} (expected 6.0)")
        print("   ✓ compute_second_derivative() passed")
    except NotImplementedError:
        print("   ⏸ compute_second_derivative() not implemented yet")
    except AssertionError as e:
        print(f"   ✗ compute_second_derivative() failed: {e}")
    
    # Test 5: Training step
    print("\n5. Testing training step...")
    try:
        # Simple linear data: y = 2x + 1
        x_data = jnp.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y_data = 2.0 * x_data + 1.0
        
        # Initial params
        params = (jnp.array(0.0), jnp.array(0.0))  # Start with 0 slope, 0 intercept
        
        loss, new_params = training_step(params, x_data, y_data, lr=0.1)
        
        print(f"   Initial params: {params}")
        print(f"   Loss: {loss:.4f}")
        print(f"   New params: ({new_params[0]:.4f}, {new_params[1]:.4f})")
        
        # Loss should decrease from initial
        assert loss > 0, "Loss should be positive"
        assert not jnp.isnan(loss), "Loss should not be NaN"
        print("   ✓ training_step() passed")
    except NotImplementedError:
        print("   ⏸ training_step() not implemented yet")
    except AssertionError as e:
        print(f"   ✗ training_step() failed: {e}")
    except Exception as e:
        print(f"   ? training_step() error: {e}")
    
    # Test 6: Fast training step (jitted)
    print("\n6. Testing jitted training step...")
    try:
        fast_step = create_fast_training_step(lr=0.1)
        
        # Run multiple steps
        params = (jnp.array(0.0), jnp.array(0.0))
        losses = []
        
        for i in range(5):
            loss, params = fast_step(params, x_data, y_data)
            losses.append(float(loss))
        
        print(f"   Loss trajectory: {[f'{l:.4f}' for l in losses]}")
        
        # Loss should generally decrease
        assert losses[0] > losses[-1], "Loss should decrease over training"
        print("   ✓ create_fast_training_step() passed")
        print("\n   All tests completed! 🎉")
    except NotImplementedError:
        print("   ⏸ create_fast_training_step() not implemented yet")
    except AssertionError as e:
        print(f"   ✗ create_fast_training_step() failed: {e}")
    except Exception as e:
        print(f"   ? create_fast_training_step() error: {e}")
    
    print("\n" + "=" * 60)
    print("Implement the functions above and re-run to see all checks pass!")
    print("=" * 60)
