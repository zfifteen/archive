def baseline_semiprime_enhanced(k: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Enhanced baseline semiprime approximation with better asymptotic behavior.
    
    This improves upon the basic π_2(x) inversion by incorporating
    higher-order correction terms for better accuracy.
    
    Parameters
    ----------
    k : float or array_like
        Index values for semiprime estimation
        
    Returns
    -------
    float or ndarray
        Enhanced baseline estimates of kth semiprime(s)
        
    Notes
    -----
    Formula: s_k ≈ k * log(k) / log(log(k + e)) * (1 + correction_terms)
    """
    k = _validate_semiprime_input(k)
    is_scalar = k.ndim == 0
    if is_scalar:
        k = k.reshape(1)
    
    result = np.zeros_like(k, dtype=np.float64)
    
    # Handle small k values explicitly
    small_mask = k <= 10
    if np.any(small_mask):
        # Known small semiprimes for better accuracy
        small_semiprimes = {1: 4, 2: 6, 3: 9, 4: 10, 5: 14, 
                          6: 15, 7: 21, 8: 22, 9: 25, 10: 26}
        
        for idx in np.where(small_mask)[0]:
            k_val = k[idx]
            k_int = int(round(k_val))
            if k_int in small_semiprimes:
                result[idx] = small_semiprimes[k_int]
            else:
                result[idx] = baseline_semiprime_approximation(k_int)
    
    # Handle larger k values with enhanced asymptotic
    large_mask = k > 10
    if np.any(large_mask):
        k_large = k[large_mask]
        
        # Enhanced asymptotic with correction terms
        log_k = np.log(k_large)
        log_log_k = np.log(log_k)
        
        # Base asymptotic: k * log(k) / log(log(k))
        base_estimate = k_large * log_k / log_log_k
        
        # First-order correction: accounts for next term in asymptotic expansion
        correction1 = k_large * log_k * (log_log_k - 1) / (log_log_k**2)
        
        # Second-order correction: improves accuracy for moderate k
        correction2 = k_large * log_k * (log_log_k - 2) / (log_log_k**2)
        
        # Combined enhanced estimate
        enhanced = base_estimate + 0.5 * correction1 + 0.1 * correction2
        
        result[large_mask] = enhanced
    
    return float(result[0]) if is_scalar else result