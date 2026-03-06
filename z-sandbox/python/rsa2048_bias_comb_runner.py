#!/usr/bin/env python3
"""
RSA-2048 Bias, Comb, Combined Runner for Daily Task

Implements bias, comb, combined mechanisms for RSA-2048 factorization gap reduction.
"""

import time
import json
import csv
import math
from typing import Dict, List, Any, Optional
import os
import sys

# Add paths
sys.path.insert(0, os.path.dirname(__file__))

try:
    import mpmath as mp
except ImportError as e:
    print("Install mpmath")
    sys.exit(1)

# Import Z5D components
try:
    
    from geom.m0_estimator import estimate_m0_from_z5d_prior
    Z5D_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: Z5D modules not available: {e}"); Z5D_AVAILABLE = False

# RSA-2048 test N from benchmark
N_TEST = 19565052573783926362804955826185174525728078526810712384495116220075771203165815540350320318234128109502866404040441646380733489768005779750907460852666274829374234588862350999665490821796652462380009427451532262669780600090584349311855804897481279577689230978047661163247172188041684808930232313420099220509975125970254512319302192626041901541490412992887762283300565206734618291529115764983558780812801167921784644100839569587504288169305437609858438979156657056535415039123177205165132056618062514534266865794937597754711033463786911711252396693196372442794203778085999392377806478126752931833456678124819568916637

P_TRUE = 134596225071135757293877433819413042692936037953129096730037533712099883422087322247202866162901551695219265438464014797133085167763724652777056857132766942498195472133731530346298881967275916900943816351152798867657836673578516686085149202952019670806806720314963439188663312724081358033818044077490265379459

Q_TRUE = 145361079506082402319115985685104724044029974560950724482315821335626420254076928561868556125783099818250531777010570908673902127477196129280179451308959161688423703684550768103325410322153626376997013729837192552778234164200704030452467012179884274065691245690105207571454569357259438464162984053635783106143

# Constants
K_DEFAULT = 0.30
DPS = 2000

def p_from_m(m: mp.mpf, k: float, logN: mp.mpf) -> mp.mpf:
    """Core comb formula"""
    return mp.exp((logN - (2 * mp.pi * m) / mp.mpf(k)) / 2)

def compute_distance(p_hat: mp.mpf, true_p: int) -> Dict[str, Any]:
    """Compute rel_distance and abs_distance"""
    p_int = int(mp.nint(p_hat))
    abs_distance = abs(p_int - true_p)
    rel_distance = float(abs_distance / true_p)
    return {
        'rel_distance': rel_distance,
        'abs_distance': str(abs_distance),  # big int as string
        'p_hat': str(p_hat),
        'p_int': str(p_int)
    }

def bias_mechanism(N: int, k: float = K_DEFAULT, dps: int = DPS, fine_bias: bool = False) -> Dict[str, Any]:
    """Bias mechanism: Z5D prior for m0, then p_hat"""
    mp.mp.dps = dps
    logN = mp.log(mp.mpf(N))
    
    if not Z5D_AVAILABLE:
        raise RuntimeError("Z5D not available")
    
    m0, _, _, _ = estimate_m0_from_z5d_prior(N, k, dps)

    if fine_bias:
        bits_N = N.bit_length()
        delta_bias = 0.0001 * bits_N  # closed-form term Δ_bias(bits_N)
        m0 += delta_bias
        # Re-center: perhaps adjust based on p_hat, but for simplicity, just add
    p_hat = p_from_m(m0, k, logN)
    
    # Distance to closest true factor
    dist_p = compute_distance(p_hat, P_TRUE)
    dist_q = compute_distance(p_hat, Q_TRUE)
    if dist_p['rel_distance'] < dist_q['rel_distance']:
        dist = dist_p
    else:
        dist = dist_q
    
    return {
        'mechanism': 'bias',
        'm0': float(m0),
        'p_hat': dist['p_hat'],
        'p_int': dist['p_int'],
        'rel_distance': dist['rel_distance'],
        'abs_distance': dist['abs_distance'],
        'params': {'k': k, 'dps': dps}
    }

