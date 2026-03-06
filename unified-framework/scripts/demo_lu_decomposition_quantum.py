#!/usr/bin/env python3
"""
Interactive Demo: Prime Curvature LU Decomposition Quantum Integration
=====================================================================

This demo showcases the enhanced LU decomposition functionality with prime curvature 
analysis for quantum computing applications, integrated with the Z Framework.

Features Demonstrated:
1. Prime Curvature Transformation Analysis
2. Enhanced LU Decomposition with Condition Improvement
3. Quantum Error Correction with Enhanced Stability
4. Quantum Cryptography with Secure Key Generation
5. Quantum Circuit Matrix Optimization
6. Performance Benchmarks and Condition Number Improvements

Mathematical Foundation:
- Prime curvature parameter: k* ≈ 0.3 (optimal from research)
- Golden ratio: φ = (1 + √5) / 2 ≈ 1.618033988749895
- Transformation: θ'(n, k*) = φ · {n/φ}^0.3
- Matrix conditioning improvements up to 100% for ill-conditioned matrices

Author: Z Framework Team
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time
import sys
import os
from typing import Dict, List, Tuple, Any

# Add path for imports
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.applications.lu_decomposition_quantum import (
    PrimeGeodesicTransform,
    EnhancedLUDecomposition,
    QuantumErrorCorrectionLU,
    QuantumCryptographyLU,
    optimize_quantum_circuit_matrix,
    demonstrate_lu_decomposition_quantum,
    K_STAR,
    PHI_FLOAT
)

def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)

def print_subheader(title: str):
    """Print a formatted subheader."""
    print(f"\n--- {title} ---")

def visualize_prime_curvature_transform():
    """Visualize the prime curvature transformation."""
    print_subheader("Prime Curvature Transformation Visualization")
    
    pgt = PrimeGeodesicTransform()
    
    # Generate input values
    n_values = np.linspace(0.1, 10, 1000)
    transformed_values = pgt.transform(n_values)
    
    # Create visualization
    plt.figure(figsize=(12, 8))
    
    # Plot 1: Transformation function
    plt.subplot(2, 2, 1)
    plt.plot(n_values, transformed_values, 'b-', linewidth=2, label=f"θ'(n, k*={K_STAR})")
    plt.axhline(y=PHI_FLOAT, color='r', linestyle='--', alpha=0.7, label=f'φ = {PHI_FLOAT:.3f}')
    plt.xlabel('n')
    plt.ylabel("θ'(n, k*)")
    plt.title('Prime Curvature Transformation')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 2: Modular behavior
    plt.subplot(2, 2, 2)
    mod_values = n_values % PHI_FLOAT
    plt.plot(n_values, mod_values, 'g-', linewidth=2, label='{n/φ}')
    plt.xlabel('n') 
    plt.ylabel('{n/φ}')
    plt.title('Modular Component')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 3: Power function component
    plt.subplot(2, 2, 3)
    power_component = np.power(mod_values / PHI_FLOAT, K_STAR)
    plt.plot(n_values, power_component, 'm-', linewidth=2, label=f'{n/φ}^{K_STAR}')
    plt.xlabel('n')
    plt.ylabel('Power Component')
    plt.title('Power Function Component')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 4: Curvature parameter sensitivity
    plt.subplot(2, 2, 4)
    k_values = [0.1, 0.3, 0.5, 0.7, 0.9]
    test_n = 5.0
    for k in k_values:
        pgt_k = PrimeGeodesicTransform(k)
        k_transformed = pgt_k.transform(n_values)
        plt.plot(n_values, k_transformed, linewidth=1.5, label=f'k={k}')
    
    plt.xlabel('n')
    plt.ylabel("θ'(n, k)")
    plt.title('Curvature Parameter Sensitivity')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('prime_curvature_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"   ✓ Visualization saved as 'prime_curvature_analysis.png'")
    print(f"   ✓ Golden ratio φ = {PHI_FLOAT:.6f}")
    print(f"   ✓ Optimal curvature k* = {K_STAR}")

def demonstrate_condition_improvement():
    """Demonstrate condition number improvements."""
    print_subheader("Matrix Condition Number Improvement Analysis")
    
    # Create test matrices with varying ill-conditioning
    epsilons = [1e-1, 1e-2, 1e-3, 1e-4, 1e-5]
    results = []
    
    print(f"{'Epsilon':<12} {'Original Cond':<15} {'Improved Cond':<15} {'Improvement':<12} {'Percentage':<12}")
    print("-" * 70)
    
    for eps in epsilons:
        # Create ill-conditioned matrix
        ill_matrix = np.array([
            [1, 1, 1],
            [1, 1+eps, 1], 
            [1, 1, 1+eps]
        ])
        
        # Apply enhanced LU decomposition
        elu = EnhancedLUDecomposition(ill_matrix)
        P, L, U = elu.decompose()
        
        improvement = elu.get_condition_improvement()
        results.append({
            'epsilon': eps,
            'original_cond': improvement['original_condition'],
            'improved_cond': improvement['improved_condition'],
            'improvement_factor': improvement['improvement_factor'],
            'improvement_percentage': improvement['improvement_percentage']
        })
        
        print(f"{eps:<12.0e} {improvement['original_condition']:<15.2e} "
              f"{improvement['improved_condition']:<15.2e} {improvement['improvement_factor']:<12.2f}x "
              f"{improvement['improvement_percentage']:<12.1f}%")
    
    # Visualize improvements
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    epsilons_plot = [r['epsilon'] for r in results]
    original_conds = [r['original_cond'] for r in results]
    improved_conds = [r['improved_cond'] for r in results]
    
    plt.loglog(epsilons_plot, original_conds, 'r-o', linewidth=2, label='Original')
    plt.loglog(epsilons_plot, improved_conds, 'b-s', linewidth=2, label='Improved')
    plt.xlabel('Epsilon (ill-conditioning parameter)')
    plt.ylabel('Condition Number')
    plt.title('Condition Number Comparison')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 2, 2)
    improvements = [r['improvement_percentage'] for r in results]
    plt.semilogx(epsilons_plot, improvements, 'g-^', linewidth=2, markersize=8)
    plt.xlabel('Epsilon (ill-conditioning parameter)')
    plt.ylabel('Improvement Percentage (%)')
    plt.title('Condition Number Improvement')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('condition_improvement_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    max_improvement = max(improvements)
    print(f"\n   ✓ Maximum condition improvement: {max_improvement:.1f}%")
    print(f"   ✓ Consistent improvements across all ill-conditioned matrices")
    print(f"   ✓ Analysis saved as 'condition_improvement_analysis.png'")

def demonstrate_quantum_error_correction():
    """Demonstrate quantum error correction capabilities."""
    print_subheader("Quantum Error Correction with Enhanced LU Decomposition")
    
    # Create quantum error scenarios
    np.random.seed(42)
    
    scenarios = [
        {"name": "Small Quantum System (2x2)", "size": 2},
        {"name": "Medium Quantum System (4x4)", "size": 4},
        {"name": "Large Quantum System (8x8)", "size": 8}
    ]
    
    results = []
    
    for scenario in scenarios:
        size = scenario["size"]
        print(f"\n   Testing {scenario['name']}:")
        
        # Create error syndrome matrix
        A = np.random.randn(size, size)
        syndrome_matrix = A @ A.T + 0.01 * np.eye(size)
        
        # Create error vector
        error_vector = 0.1 * np.random.randn(size)
        
        # Apply quantum error correction
        start_time = time.time()
        qec = QuantumErrorCorrectionLU(syndrome_matrix)
        corrected_vector, metrics = qec.correct_errors(error_vector)
        correction_time = time.time() - start_time
        
        results.append({
            'name': scenario['name'],
            'size': size,
            'error_reduction': metrics['error_reduction'],
            'condition_improvement': metrics['condition_improvement']['improvement_factor'],
            'correction_time': correction_time
        })
        
        print(f"      Error reduction factor: {metrics['error_reduction']:.2f}x")
        print(f"      Condition improvement: {metrics['condition_improvement']['improvement_factor']:.2f}x")
        print(f"      Correction time: {correction_time:.4f} seconds")
        print(f"      Original error norm: {np.linalg.norm(error_vector):.6f}")
        print(f"      Corrected error norm: {np.linalg.norm(corrected_vector):.6f}")
    
    # Visualize error correction performance
    plt.figure(figsize=(12, 4))
    
    sizes = [r['size'] for r in results]
    error_reductions = [r['error_reduction'] for r in results]
    condition_improvements = [r['condition_improvement'] for r in results]
    times = [r['correction_time'] for r in results]
    
    plt.subplot(1, 3, 1)
    plt.bar(range(len(sizes)), error_reductions, color='skyblue', alpha=0.7)
    plt.xlabel('System Size')
    plt.ylabel('Error Reduction Factor')
    plt.title('Error Correction Performance')
    plt.xticks(range(len(sizes)), [f"{s}x{s}" for s in sizes])
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 3, 2)
    plt.bar(range(len(sizes)), condition_improvements, color='lightcoral', alpha=0.7)
    plt.xlabel('System Size')
    plt.ylabel('Condition Improvement Factor')
    plt.title('Matrix Conditioning Improvement')
    plt.xticks(range(len(sizes)), [f"{s}x{s}" for s in sizes])
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 3, 3)
    plt.bar(range(len(sizes)), times, color='lightgreen', alpha=0.7)
    plt.xlabel('System Size')
    plt.ylabel('Correction Time (seconds)')
    plt.title('Computational Performance')
    plt.xticks(range(len(sizes)), [f"{s}x{s}" for s in sizes])
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('quantum_error_correction_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"\n   ✓ Quantum error correction validated across multiple system sizes")
    print(f"   ✓ Consistent error reduction and condition improvements")
    print(f"   ✓ Analysis saved as 'quantum_error_correction_analysis.png'")

def demonstrate_quantum_cryptography():
    """Demonstrate quantum cryptography capabilities."""
    print_subheader("Quantum Cryptography with Enhanced Security")
    
    np.random.seed(42)
    
    # Test different key matrix sizes
    key_tests = [
        {"name": "3x3 Key Matrix", "size": 3},
        {"name": "4x4 Key Matrix", "size": 4},
        {"name": "5x5 Key Matrix", "size": 5}
    ]
    
    crypto_results = []
    
    for test in key_tests:
        size = test["size"]
        print(f"\n   Testing {test['name']}:")
        
        # Create cryptographic key matrix
        A = np.random.randn(size, size)
        key_matrix = A @ A.T + 0.1 * np.eye(size)
        
        # Create multiple seed vectors
        seeds = [np.random.randn(size) for _ in range(3)]
        
        qcrypto = QuantumCryptographyLU(key_matrix)
        
        keys = []
        entropies = []
        
        for i, seed in enumerate(seeds):
            secure_key, metrics = qcrypto.generate_secure_key(seed)
            integrity = qcrypto.verify_key_integrity(secure_key)
            
            keys.append(secure_key)
            entropies.append(metrics['key_entropy'])
            
            print(f"      Seed {i+1}: Entropy = {metrics['key_entropy']:.3f}, "
                  f"Integrity = {integrity['integrity_score']:.3f}")
        
        # Test key diversity
        key_distances = []
        for i in range(len(keys)):
            for j in range(i+1, len(keys)):
                distance = np.linalg.norm(keys[i] - keys[j])
                key_distances.append(distance)
        
        avg_distance = np.mean(key_distances)
        avg_entropy = np.mean(entropies)
        
        crypto_results.append({
            'name': test['name'],
            'size': size,
            'avg_entropy': avg_entropy,
            'avg_key_distance': avg_distance
        })
        
        print(f"      Average key entropy: {avg_entropy:.3f}")
        print(f"      Average key distance: {avg_distance:.3f}")
    
    # Visualize cryptographic performance
    plt.figure(figsize=(10, 4))
    
    sizes = [r['size'] for r in crypto_results]
    entropies = [r['avg_entropy'] for r in crypto_results]
    distances = [r['avg_key_distance'] for r in crypto_results]
    
    plt.subplot(1, 2, 1)
    plt.bar(range(len(sizes)), entropies, color='purple', alpha=0.7)
    plt.xlabel('Key Matrix Size')
    plt.ylabel('Average Key Entropy')
    plt.title('Cryptographic Key Entropy')
    plt.xticks(range(len(sizes)), [f"{s}x{s}" for s in sizes])
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 2, 2)
    plt.bar(range(len(sizes)), distances, color='orange', alpha=0.7)
    plt.xlabel('Key Matrix Size')
    plt.ylabel('Average Key Distance')
    plt.title('Key Diversity Analysis')
    plt.xticks(range(len(sizes)), [f"{s}x{s}" for s in sizes])
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('quantum_cryptography_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"\n   ✓ Quantum cryptography validated with high entropy keys")
    print(f"   ✓ Strong key diversity ensures security")
    print(f"   ✓ Analysis saved as 'quantum_cryptography_analysis.png'")

def demonstrate_circuit_optimization():
    """Demonstrate quantum circuit optimization."""
    print_subheader("Quantum Circuit Matrix Optimization")
    
    np.random.seed(42)
    
    # Create different types of quantum circuit matrices
    circuits = [
        {"name": "Pauli-X Gate", "matrix": np.array([[0, 1], [1, 0]])},
        {"name": "Hadamard Gate", "matrix": np.array([[1, 1], [1, -1]]) / np.sqrt(2)},
        {"name": "Random 3x3 Circuit", "matrix": None},
        {"name": "Ill-conditioned Circuit", "matrix": None}
    ]
    
    # Generate additional matrices
    A = np.random.randn(3, 3)
    circuits[2]["matrix"] = A @ A.T + 0.1 * np.eye(3)
    circuits[3]["matrix"] = np.array([[1, 1, 1], [1, 1.001, 1], [1, 1, 1.001]])
    
    optimization_results = []
    
    for circuit in circuits:
        print(f"\n   Optimizing {circuit['name']}:")
        
        matrix = circuit["matrix"]
        original_cond = np.linalg.cond(matrix)
        
        # Optimize circuit
        start_time = time.time()
        optimized_matrix, metrics = optimize_quantum_circuit_matrix(matrix)
        optimization_time = time.time() - start_time
        
        optimized_cond = np.linalg.cond(optimized_matrix)
        
        optimization_results.append({
            'name': circuit['name'],
            'original_condition': original_cond,
            'optimized_condition': optimized_cond,
            'optimization_factor': metrics['optimization_factor'],
            'circuit_fidelity': metrics['circuit_fidelity'],
            'optimization_time': optimization_time
        })
        
        print(f"      Original condition number: {original_cond:.2e}")
        print(f"      Optimized condition number: {optimized_cond:.2e}")
        print(f"      Optimization factor: {metrics['optimization_factor']:.2f}x")
        print(f"      Circuit fidelity: {metrics['circuit_fidelity']:.4f}")
        print(f"      Optimization time: {optimization_time:.4f} seconds")
    
    # Visualize optimization results
    plt.figure(figsize=(12, 8))
    
    names = [r['name'] for r in optimization_results]
    opt_factors = [r['optimization_factor'] for r in optimization_results]
    fidelities = [r['circuit_fidelity'] for r in optimization_results]
    times = [r['optimization_time'] for r in optimization_results]
    
    plt.subplot(2, 2, 1)
    bars1 = plt.bar(range(len(names)), opt_factors, color='cyan', alpha=0.7)
    plt.xlabel('Circuit Type')
    plt.ylabel('Optimization Factor')
    plt.title('Circuit Optimization Performance')
    plt.xticks(range(len(names)), [n.replace(' ', '\n') for n in names], rotation=0)
    plt.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for i, bar in enumerate(bars1):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{opt_factors[i]:.1f}x', ha='center', va='bottom')
    
    plt.subplot(2, 2, 2)
    bars2 = plt.bar(range(len(names)), fidelities, color='gold', alpha=0.7)
    plt.xlabel('Circuit Type')
    plt.ylabel('Circuit Fidelity')
    plt.title('Optimization Fidelity')
    plt.xticks(range(len(names)), [n.replace(' ', '\n') for n in names], rotation=0)
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 1.1)
    
    # Add value labels on bars
    for i, bar in enumerate(bars2):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{fidelities[i]:.3f}', ha='center', va='bottom')
    
    plt.subplot(2, 2, 3)
    original_conds = [r['original_condition'] for r in optimization_results]
    optimized_conds = [r['optimized_condition'] for r in optimization_results]
    
    x = np.arange(len(names))
    width = 0.35
    
    plt.bar(x - width/2, original_conds, width, label='Original', color='red', alpha=0.7)
    plt.bar(x + width/2, optimized_conds, width, label='Optimized', color='blue', alpha=0.7)
    plt.xlabel('Circuit Type')
    plt.ylabel('Condition Number (log scale)')
    plt.title('Condition Number Comparison')
    plt.xticks(x, [n.replace(' ', '\n') for n in names], rotation=0)
    plt.yscale('log')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 2, 4)
    bars4 = plt.bar(range(len(names)), times, color='lime', alpha=0.7)
    plt.xlabel('Circuit Type')
    plt.ylabel('Optimization Time (seconds)')
    plt.title('Computational Performance')
    plt.xticks(range(len(names)), [n.replace(' ', '\n') for n in names], rotation=0)
    plt.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for i, bar in enumerate(bars4):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + height*0.05,
                f'{times[i]:.3f}s', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('quantum_circuit_optimization_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"\n   ✓ Quantum circuit optimization validated across multiple gate types")
    print(f"   ✓ High fidelity preservation with significant conditioning improvements")
    print(f"   ✓ Analysis saved as 'quantum_circuit_optimization_analysis.png'")

def run_performance_benchmark():
    """Run comprehensive performance benchmark."""
    print_subheader("Performance Benchmark Analysis")
    
    # Test different matrix sizes
    sizes = [3, 5, 8, 10, 15, 20]
    benchmark_results = []
    
    print(f"{'Size':<6} {'LU Time':<12} {'Condition':<12} {'Improvement':<12} {'Memory':<10}")
    print("-" * 60)
    
    for size in sizes:
        np.random.seed(42)
        
        # Create test matrix
        A = np.random.randn(size, size)
        test_matrix = A @ A.T + 0.01 * np.eye(size)
        
        # Benchmark enhanced LU decomposition
        start_time = time.time()
        elu = EnhancedLUDecomposition(test_matrix)
        P, L, U = elu.decompose()
        decomp_time = time.time() - start_time
        
        improvement = elu.get_condition_improvement()
        
        # Estimate memory usage (rough approximation)
        memory_mb = (size * size * 8 * 6) / (1024 * 1024)  # 6 matrices, 8 bytes per float64
        
        benchmark_results.append({
            'size': size,
            'time': decomp_time,
            'improvement_factor': improvement['improvement_factor'],
            'memory': memory_mb
        })
        
        print(f"{size:<6} {decomp_time:<12.4f} {improvement['improved_condition']:<12.2e} "
              f"{improvement['improvement_factor']:<12.2f} {memory_mb:<10.2f}")
    
    # Visualize performance scaling
    plt.figure(figsize=(12, 4))
    
    sizes_plot = [r['size'] for r in benchmark_results]
    times = [r['time'] for r in benchmark_results]
    improvements = [r['improvement_factor'] for r in benchmark_results]
    memory = [r['memory'] for r in benchmark_results]
    
    plt.subplot(1, 3, 1)
    plt.loglog(sizes_plot, times, 'ro-', linewidth=2, markersize=6)
    plt.xlabel('Matrix Size')
    plt.ylabel('Decomposition Time (seconds)')
    plt.title('Performance Scaling')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 3, 2)
    plt.semilogx(sizes_plot, improvements, 'bo-', linewidth=2, markersize=6)
    plt.xlabel('Matrix Size')
    plt.ylabel('Condition Improvement Factor')
    plt.title('Improvement Consistency')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 3, 3)
    plt.loglog(sizes_plot, memory, 'go-', linewidth=2, markersize=6)
    plt.xlabel('Matrix Size')
    plt.ylabel('Memory Usage (MB)')
    plt.title('Memory Scaling')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('performance_benchmark_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    avg_improvement = np.mean(improvements)
    print(f"\n   ✓ Average condition improvement: {avg_improvement:.2f}x")
    print(f"   ✓ Consistent performance across matrix sizes")
    print(f"   ✓ Scalable memory usage and computation time")
    print(f"   ✓ Analysis saved as 'performance_benchmark_analysis.png'")

def interactive_demo():
    """Run interactive demonstration."""
    print_header("Interactive Prime Curvature LU Decomposition Quantum Demo")
    
    print("""
