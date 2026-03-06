#!/usr/bin/env python3
"""
Extended Arctan Geodesic Primes Demo with Conical Flow Integration
==================================================================

This script extends the Arctan Geodesic Primes approach by integrating it with
conical flow models and biological applications.

Features:
- Arctan Geodesic Primes with conical flow enhancement
- 15-30% error reduction simulation
- Molecular geodesic analysis with rdkit
- Biological sequence alignment integration with BioPython

Author: Unified Framework Team
Date: November 2025
"""

import sys
import os
import random
from typing import List, Tuple, Dict, Any
import math

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import mpmath as mp
    mp.mp.dps = 50
    HAS_MPMATH = True
except ImportError:
    HAS_MPMATH = False
    mp = None

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import sympy
    HAS_SYMPY = True
except ImportError:
    HAS_SYMPY = False

# Try to import biological libraries
try:
    import Bio
    from Bio import SeqIO, AlignIO
    from Bio.Seq import Seq
    from Bio.Align import MultipleSeqAlignment
    HAS_BIOPYTHON = True
except ImportError:
    HAS_BIOPYTHON = False

try:
    import rdkit
    from rdkit import Chem
    from rdkit.Chem import AllChem
    HAS_RDKIT = True
except ImportError:
    HAS_RDKIT = False

# Import Z5D functions
try:
    from core.conical_flow import conical_density_enhancement_factor
    from core.z_5d_enhanced import z5d_predictor_with_dist_level
except ImportError:
    print("Warning: Could not import Z5D functions")

# Arctan Geodesic Primes implementation
class ArctanGeodesicPrimes:
    """Arctan Geodesic Primes with conical flow integration."""

    def __init__(self, kappa_geo: float = 0.3):
        self.phi = (1 + math.sqrt(5)) / 2  # Golden ratio
        self.kappa_geo = kappa_geo

    def theta_prime(self, n: int) -> float:
        """Compute θ'(n,k) geodesic mapping."""
        y = n / self.phi
        frac = y - math.floor(y)
        return self.phi * (frac ** self.kappa_geo)

    def arctan_identity_check(self) -> Dict[str, Any]:
        """Verify arctan identities for robustness."""
        if not HAS_MPMATH:
            return {"error": "mpmath not available"}

        # Identity: arctan(x) + arctan(1/x) = π/2 for x > 0
        x = mp.mpf('2.5')
        lhs = mp.atan(x) + mp.atan(1/x)
        rhs = mp.pi / 2
        identity1_error = abs(lhs - rhs)

        # Double angle: arctan(x) = 2*arctan(x/(1+sqrt(1+x^2)))
        x = mp.mpf('1.5')
        lhs = mp.atan(x)
        rhs = 2 * mp.atan(x / (1 + mp.sqrt(1 + x**2)))
        identity2_error = abs(lhs - rhs)

        return {
            "identity1_error": float(identity1_error),
            "identity2_error": float(identity2_error),
            "total_error": float(identity1_error + identity2_error)
        }

    def conical_enhanced_theta_prime(self, n: int, dist_level: float = 0.525) -> float:
        """θ'(n,k) with conical flow enhancement."""
        base_theta = self.theta_prime(n)

        if HAS_MPMATH:
            try:
                enhancement = conical_density_enhancement_factor(n, dist_level=dist_level)
                return base_theta * float(enhancement)
            except:
                pass

        return base_theta

    def simulate_error_reduction(self, n_samples: int = 1000, n_max: int = 100000) -> Dict[str, Any]:
        """Simulate 15-30% error reduction with conical flow integration."""
        if not HAS_SYMPY:
            return {"error": "sympy not available for prime generation"}

        # Generate primes
        primes = list(sympy.primerange(2, n_max))
        n_primes = len(primes)

        if n_primes < n_samples:
            n_samples = n_primes

        # Sample primes
        sampled_primes = random.sample(primes, n_samples)

        # Compute predictions with and without conical enhancement
        errors_standard = []
        errors_enhanced = []

        for p in sampled_primes:
            # Find prime index (approximate)
            idx = sum(1 for q in primes if q <= p)

            # Standard Z5D prediction
            try:
                pred_standard = z5d_predictor_with_dist_level(idx)
                error_standard = abs(float(pred_standard) - p) / p * 100
                errors_standard.append(error_standard)
            except:
                continue

            # Enhanced prediction (simulate conical flow integration)
            try:
                # Use conical enhancement to adjust the prediction
                enhancement = conical_density_enhancement_factor(idx)
                pred_enhanced = float(pred_standard) * float(enhancement)
                error_enhanced = abs(pred_enhanced - p) / p * 100
                errors_enhanced.append(error_enhanced)
            except:
                continue

        if not errors_standard or not errors_enhanced:
            return {"error": "Could not compute predictions"}

        mean_error_standard = sum(errors_standard) / len(errors_standard)
        mean_error_enhanced = sum(errors_enhanced) / len(errors_enhanced)
        error_reduction = (mean_error_standard - mean_error_enhanced) / mean_error_standard * 100

        return {
            "n_samples": len(errors_standard),
            "mean_error_standard": mean_error_standard,
            "mean_error_enhanced": mean_error_enhanced,
            "error_reduction_percent": error_reduction,
            "target_achieved": 15 <= error_reduction <= 30
        }

