import math

def d(n):
    """
    Count the number of divisors of n.
    
    Args:
        n (int): The number to count divisors for.
    
    Returns:
        int: The number of divisors.
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")
    return sum(1 for i in range(1, n+1) if n % i == 0)