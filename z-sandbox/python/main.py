def main():
    parser = argparse.ArgumentParser(description="Geometric Resonance Factorization")
    parser.add_argument("--N", type=str, default="137524771864208156028430259349934309717", help="Number to factor")
    parser.add_argument("--dps", type=int, default=200, help="Decimal precision")
    parser.add_argument("--num_samples", type=int, default=801, help="Number of k samples")
    parser.add_argument("--k_lo", type=float, default=0.25, help="Lower k bound")
    parser.add_argument("--k_hi", type=float, default=0.45, help="Upper k bound")
    parser.add_argument("--m_span", type=int, default=180, help="Mode span")
    parser.add_argument("--J", type=int, default=6, help="Dirichlet kernel order")
    parser.add_argument("--bias", type=str, default="0.0", help="Bias value")
    parser.add_argument("--threshold", type=float, default=0.92, help="Dirichlet threshold multiplier")
    parser.add_argument("--output_dir", type=str, default="results", help="Output directory")
    args = parser.parse_args()
    
    N_int = int(args.N)
    config = {
        "mp.dps": args.dps,
        "num_samples": args.num_samples,
        "k_lo": args.k_lo,
        "k_hi": args.k_hi,
        "m_span": args.m_span,
        "J": args.J,
        "bias": args.bias,
        'm_span': 180,
        'J': 6,
        'bias_form': 'zero',
        'sampler': 'golden_ratio_qmc'
    }
    
    factors = factor_by_geometric_resonance(N_int, config)
    
    if factors[0] is not None:
        p, q, metadata = factors
        print(p)
        print(q)
        
        # Save artifacts
        with open('/tmp/config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        with open('/tmp/metrics.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Save candidates list
        with open('/tmp/candidates.txt', 'w') as f:
            # Re-generate to get full list
            cands = resonance_candidates(
                mpf(N_int),
                num_samples=config['num_samples'],
                k_lo=config['k_lo'],
                k_hi=config['k_hi'],
                m_span=config['m_span'],
                J=config['J']
            )
            for c in cands:
                f.write(f"{c}\n")
    else:
        print("No factors found")
        return 1
