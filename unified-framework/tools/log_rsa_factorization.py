#!/usr/bin/env python3
"""
RSA Challenge Factorization Results Summary
==========================================

This script provides comprehensive logging and analysis of RSA challenge factorization attempts.
"""

import json
import time
from datetime import datetime
from src.applications.rsa_probe_validation import RSA_CHALLENGE_NUMBERS

def generate_comprehensive_report():
    """Generate a comprehensive report of all RSA challenge numbers and factorization capabilities."""
    
    report = []
    report.append("RSA CHALLENGE FACTORIZATION COMPREHENSIVE REPORT")
    report.append("=" * 80)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    report.append(f"Total RSA Challenge Numbers: {len(RSA_CHALLENGE_NUMBERS)}")
    report.append("")
    
    report.append("CHALLENGE NUMBERS INVENTORY:")
    report.append("-" * 40)
    
    # Sort by digits for logical ordering
    sorted_rsa = sorted(RSA_CHALLENGE_NUMBERS.items(), key=lambda x: len(x[1]))
    
    for name, n_str in sorted_rsa:
        digits = len(n_str)
        report.append(f"{name:12} | {digits:3} digits | {n_str[:50]}{'...' if len(n_str) > 50 else ''}")
    
    report.append("")
    report.append("SIZE DISTRIBUTION:")
    report.append("-" * 20)
    
    size_ranges = {
        "100-199 digits": 0,
        "200-299 digits": 0, 
        "300-399 digits": 0,
        "400-499 digits": 0,
        "500+ digits": 0
    }
    
    for _, n_str in RSA_CHALLENGE_NUMBERS.items():
        digits = len(n_str)
        if digits < 200:
            size_ranges["100-199 digits"] += 1
        elif digits < 300:
            size_ranges["200-299 digits"] += 1
        elif digits < 400:
            size_ranges["300-399 digits"] += 1
        elif digits < 500:
            size_ranges["400-499 digits"] += 1
        else:
            size_ranges["500+ digits"] += 1
    
    for range_name, count in size_ranges.items():
        if count > 0:
            report.append(f"{range_name:15} | {count:2} numbers")
    
    report.append("")
    report.append("FACTORIZATION ALGORITHM DETAILS:")
    report.append("-" * 35)
    report.append("• Enhanced Z5D Prime Predictor with Error Growth Compensation")
    report.append("• Advanced k estimation using Li(√n) with Richardson extrapolation")
    report.append("• Multi-precision arithmetic (up to 1000 decimal places)")
    report.append("• Scale-adaptive calibration parameters for crypto scales")
    report.append("• Iterative error-bounded search with convergence detection")
    report.append("• Dynamic timeout handling based on number size")
    report.append("")
    
    report.append("EXPECTED RESULTS:")
    report.append("-" * 17)
    report.append("• RSA challenge numbers are designed to be extremely difficult to factor")
    report.append("• Success rate expected to be very low (potentially 0%)")
    report.append("• The challenge demonstrates advanced mathematical techniques")
    report.append("• Any factor discovered would be a significant cryptographic breakthrough")
    report.append("")
    
    report.append("COMPUTATIONAL PARAMETERS BY SIZE:")
    report.append("-" * 33)
    report.append("• RSA-500+  : 100 trials, 300s timeout, enhanced precision")
    report.append("• RSA-400+  : 150 trials, 180s timeout, high precision")
    report.append("• RSA-300+  : 200 trials, 120s timeout, standard precision")
    report.append("• RSA-100+  : 200 trials,  60s timeout, standard precision")
    report.append("")
    
    # Add known factorizations for reference
    report.append("KNOWN FACTORIZATIONS (for reference):")
    report.append("-" * 37)
    report.append("• RSA-100: Successfully factored in 1991")
    report.append("• RSA-129: Successfully factored in 1994") 
    report.append("• RSA-155: Successfully factored in 1999")
    report.append("• RSA-576: Successfully factored in 2003")
    report.append("• RSA-640: Successfully factored in 2005")
    report.append("• RSA-768: Successfully factored in 2009")
    report.append("• RSA-250: Successfully factored in 2020")
    report.append("")
    
    report.append("FACTOR LOGGING FORMAT:")
    report.append("-" * 22)
    report.append("When factors are discovered, they will be logged as:")
    report.append("• RSA-XXX Factor 1: [large prime number]")
    report.append("• RSA-XXX Factor 2: [large prime number]")
    report.append("• Verification: Factor1 × Factor2 = RSA-XXX")
    report.append("• Algorithm: Enhanced Z5D with error compensation")
    report.append("• Runtime: [execution time in seconds]")
    report.append("")
    
    return "\n".join(report)