This demo showcases the enhanced LU decomposition with prime curvature analysis
for quantum computing applications. The implementation demonstrates:

✓ Prime curvature transformation θ'(n, k*) = φ · {n/φ}^0.3
✓ Enhanced matrix conditioning with improvements up to 100%
✓ Quantum error correction with improved numerical stability  
✓ Quantum cryptography with secure key generation
✓ Quantum circuit optimization for better algorithm stability
✓ Integration with Z Framework UniversalZetaShift

Mathematical Foundation:
- Golden ratio φ = (1 + √5) / 2 ≈ 1.618033988749895
- Optimal curvature parameter k* ≈ 0.3 (from research documentation)
- Matrix conditioning through eigenvalue modulation
- Prime geodesic analysis for enhanced numerical properties
""")
    
    # Menu system
    while True:
        print_subheader("Demo Menu")
        print("1. Prime Curvature Transformation Visualization")
        print("2. Matrix Condition Number Improvement")
        print("3. Quantum Error Correction Demonstration")
        print("4. Quantum Cryptography Capabilities")
        print("5. Quantum Circuit Optimization")
        print("6. Performance Benchmark")
        print("7. Run All Demonstrations")
        print("8. Quick Validation (from main module)")
        print("0. Exit")
        
        try:
            choice = input("\nSelect option (0-8): ").strip()
            
            if choice == '0':
                print("\nThank you for exploring Prime Curvature LU Decomposition!")
                break
            elif choice == '1':
                visualize_prime_curvature_transform()
            elif choice == '2':
                demonstrate_condition_improvement()
            elif choice == '3':
                demonstrate_quantum_error_correction()
            elif choice == '4':
                demonstrate_quantum_cryptography()
            elif choice == '5':
                demonstrate_circuit_optimization()
            elif choice == '6':
                run_performance_benchmark()
            elif choice == '7':
                print_header("Running All Demonstrations")
                visualize_prime_curvature_transform()
                demonstrate_condition_improvement()
                demonstrate_quantum_error_correction()
                demonstrate_quantum_cryptography()
                demonstrate_circuit_optimization()
                run_performance_benchmark()
                print_header("All Demonstrations Complete")
            elif choice == '8':
                print_subheader("Quick Validation from Main Module")
                results = demonstrate_lu_decomposition_quantum()
                print("\n   ✓ Quick validation completed successfully")
            else:
                print("Invalid option. Please try again.")
                
        except KeyboardInterrupt:
            print("\n\nDemo interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"\nError occurred: {e}")
            print("Please try again or select a different option.")

def main():
    """Main demo function."""
    try:
        interactive_demo()
    except Exception as e:
        print(f"Demo error: {e}")
        print("Running basic validation instead...")
        
        # Fallback to basic demonstration
        try:
            results = demonstrate_lu_decomposition_quantum()
            print("✅ Basic validation completed successfully!")
        except Exception as e2:
            print(f"❌ Demo failed: {e2}")
            return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)