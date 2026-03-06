#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rsa260_z5d_runner.py — Unified Z5D-powered RSA factorization orchestrator

Integrates all Z5D components:
- Z5D geometric prior for m₀ estimation
- Adaptive stepping (Δm ≈ k/(π·p̂))
- Integer-resonance line search
- Two-k vernier triangulation
- GCD-first gating (mandatory before PRP)
- Checkpoint/resume with STATE.json
- JSONL evidence logging
- Responsible disclosure (FACTORS.sealed)

Usage:
    python3 python/rsa260_z5d_runner.py --dps 2000 --k 0.30 --use-z5d-prior \\
        --adaptive-step --line-search --vernier-k2 0.31 \\
        --max-candidates 100000 --checkpoint STATE.json
"""

import argparse
import hashlib
import json
import sys
import time
import os
from dataclasses import dataclass, asdict
from typing import Optional, List, Tuple
from pathlib import Path

try:
    import mpmath as mp
except ImportError:
    print("FATAL: mpmath is required. Install with: pip install mpmath", file=sys.stderr)
    sys.exit(1)

try:
    from python.geom.z5d_predictor import predict_prime_near_sqrt
    from python.geom.m0_estimator import estimate_m0_from_z5d_prior
    from python.geom.adaptive_step import generate_symmetric_queue
    from python.geom.resonance_search import refine_m_with_line_search, integer_resonance_objective
    from python.geom.vernier_search import vernier_triangulation
    Z5D_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: Z5D modules not available: {e}", file=sys.stderr)
    Z5D_AVAILABLE = False


def enforce_precision_and_provenance(bitlen: int, required_multiplier: float = 2.0, 
                                   provenance_path: str = None) -> None:
    """
    Enforce sufficient mpmath precision for target modulus and log provenance.
    
    Args:
        bitlen: Bit length of target modulus
        required_multiplier: Decimal digit margin multiplier (default 2x)
        provenance_path: Path to append JSONL provenance (optional)
    
    Raises:
        RuntimeError: If mp.mp.dps is insufficient
    """
    import math
    import platform
    import time
    import os
    
    # Required dps: bits -> decimal digits with margin
    required_dps = int(math.ceil(required_multiplier * bitlen * math.log10(2)))
    current_dps = int(mp.mp.dps)
    
    if current_dps < required_dps:
        raise RuntimeError(
            f"Insufficient mpmath precision: mp.mp.dps={current_dps} < required {required_dps} "
            f"for {bitlen}-bit modulus. Set mp.mp.dps >= {required_dps} and retry."
        )
    
    # Log provenance if path provided
    if provenance_path:
        prov = {
            "timestamp": time.time(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "mp_mp_dps": mp.mp.dps,
            "required_mp_dps": required_dps,
            "git_commit": get_git_commit_sha(),
        }
        with open(provenance_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(prov, sort_keys=True) + "\n")


# RSA-260 constant
RSA_260_DECIMAL = (
    "2211282552952966643528108525502623092761208950247001539441374831912882294140"
    "2001986512729726569746599085900330031400051170742204560859276357953757185954"
    "2988389587092292384910067030341246205457845664136645406842143612930176940208"
    "46391065875914794251435144458199"
)


@dataclass
class RunState:
    """Checkpoint state for resume"""
    commit_sha: str
    N_label: str
    N: int
    k: float
    dps: int
    m0: float
    window: float
    use_z5d: bool
    adaptive_step: bool
    line_search: bool
    vernier_k2: Optional[float]
    candidates_seen: int
    gcd_calls: int
    prp_calls: int
    line_search_calls: int
    timestamp: float
    
    def to_dict(self):
        d = asdict(self)
        d['N'] = str(self.N)  # Convert to string for JSON
        return d
    
    @staticmethod
    def from_dict(d):
        d['N'] = int(d['N'])
        return RunState(**d)


@dataclass
class CandidateResult:
    """Result for a single candidate"""
    i: int
    m: float
    p_hat: str
    p_int: str
    rounding_mode: str
    gcd: int
    prp_result: Optional[bool]
    resonance_score: Optional[float]
    elapsed_ms: float
    timestamp: float


def get_git_commit_sha() -> str:
    """Get current git commit SHA"""
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            capture_output=True, text=True, cwd=os.path.dirname(__file__)
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:  # Intentionally ignore all exceptions: if git is unavailable or any error occurs,
        # we return "unknown" as the commit SHA is non-critical for main functionality.
        pass
    return "unknown"


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("ascii")).hexdigest()


def p_from_m(m: mp.mpf, k: float, logN: mp.mpf) -> mp.mpf:
    """Core comb formula"""
    return mp.exp((logN - (2 * mp.pi * m) / mp.mpf(k)) / 2)


def is_probable_prime(n: int, rounds: int = 32, seed: int = 0x5A17) -> bool:
    """Miller-Rabin PRP with deterministic seed"""
    if n < 2:
        return False
    
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for sp in small_primes:
        if n == sp:
            return True
        if n % sp == 0:
            return False
    
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    
    import random
    rng = random.Random(seed ^ n)
    
    for _ in range(rounds):
        a = rng.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        
        composite = True
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                composite = False
                break
        
        if composite:
            return False
    
    return True


def check_gcd_first(N: int, p_int: int) -> int:
    """GCD-first gating (mandatory)"""
    import math
    return math.gcd(N, p_int)


def log_candidate_jsonl(result: CandidateResult, log_file: str, state: RunState):
    """Append candidate result to JSONL log"""
    log_entry = {
        'timestamp': result.timestamp,
        'commit_sha': state.commit_sha,
        'N_label': state.N_label,
        'k': state.k,
        'dps': state.dps,
        'i': result.i,
        'm': result.m,
        'p_hat': result.p_hat,
        'p_int': result.p_int,
        'rounding_mode': result.rounding_mode,
        'gcd': result.gcd,
        'prp_result': result.prp_result,
        'resonance_score': result.resonance_score,
        'elapsed_ms': result.elapsed_ms,
        'cumulative_candidates': state.candidates_seen,
    }
    
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')


def save_checkpoint(state: RunState, checkpoint_file: str):
    """Save checkpoint state"""
    with open(checkpoint_file, 'w') as f:
        json.dump(state.to_dict(), f, indent=2)


def load_checkpoint(checkpoint_file: str) -> Optional[RunState]:
    """Load checkpoint state"""
    if not os.path.exists(checkpoint_file):
        return None
    
    try:
        with open(checkpoint_file, 'r') as f:
            data = json.load(f)
        return RunState.from_dict(data)
    except Exception as e:
        print(f"WARNING: Failed to load checkpoint: {e}", file=sys.stderr)
        return None


def seal_factors(N: int, p: int, q: int, seal_file: str = "FACTORS.sealed"):
    """Write factors to sealed file (chmod 600)"""
    seal_path = Path(seal_file)
    
    with open(seal_path, 'w') as f:
        f.write(f"# RSA Factorization Result (SEALED)\n")
        f.write(f"# Date: {time.ctime()}\n\n")
        f.write(f"N = {N}\n\n")
        f.write(f"p = {p}\n")
        f.write(f"q = {q}\n\n")
        f.write(f"# Verification: p * q = N\n")
        f.write(f"p * q = {p * q}\n")
        f.write(f"Match: {p * q == N}\n")
    
    # Set restrictive permissions (owner read/write only)
    seal_path.chmod(0o600)
    
    print(f"\n=== FACTORS SEALED ===")
    print(f"Factors written to: {seal_file}")
    print(f"Permissions: 600 (owner read/write only)")
    print(f"Use '--reveal {seal_file}' to display factors")


def run(args: argparse.Namespace) -> int:
    """Main runner"""
    
    # Setup precision
    mp.mp.dps = args.dps
    mp.mp.pretty = False
    
    # Load or create state
    state = None
    if args.resume and os.path.exists(args.checkpoint):
        state = load_checkpoint(args.checkpoint)
        if state:
            print(f"=== RESUMING FROM CHECKPOINT ===")
            print(f"Candidates seen: {state.candidates_seen}")
            print(f"GCD calls: {state.gcd_calls}")
            print(f"PRP calls: {state.prp_calls}")
            print(f"Timestamp: {time.ctime(state.timestamp)}\n")
    
    # Get N
    if args.N_source == "rsa260":
        N_dec = RSA_260_DECIMAL
        N_label = "RSA-260"
    elif args.N_source == "file":
        with open(args.N_file, 'r') as f:
            N_dec = f.read().strip()
        N_label = Path(args.N_file).stem
    else:
        print(f"FATAL: Unknown N source: {args.N_source}", file=sys.stderr)
        return 2
    
    N = int(N_dec)
    N_sha = sha256_hex(N_dec)
    n_bits = N.bit_length()
    n_digits = len(str(N))
    
    # Enforce precision and log provenance
    try:
        enforce_precision_and_provenance(n_bits, provenance_path=args.provenance_log)
    except RuntimeError as e:
        print(f"FATAL: {e}", file=sys.stderr)
        return 3
    
    logN = mp.log(mp.mpf(N))
    
    # Initialize state if new run
    if state is None:
        state = RunState(
            commit_sha=get_git_commit_sha(),
            N_label=N_label,
            N=N,
            k=args.k,
            dps=args.dps,
            m0=args.m0,
            window=args.window,
            use_z5d=args.use_z5d_prior,
            adaptive_step=args.adaptive_step,
            line_search=args.line_search,
            vernier_k2=args.vernier_k2,
            candidates_seen=0,
            gcd_calls=0,
            prp_calls=0,
            line_search_calls=0,
            timestamp=time.time()
        )
    
    # Log environment
    print("=== RSA-260 Z5D Runner ===")
    print(f"N ({N_label})     : bits={n_bits}, digits={n_digits}")
    print(f"N_sha256         : {N_sha}")
    print(f"dps              : {args.dps}")
    print(f"k                : {args.k}")
    print(f"commit_sha       : {state.commit_sha}\n")
    
    # Z5D prior
    m0_final = args.m0
    window_final = args.window
    
    if args.use_z5d_prior and Z5D_AVAILABLE:
        print("=== Z5D Prior ===")
        m0_z5d, window_z5d, epsilon_ppm, safety = estimate_m0_from_z5d_prior(N, args.k, args.dps)
        print(f"m₀ (Z5D)         : {mp.nstr(m0_z5d, 15)}")
        print(f"window (Z5D)     : {mp.nstr(window_z5d, 15)}")
        print(f"ε (ppm)          : {epsilon_ppm}")
        print(f"Safety mult      : {safety}\n")
        
        if args.m0 == 0.0:
            m0_final = float(m0_z5d)
        if args.window == 0.1:
            window_final = float(window_z5d)
    
    # Vernier (optional)
    if args.vernier_k2 is not None:
        print("=== Vernier Triangulation ===")
        print(f"k₁               : {args.k}")
        print(f"k₂               : {args.vernier_k2}")
        
        candidates_vernier = vernier_triangulation(
            N, args.k, args.vernier_k2, mp.mpf(m0_final), mp.mpf(window_final),
            coarse_step=args.vernier_step, threshold=args.vernier_threshold,
            top_k=args.vernier_top_k, dps=args.dps
        )
        
        print(f"Candidates       : {len(candidates_vernier)}\n")
        
        # Use vernier candidates as m queue
        m_queue = [m for m, score in candidates_vernier]
    
    # Adaptive step (if no vernier)
    elif args.adaptive_step:
        print("=== Adaptive Step ===")
        print(f"Generating symmetric queue with adaptive Δm...\n")
        
        m_queue = generate_symmetric_queue(
            mp.mpf(m0_final), mp.mpf(window_final), args.k, logN,
            p_from_m,
            max_candidates=args.max_candidates
        )
    
    # Fixed step (fallback)
    else:
        print("=== Fixed Step ===")
        print(f"m₀               : {m0_final}")
        print(f"window           : {window_final}")
        print(f"step             : {args.step}\n")
        
        # Generate fixed grid
        m_queue = []
        m_current = mp.mpf(m0_final) - mp.mpf(window_final)
        m_end = mp.mpf(m0_final) + mp.mpf(window_final)
        while m_current <= m_end:
            m_queue.append(m_current)
            m_current += mp.mpf(args.step)
    
    print(f"Queue size       : {len(m_queue)}")
    print(f"Max candidates   : {args.max_candidates}")
    print(f"Neighbor radius  : {args.neighbor_radius}\n")
    
    # Main search loop
    print("=== Search ===")
    start_time = time.time()
    
    for i, m in enumerate(m_queue):
        if state.candidates_seen >= args.max_candidates:
            print(f"\nReached max candidates limit: {args.max_candidates}")
            break
        
        iter_start = time.time()
        
        # Optional: line search refinement
        m_search = m
        resonance_score = None
        
        if args.line_search:
            m_search, resonance_score = refine_m_with_line_search(
                m, args.k, N, logN, delta=0.01, dps=args.dps
            )
            state.line_search_calls += 1
        
        # Compute p̂
        p_hat = p_from_m(m_search, args.k, logN)
        
        # Rounding modes + neighbors
        p_candidates = []
        p_round = int(mp.nint(p_hat))
        p_floor = int(mp.floor(p_hat))
        p_ceil = int(mp.ceil(p_hat))
        
        for p_base, mode in [(p_round, 'round'), (p_floor, 'floor'), (p_ceil, 'ceil')]:
            for delta in range(-args.neighbor_radius, args.neighbor_radius + 1):
                p_cand = p_base + delta
                if p_cand > 1 and p_cand < N:
                    p_candidates.append((p_cand, mode))
        
        # GCD-first gating
        for p_int, rounding_mode in p_candidates:
            state.candidates_seen += 1
            
            g = check_gcd_first(N, p_int)
            state.gcd_calls += 1
            
            prp_result = None
            if g == 1:
                # Only PRP if gcd=1 (for ranking/diagnostics)
                prp_result = is_probable_prime(p_int, rounds=args.prp_rounds)
                state.prp_calls += 1
            
            elapsed_ms = (time.time() - iter_start) * 1000
            
            # Log
            result = CandidateResult(
                i=i,
                m=float(m_search),
                p_hat=mp.nstr(p_hat, 20),
                p_int=str(p_int),
                rounding_mode=rounding_mode,
                gcd=g,
                prp_result=prp_result,
                resonance_score=float(resonance_score) if resonance_score else None,
                elapsed_ms=elapsed_ms,
                timestamp=time.time()
            )
            
            if args.log_file and state.candidates_seen % args.log_interval == 0:
                log_candidate_jsonl(result, args.log_file, state)
            
            # SUCCESS: gcd ∉ {1, N}
            if 1 < g < N:
                q = N // g
                
                print(f"\n=== SUCCESS ===")
                print(f"Candidates seen  : {state.candidates_seen}")
                print(f"GCD calls        : {state.gcd_calls}")
                print(f"PRP calls        : {state.prp_calls}")
                print(f"Elapsed          : {time.time() - start_time:.2f}s")
                print(f"\nm                : {mp.nstr(m_search, 15)}")
                print(f"p (bits={g.bit_length()}, digits={len(str(g))})")
                print(f"q (bits={q.bit_length()}, digits={len(str(q))})")
                print(f"\nVerification: p * q = N: {g * q == N}")
                
                # Seal factors
                seal_factors(N, g, q, seal_file=args.seal_file)
                
                # Save final checkpoint
                if args.checkpoint:
                    save_checkpoint(state, args.checkpoint)
                
                return 0
        
        # Periodic checkpoint
        if args.checkpoint and state.candidates_seen % 1000 == 0:
            save_checkpoint(state, args.checkpoint)
        
        # Progress
        if state.candidates_seen % args.log_interval == 0:
            elapsed = time.time() - start_time
            rate = state.candidates_seen / elapsed if elapsed > 0 else 0
            print(f"[{state.candidates_seen:6d}] m={mp.nstr(m_search, 12)}, "
                  f"gcd={state.gcd_calls}, prp={state.prp_calls}, "
                  f"rate={rate:.1f} cand/s")
    
    # Not found
    print(f"\n=== NOT FACTORED ===")
    print(f"Candidates seen  : {state.candidates_seen}")
    print(f"GCD calls        : {state.gcd_calls}")
    print(f"PRP calls        : {state.prp_calls}")
    print(f"Elapsed          : {time.time() - start_time:.2f}s")
    
    if args.checkpoint:
        save_checkpoint(state, args.checkpoint)
    
    return 1


def build_argparser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="rsa260_z5d_runner.py",
        description="Unified Z5D-powered RSA factorization orchestrator"
    )
    
    # N source
    ap.add_argument("--N_source", choices=["rsa260", "file"], default="rsa260")
    ap.add_argument("--N_file", type=str, default=None)
    
    # Precision
    ap.add_argument("--dps", type=int, default=2000,
                    help="mpmath decimal precision (≥2000 for RSA-260)")
    
    # Comb parameters
    ap.add_argument("--k", type=float, default=0.30,
                    help="Primary wave number")
    ap.add_argument("--m0", type=float, default=0.0,
                    help="Manual m₀ (overrides Z5D if non-zero)")
    ap.add_argument("--window", type=float, default=0.1,
                    help="Half-window (overrides Z5D if ≠0.1)")
    ap.add_argument("--step", type=float, default=0.0001,
                    help="Fixed step (if not using adaptive)")
    
    # Z5D prior
    ap.add_argument("--use-z5d-prior", action="store_true",
                    help="Enable Z5D geometric prior")
    
    # Adaptive step
    ap.add_argument("--adaptive-step", action="store_true",
                    help="Enable adaptive Δm stepping")
    
    # Line search
    ap.add_argument("--line-search", action="store_true",
                    help="Enable integer-resonance line search")
    
    # Vernier
    ap.add_argument("--vernier-k2", type=float, default=None,
                    help="Second k for vernier triangulation")
    ap.add_argument("--vernier-step", type=float, default=0.001,
                    help="Coarse step for vernier sweep")
    ap.add_argument("--vernier-threshold", type=float, default=3.0,
                    help="Minimum resonance threshold for vernier")
    ap.add_argument("--vernier-top-k", type=int, default=100,
                    help="Top K candidates from vernier")
    
    # Search limits
    ap.add_argument("--max-candidates", type=int, default=100000,
                    help="Maximum candidates to evaluate")
    ap.add_argument("--neighbor-radius", type=int, default=2,
                    help="Check p_int ± r neighbors")
    ap.add_argument("--prp-rounds", type=int, default=32,
                    help="Miller-Rabin rounds")
    
    # Logging & checkpoint
    ap.add_argument("--log-file", type=str, default=None,
                    help="JSONL log file (optional)")
    ap.add_argument("--log-interval", type=int, default=100,
                    help="Log every N candidates")
    ap.add_argument("--checkpoint", type=str, default=None,
                    help="Checkpoint file (STATE.json)")
    ap.add_argument("--resume", action="store_true",
                    help="Resume from checkpoint")
    ap.add_argument("--provenance-log", type=str, default=None,
                    help="Provenance JSONL log file (optional)")
    
    # Output
    ap.add_argument("--seal-file", type=str, default="FACTORS.sealed",
                    help="Sealed factors output file")
    
    return ap


if __name__ == "__main__":
    sys.setrecursionlimit(1000000)
    args = build_argparser().parse_args()
    exit_code = run(args)
    sys.exit(exit_code)