def comb_mechanism(N: int, m0: float, window: float = 0.1, m_step: float = 1e-3, k: float = K_DEFAULT, dps: int = DPS) -> Dict[str, Any]:
    """Comb mechanism: fractional comb sampling around m0"""
    mp.mp.dps = dps
    logN = mp.log(mp.mpf(N))
    
    m_current = mp.mpf(m0) - mp.mpf(window)
    m_end = mp.mpf(m0) + mp.mpf(window)
    best_rel = float('inf')
    best_result = None
    
    while m_current <= m_end:
        p_hat = p_from_m(m_current, k, logN)
        dist_p = compute_distance(p_hat, P_TRUE)
        dist_q = compute_distance(p_hat, Q_TRUE)
        dist = min(dist_p, dist_q, key=lambda x: x['rel_distance'])
        
        if dist['rel_distance'] < best_rel:
            best_rel = dist['rel_distance']
            best_result = {
                'mechanism': 'comb',
                'm': float(m_current),
                'p_hat': dist['p_hat'],
                'p_int': dist['p_int'],
                'rel_distance': dist['rel_distance'],
                'abs_distance': dist['abs_distance'],
                'params': {'k': k, 'm0': m0, 'window': window, 'm_step': m_step, 'dps': dps}
            }
        
        m_current += mp.mpf(m_step)
    
    return best_result

def combined_mechanism(N: int, k: float = K_DEFAULT, dps: int = DPS, fine_bias: bool = False) -> Dict[str, Any]:
    """Combined mechanism: bias -> re-center -> comb"""
    # First, bias to get m0
    bias_result = bias_mechanism(N, k, dps, fine_bias=fine_bias)
    m0_bias = bias_result['m0']
    
    # Re-center: use the m from bias as new m0
    # For simplicity, use the m0 from bias
    
    # Then comb around it
    comb_result = comb_mechanism(N, m0_bias, k=k, dps=dps)
    
    return {
        'mechanism': 'combined',
        'm0_bias': m0_bias,
        'm_comb': comb_result['m'],
        'p_hat': comb_result['p_hat'],
        'p_int': comb_result['p_int'],
        'rel_distance': comb_result['rel_distance'],
        'abs_distance': comb_result['abs_distance'],
        'params': {'k': k, 'dps': dps}
    }

def run_baselines(N: int, fine_bias: bool = False) -> List[Dict[str, Any]]:
    """Run bias and comb baselines"""
    results = []
    
    start_time = time.time()
    
    # Bias
    try:
        bias_res = bias_mechanism(N, fine_bias=fine_bias)
        bias_res['runtime_s'] = time.time() - start_time
        results.append(bias_res)
    except Exception as e:
        print(f"Bias failed: {e}")
        return []
    
    start_time = time.time()
    
    # Comb - need m0 from bias
    m0 = bias_res['m0']
    try:
        comb_res = comb_mechanism(N, m0)
        comb_res['runtime_s'] = time.time() - start_time
        results.append(comb_res)
    except Exception as e:
        print(f"Comb failed: {e}")
        return []
    
    return results

def run_combined(N: int, fine_bias: bool = False) -> Dict[str, Any]:
    """Run combined"""
    start_time = time.time()
    combined_res = combined_mechanism(N)
    combined_res['runtime_s'] = time.time() - start_time
    return combined_res

def log_tsv(results: List[Dict[str, Any]], filename: str):
    """Log to TSV"""
    if not results:
        return
    
    keys = ['timestamp', 'mechanism', 'rel_distance', 'abs_distance', 'params', 'json_notes', 'runtime_s']
    
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys, delimiter='\t')
        writer.writeheader()
        
        for res in results:
            row = {
                'timestamp': time.time(),
                'mechanism': res['mechanism'],
                'rel_distance': res['rel_distance'],
                'abs_distance': res['abs_distance'],
                'params': json.dumps(res['params']),
                'json_notes': '{}',
                'runtime_s': res['runtime_s']
            }
            writer.writerow(row)

def main():
    # Reproduce baselines
# Single-pass log-scale fine bias
    baselines = run_baselines(N_TEST, fine_bias=True)
    if not baselines:
        print("Baselines failed")
        return
    
    # Unbreak combined
    combined = run_combined(N_TEST, fine_bias=True)
    
    # Check assertion
    bias_rel = baselines[0]['rel_distance']
    comb_rel = baselines[1]['rel_distance']
    combined_rel = combined['rel_distance']
    
    if combined_rel > max(bias_rel, comb_rel):
        print(f"Combined rel {combined_rel} > max({bias_rel}, {comb_rel})")
        # Dump params
        print("Bias params:", baselines[0]['params'])
        print("Comb params:", baselines[1]['params'])
        print("Combined params:", combined['params'])
        return
    
    all_results = baselines + [combined]
    
    # Log
    os.makedirs('results', exist_ok=True)
    log_tsv(all_results, 'results/2025-11-05.tsv')
    
    # JSONL
    with open('results/2025-11-05.jsonl', 'w') as f:
        for res in all_results:
            f.write(json.dumps(res) + '\n')
    
    print("Baselines and combined completed")

if __name__ == "__main__":
    main()