class MolecularGeodesics:
    """Molecular geodesic analysis using rdkit."""

    def __init__(self):
        if not HAS_RDKIT:
            raise ImportError("rdkit not available")

    def molecule_to_geodesic(self, smiles: str) -> Dict[str, Any]:
        """Convert molecular structure to geodesic representation."""
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return {"error": "Invalid SMILES"}

        # Get molecular properties
        n_atoms = mol.GetNumAtoms()
        n_bonds = mol.GetNumBonds()
        mol_wt = Chem.Descriptors.ExactMolWt(mol)

        # Compute "geodesic" properties using molecular structure
        # This is a simplified analogy - real implementation would use more sophisticated geometry
        geodesic_features = {
            "n_atoms": n_atoms,
            "n_bonds": n_bonds,
            "molecular_weight": mol_wt,
            "density": n_bonds / n_atoms if n_atoms > 0 else 0,
            "complexity_score": n_atoms * math.log(n_bonds + 1) if n_bonds > 0 else 0
        }

        return geodesic_features

    def analyze_drug_like_molecules(self) -> Dict[str, Any]:
        """Analyze common drug-like molecules using geodesic principles."""
        drug_smiles = {
            "aspirin": "CC(=O)OC1=CC=CC=C1C(=O)O",
            "caffeine": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
            "ibuprofen": "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",
            "paracetamol": "CC(=O)NC1=CC=C(O)C=C1"
        }

        results = {}
        for name, smiles in drug_smiles.items():
            results[name] = self.molecule_to_geodesic(smiles)

        return results

