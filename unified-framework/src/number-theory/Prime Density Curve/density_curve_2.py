import mpmath
import numpy as np  # Handles arrays and mathematical operations
import matplotlib.pyplot as plt  # For creating visualizations
from mpl_toolkits.mplot3d import Axes3D  # Adds 3D plotting capabilities


# Function to check if a number is prime
def is_prime(n):
    """
    Returns True if the number n is prime, otherwise returns False.
    - A prime number is greater than 1 and is divisible only by 1 and itself.
    - For optimization, numbers are checked only up to their square root.
    """
    if n < 2:  # Numbers less than 2 are not prime
        return False
    if n == 2:  # 2 is the only even prime number
        return True
    if n % 2 == 0:  # Even numbers greater than 2 are not prime
        return False
    # Check divisibility for odd numbers from 3 to sqrt(n)
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

# Function to calculate curvature (κ)
def kappa(n):
    """
    Computes the curvature κ(n) for a given number n.
    - Curvature is based on the number of divisors (d(n)) and the logarithm of n.
    - Formula: κ(n) = d(n) * log(n + 1) / e²
      - d(n): Number of divisors of n
      - log(n + 1): Adds a growth factor to the divisor count
      - e²: Euler's number squared smooths the result
    """
    # Count divisors of n using a list comprehension
    d_n = len([i for i in range(1, n + 1) if n % i == 0])
    # Calculate curvature
    return d_n * np.log(n + 1) / np.exp(2)

# Upper limit for numbers to analyze
N = 500
# Create a list of numbers from 2 to N
nums = np.arange(2, N + 1)

# Calculate κ(n) for all numbers in the range
kappas = np.array([kappa(n) for n in nums])
# Check if each number in the range is prime
is_primes = np.array([is_prime(n) for n in nums])

# Prepare 3D scatter data
x = nums  # x-axis: numbers
y = kappas  # y-axis: curvature values
z = np.zeros_like(x)  # z-axis will separate primes from composites
z[is_primes] = 1  # Mark primes with "1" on the z-axis

# Generate helical coordinates for visualization
theta = 2 * np.pi * nums / HELIX_NUMBERS_PER_TURN  # Angle for the helix (see HELIX_NUMBERS_PER_TURN above)
r = kappas / max(kappas)  # Normalize curvature values to act as radius
x_helix = r * np.cos(theta)  # x-coordinates on the helix (horizontal projection)
y_helix = r * np.sin(theta)  # y-coordinates on the helix (vertical projection)
z_helix = nums  # z-coordinates: linear mapping of numbers along the helix

# Create a figure for plotting
fig = plt.figure(figsize=(18, 5))

# Plot 1: 3D Scatter Plot of Prime and Composite Numbers
ax1 = fig.add_subplot(131, projection='3d')
# Plot composites (non-prime numbers)
ax1.scatter(x[~is_primes], y[~is_primes], z[~is_primes], c='gray', label='Composite', alpha=0.5)
# Plot primes
ax1.scatter(x[is_primes], y[is_primes], z[is_primes], c='red', label='Prime')
ax1.set_title("3D Scatter (n, κ(n), PrimeFlag)")  # Plot title
ax1.set_xlabel("n")  # Label for x-axis
ax1.set_ylabel("κ(n)")  # Label for y-axis
ax1.set_zlabel("Prime Flag")  # Label for z-axis
ax1.legend()  # Add a legend for clarity

# Plot 2: A 3D Ridge Showing Curvature κ(n) Over the Numbers
ax2 = fig.add_subplot(132, projection='3d')
# Create a line plot showing curvature values
ax2.plot(x, y, zs=0, zdir='z', label='κ(n)', color='blue')
ax2.set_title("3D Curvature Ridge")  # Title to describe the visualization
ax2.set_xlabel("n")  # Label for x-axis
ax2.set_ylabel("κ(n)")  # Label for y-axis
ax2.set_zlabel("z")  # Default z-axis (arbitrary here)

# Plot 3: Helical Projection of Curvature κ(n)
ax3 = fig.add_subplot(133, projection='3d')
# Plot the helical trajectory
ax3.plot(x_helix, y_helix, z_helix, label='κ(n) helix', color='purple')
# Highlight primes on the helix for contrast
ax3.scatter(x_helix[is_primes], y_helix[is_primes], z_helix[is_primes], c='red', label='Prime')
ax3.set_title("Helical Projection of κ(n)")  # Title for the 3D helix
ax3.set_xlabel("x (κ*cosθ)")  # Horizontal projection axis for the helix
ax3.set_ylabel("y (κ*sinθ)")  # Vertical projection axis for the helix
ax3.set_zlabel("n")  # Numbers along the helix
ax3.legend()  # Add a legend to distinguish primes from the helix line

# Adjust layout and display all plots
plt.tight_layout()  # Automatically adjust spaces between plots
plt.show()  # Render the plots