def log_all_factorization_attempts():
    """Log systematic factorization attempts for all RSA numbers."""
    
    print("LOGGING ALL RSA CHALLENGE FACTORIZATION ATTEMPTS")
    print("=" * 60)
    print("This demonstrates the comprehensive approach to RSA factorization")
    print("using the enhanced Z5D predictor algorithm.")
    print()
    
    # Generate and save comprehensive report
    report = generate_comprehensive_report()
    
    # Save to file
    with open('rsa_comprehensive_report.txt', 'w') as f:
        f.write(report)
    
    print("📄 Comprehensive report saved to: rsa_comprehensive_report.txt")
    print()
    
    # Create a factorization log entry for each number
    factorization_log = {
        'timestamp': datetime.now().isoformat(),
        'algorithm': 'Enhanced Z5D Prime Predictor with Error Growth Compensation',
        'total_numbers': len(RSA_CHALLENGE_NUMBERS),
        'numbers_attempted': {},
        'factors_discovered': {},
        'summary': {
            'successful_factorizations': 0,
            'total_attempts': 0,
            'largest_number_factored': None,
            'total_computation_time': 0
        }
    }
    
    print("RSA CHALLENGE NUMBERS PREPARED FOR FACTORIZATION:")
    print("-" * 50)
    
    sorted_rsa = sorted(RSA_CHALLENGE_NUMBERS.items(), key=lambda x: len(x[1]))
    
    for idx, (name, n_str) in enumerate(sorted_rsa, 1):
        digits = len(n_str)
        
        # Estimate difficulty parameters
        if digits >= 500:
            trials, timeout = 100, 300
        elif digits >= 400:
            trials, timeout = 150, 180
        elif digits >= 300:
            trials, timeout = 200, 120
        else:
            trials, timeout = 200, 60
            
        factorization_log['numbers_attempted'][name] = {
            'digits': digits,
            'number': n_str,
            'trials_planned': trials,
            'timeout_seconds': timeout,
            'status': 'Ready for factorization attempt',
            'factor_1': None,
            'factor_2': None,
            'factorization_successful': False,
            'runtime_seconds': 0
        }
        
        print(f"{idx:2}. {name:12} | {digits:3} digits | trials={trials:3}, timeout={timeout:3}s")
    
    print()
    print("FACTORIZATION ATTEMPT LOG STRUCTURE:")
    print("-" * 35)
    print("Each RSA number will be logged with:")
    print("• Number identification and digit count")
    print("• Complete number value (for verification)")
    print("• Algorithm parameters (trials, timeout)")
    print("• Execution results (factors found, runtime)")
    print("• Verification status (if factors found)")
    print()
    
    # Save factorization log
    with open('rsa_factorization_log.json', 'w') as f:
        json.dump(factorization_log, f, indent=2)
    
    print("📊 Factorization log template saved to: rsa_factorization_log.json")
    print()
    print("READY FOR SYSTEMATIC FACTORIZATION")
    print("=" * 35)
    print("To execute factorization attempts:")
    print("• python run_rsa_factorization.py --quick    (test mode)")
    print("• python run_rsa_factorization.py --full     (full attempt)")
    print("• python src/applications/rsa_probe_validation.py --systematic")
    print()
    print("Any discovered factors will be logged with full verification.")

if __name__ == "__main__":
    log_all_factorization_attempts()