class BiologicalSequenceGeodesics:
    """Biological sequence analysis using geodesic principles."""

    def __init__(self):
        if not HAS_BIOPYTHON:
            raise ImportError("BioPython not available")

    def sequence_to_geodesic(self, sequence: str, seq_type: str = "dna") -> Dict[str, Any]:
        """Convert biological sequence to geodesic representation."""
        if seq_type.lower() == "dna":
            seq = Seq(sequence)
        else:
            seq = sequence  # Assume protein

        seq_len = len(seq)

        # Compute "geodesic" features based on sequence properties
        # This is a simplified analogy
        gc_content = (sequence.count('G') + sequence.count('C')) / seq_len if seq_len > 0 else 0

        # Use sequence position as "coordinate"
        geodesic_coords = []
        for i, base in enumerate(sequence):
            # Simple mapping: A=0, C=1, G=2, T=3
            coord = {"A": 0, "C": 1, "G": 2, "T": 3}.get(base.upper(), 0)
            geodesic_coords.append(coord)

        # Compute "curvature" as variance in coordinates
        if HAS_NUMPY:
            curvature = np.var(geodesic_coords)
        else:
            mean_coord = sum(geodesic_coords) / len(geodesic_coords)
            curvature = sum((x - mean_coord)**2 for x in geodesic_coords) / len(geodesic_coords)

        return {
            "length": seq_len,
            "gc_content": gc_content,
            "curvature": curvature,
            "complexity": seq_len * math.log(len(set(sequence)) + 1)
        }

    def analyze_sample_sequences(self) -> Dict[str, Any]:
        """Analyze sample biological sequences."""
        sequences = {
            "human_insulin_gene": "ATGGCCCTGTGGATGCGCCTCCTGCCCCTGCTGGCGCTGCTGGCCCTCTGGGGACCTGACCCAGCCGCAGCCTTTGTGAACCAACACCTGTGCGGCTCACACCTGGTGGAAGCTCTCTACCTAGTGTGCGGGGAACGAGGCTTCTTCTACACACCCAAGACCCGCCGGGAGGCAGAGGACCTGCAGGTGGGGCAGGTGGAGCTGGGCGGGGGCCCTGGTGCAGGCAGCCTGCAGCCCTTGGCCCTGGAGGGGTCCCTGCAGAAGCGTGGCATTGTGGAACAATGCTGTACCAGCATCTGCTCCCTCTACCAGCTGGAGAACTACTGCAACTA",
            "e_coli_promoter": "TTGACA",
            "fibonacci_dna": "ATCGATCGATCG"  # Artificial sequence
        }

        results = {}
        for name, seq in sequences.items():
            results[name] = self.sequence_to_geodesic(seq, "dna")

        return results

def main():
    """Main demonstration."""
    print("=" * 70)
    print("Extended Arctan Geodesic Primes Demo")
    print("=" * 70)

    # Initialize Arctan Geodesic Primes
    agp = ArctanGeodesicPrimes()

    # 1. Verify arctan identities
    print("\n1. Arctan Identity Verification")
    print("-" * 30)
    identities = agp.arctan_identity_check()
    if "error" not in identities:
        print(".2e")
        print(".2e")
        print(".2e")
    else:
        print(f"Error: {identities['error']}")

    # 2. Error reduction simulation
    print("\n2. Error Reduction Simulation (15-30% target)")
    print("-" * 40)
    error_sim = agp.simulate_error_reduction(n_samples=100, n_max=50000)
    if "error" not in error_sim:
        print(".2f")
        print(".2f")
        print(".1f")
        print(f"Target achieved: {'✓' if error_sim['target_achieved'] else '✗'}")
    else:
        print(f"Error: {error_sim['error']}")

    # 3. Molecular geodesics (if rdkit available)
    if HAS_RDKIT:
        print("\n3. Molecular Geodesic Analysis")
        print("-" * 30)
        try:
            mol_geo = MolecularGeodesics()
            drug_analysis = mol_geo.analyze_drug_like_molecules()
            for drug, features in drug_analysis.items():
                print(f"{drug.capitalize()}: atoms={features['n_atoms']}, bonds={features['n_bonds']}, complexity={features['complexity_score']:.2f}")
        except Exception as e:
            print(f"Molecular analysis failed: {e}")
    else:
        print("\n3. Molecular Geodesic Analysis (rdkit not available)")
        print("-" * 50)

    # 4. Biological sequence geodesics (if BioPython available)
    if HAS_BIOPYTHON:
        print("\n4. Biological Sequence Geodesic Analysis")
        print("-" * 40)
        try:
            bio_geo = BiologicalSequenceGeodesics()
            seq_analysis = bio_geo.analyze_sample_sequences()
            for seq_name, features in seq_analysis.items():
                print(f"{seq_name}: len={features['length']}, GC={features['gc_content']:.2f}, curvature={features['curvature']:.2f}")
        except Exception as e:
            print(f"Biological analysis failed: {e}")
    else:
        print("\n4. Biological Sequence Geodesic Analysis (BioPython not available)")
        print("-" * 55)

    print("\n" + "=" * 70)
    print("Demo completed. Arctan Geodesic Primes integrated with conical flow.")
    print("=" * 70)

if __name__ == '__main__':
    main()