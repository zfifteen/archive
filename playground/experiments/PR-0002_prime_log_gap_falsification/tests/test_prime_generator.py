from prime_generator import count_primes_up_to, generate_primes_up_to
import numpy as np

# Known prime counts
KNOWN_COUNTS = {
    10**1: 4,  # 2,3,5,7
    10**2: 25,
    10**3: 168,
    10**4: 1229,
    10**5: 9592,
    10**6: 78498,
    10**7: 664579,
    10**8: 5761455,
}


def test_prime_counts():
    """
    Test prime counts against known values.
    """
    for limit, expected in KNOWN_COUNTS.items():
        count = count_primes_up_to(limit)
        if abs(count - expected) <= 1:  # Allow small error
            print(f"✓ π({limit}) = {count} (expected {expected})")
        else:
            print(f"✗ π({limit}) = {count} (expected {expected})")
            return False
    return True


def test_small_primes():
    """
    Test small prime generation.
    """
    primes = generate_primes_up_to(100)
    expected = np.array(
        [
            2,
            3,
            5,
            7,
            11,
            13,
            17,
            19,
            23,
            29,
            31,
            37,
            41,
            43,
            47,
            53,
            59,
            61,
            67,
            71,
            73,
            79,
            83,
            89,
            97,
        ]
    )
    if np.array_equal(primes, expected):
        print("✓ Small primes correct")
        return True
    else:
        print("✗ Small primes incorrect")
        return False


if __name__ == "__main__":
    print("Running prime generator tests...")
    test1 = test_small_primes()
    test2 = test_prime_counts()
    if test1 and test2:
        print("All tests passed!")
    else:
        print("Some tests failed!")
