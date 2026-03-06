
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad

# The core mathematical function for Periodic Integral Modulation
def f(x):
    """The core periodic modulation function."""
    return 1 / (1 + np.exp(np.sin(x)))

def demonstrate_integral_property():
    """
    Demonstrates that the definite integral of f(x) from 0 to 2π is exactly π.
    This is a known mathematical identity ∫₀²π dx / (1 + e^sin(x)) = π.
    """
    print("1. The Integral Property: ∫₀²π f(x) dx = π")
    print("-------------------------------------------------")
    
    # Perform the numerical integration
    integral_result, error = quad(f, 0, 2 * np.pi)
    
    print(f"  Numerical integration result: {integral_result:.15f}")
    print(f"  Exact value of π:             {np.pi:.15f}")
    print(f"  Absolute error:               {abs(integral_result - np.pi):.2e}")
    
    # Check if the result is within a small tolerance of π
    is_exact = np.allclose(integral_result, np.pi)
    print(f"\n  Conclusion: The integral evaluates to π. (Validated: {is_exact})")
    print("-" * 49 + "\n")

def demonstrate_symmetry_property():
    """
    Demonstrates the symmetry property f(x) + f(x + π) = 1.
    This property shows a perfect balance in the function's values when shifted by π.
    """
    print("2. The Symmetry Property: f(x) + f(x + π) = 1")
    print("-------------------------------------------------")
    
    # Test the property at various points
    test_points = [0, np.pi/6, np.pi/4, np.pi/3, np.pi/2]
    
    print("  x (rad) | f(x)      | f(x+π)    | Sum (f(x)+f(x+π)) | Deviation from 1")
    print("  --------|-----------|-----------|-------------------|-----------------")
    
    max_deviation = 0
    for x in test_points:
        val1 = f(x)
        val2 = f(x + np.pi)
        total = val1 + val2
        deviation = abs(total - 1)
        max_deviation = max(max_deviation, deviation)
        print(f"  {x:^7.3f} | {val1:.7f} | {val2:.7f} | {total:.15f} | {deviation:.2e}")
        
    is_symmetric = np.allclose(max_deviation, 0)
    print(f"\n  Conclusion: The symmetry property holds across all test points. (Validated: {is_symmetric})")
    print("-" * 49 + "\n")

def visualize_function_and_properties():
    """
    Creates a plot to visualize the function f(x) and its symmetry.
    """
    print("3. Visualization")
    print("-------------------------------------------------")
    print("  Generating plot 'periodic_modulation_function.png'...")

    x_vals = np.linspace(0, 2 * np.pi, 400)
    y_vals = f(x_vals)
    
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Plot the function
    ax.plot(x_vals, y_vals, label='f(x) = 1 / (1 + e^sin(x))', color='blue', linewidth=2)
    
    # Shade the area under the curve to represent the integral
    ax.fill_between(x_vals, y_vals, color='lightblue', alpha=0.6, label='Area = ∫f(x)dx = π')
    
    # Demonstrate the symmetry
    # Plot f(x+π) and show it's equal to 1 - f(x)
    y_vals_shifted = f(x_vals + np.pi)
    ax.plot(x_vals, y_vals_shifted, label='f(x + π)', color='red', linestyle='--', linewidth=2)
    
    # Add annotations
    ax.set_title("Mathematical Properties of the Periodic Modulation Function", fontsize=16)
    ax.set_xlabel("x (radians)", fontsize=12)
    ax.set_ylabel("f(x)", fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True)
    
    # Set x-axis ticks to be in terms of π
    ax.set_xticks([0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi])
    ax.set_xticklabels(['0', 'π/2', 'π', '3π/2', '2π'])
    ax.set_xlim(0, 2 * np.pi)
    ax.set_ylim(0, 1)
    
    # Highlight a point and its symmetric counterpart
    x_point = np.pi / 4
    y_point = f(x_point)
    y_point_symm = f(x_point + np.pi)
    ax.plot([x_point, x_point + np.pi], [y_point, y_point_symm], 'ko')
    ax.vlines(x_point, 0, y_point, color='gray', linestyle=':')
    ax.vlines(x_point + np.pi, 0, y_point_symm, color='gray', linestyle=':')
    ax.text(x_point, y_point + 0.02, f'f(π/4)≈{y_point:.2f}', ha='center')
    ax.text(x_point + np.pi, y_point_symm + 0.02, f'f(5π/4)≈{y_point_symm:.2f}', ha='center')
    
    plt.savefig("periodic_modulation_function.png")
    print("  Plot saved successfully.")
    print("-" * 49 + "\n")


if __name__ == "__main__":
    print("=================================================")
    print("  The Mathematics of Periodic Integral Modulation")
    print("=================================================\n")
    demonstrate_integral_property()
    demonstrate_symmetry_property()
    visualize_function_and_properties()
    print("Demonstration complete.")
