    def z5d_guided_factor_search(self, n: int, search_radius: int = 1000) -> Optional[Tuple[int, int]]:
        """
        Z5D-guided factor search for semiprime n = p*q.

        Uses Z5D prediction to guide factorization.
        """
        if n < 4 or n % 2 == 0:
            return None  # Not a semiprime or too small

        # Simple estimate: p ≈ sqrt(n)
        sqrt_n = int(math.sqrt(n))
        p_estimate = sqrt_n

        # For Z5D, estimate k and get prediction
        try:
            k_est = self.estimate_semiprime_index(n)
            predicted_n = z5d_semiprime_variant(k_est)
            if predicted_n > 0:
                p_estimate = int(math.sqrt(predicted_n))
                print(f"Using Z5D prediction: predicted n ≈ {predicted_n:.0f}, p ≈ {p_estimate}")
        except Exception as e:
            print(f"Z5D prediction failed ({e}), using sqrt estimate")

        # Search around estimated p
        for offset in range(-search_radius, search_radius + 1):
            p_candidate = p_estimate + offset
            if p_candidate < 2:
                continue
            if n % p_candidate == 0:
                q_candidate = n // p_candidate
                if self.is_prime(p_candidate) and self.is_prime(q_candidate):
                    return (p_candidate, q_candidate)

        return None