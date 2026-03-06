"""
Codon Mutation Rate Falsification Experiment

This experiment attempts to falsify the hypothesis that Stadlmann's θ ≈ 0.525
bounds mutation rates in codon distributions with correlation r ≥ 0.90.

The hypothesis claims that the distribution level parameter θ, derived from
Stadlmann's 2023 work on prime number distributions in arithmetic progressions,
can predict or bound mutation rates in biological codon sequences.

Methodology:
1. Obtain real biological sequence data using BioPython
2. Calculate codon usage frequencies and mutation rates
3. Compute correlation between θ-dependent metrics and observed mutation rates
4. Perform bootstrap confidence interval analysis (1,000 resamples)
5. Test if correlation r ≥ 0.90 as claimed

Author: Falsification Experiment
Date: 2025-11-23
Seed: 42 (for reproducibility)
"""

import numpy as np
from Bio import SeqIO, Entrez
from Bio.Seq import Seq
from scipy.stats import pearsonr, spearmanr
import json
import warnings
from collections import Counter, defaultdict
from datetime import datetime

# Set random seed for reproducibility
SEED = 42
np.random.seed(SEED)

# Stadlmann's distribution level parameter from the Z Framework
THETA_STADLMANN = 0.525

# Epsilon for numerical stability in logarithmic calculations
EPSILON = 1e-10

# Email for NCBI Entrez (required)
Entrez.email = "experiment@falsification.test"

# Result verdict strings
VERDICT_FALSIFIED = "FALSIFIED (below threshold)"
VERDICT_NOT_FALSIFIED = "CANNOT FALSIFY (meets threshold)"


class CodonMutationAnalysis:
    """Analyzes codon mutation rates and tests correlation with Stadlmann's θ."""
    
    def __init__(self, seed=42):
        """
        Initialize the analysis.
        
        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        np.random.seed(seed)
        self.results = {}
        
        # Standard genetic code
        self.genetic_code = {
            'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
            'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
            'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*',
            'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W',
            'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
            'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
            'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
            'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
            'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
            'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
            'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
            'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
            'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
            'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
            'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
            'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G',
        }
        
        # Synonymous codon groups (codons that code for the same amino acid)
        self.synonymous_groups = self._build_synonymous_groups()
        
    def _build_synonymous_groups(self):
        """Build groups of synonymous codons."""
        groups = defaultdict(list)
        for codon, aa in self.genetic_code.items():
            if aa != '*':  # Exclude stop codons
                groups[aa].append(codon)
        return dict(groups)
    
    def get_sample_sequences(self):
        """
        Get sample DNA sequences for analysis.
        
        For this falsification experiment, we'll use a hardcoded set of
        sequences based on real E. coli gene sequences to avoid network
        dependencies and ensure reproducibility.
        
        Returns:
            List of DNA sequences as strings
        """
        # These are simplified representations of real E. coli genes
        # In a full experiment, these would be fetched from NCBI
        sequences = [
            # lacZ gene excerpt (β-galactosidase)
            "ATGACCATGATTACGGATTCACTGGCCGTCGTTTTACAACGTCGTGACTGGGAAAACCCTGGCGTTACCCAACTTAATCGCCTTGCAGCACATCCCCCTTTCGCCAGCTGGCGTAATAGCGAAGAGGCCCGCACCGATCGCCCTTCCCAACAGTTGCGCAGCCTGAATGGCGAATGGCGCCTGATGCGGTATTTTCTCCTTACGCATCTGTGCGGTATTTCACACCGCATATGGTGCACTCTCAGTACAATCTGCTCTGATGCCGCATAGTTAAGCCAGCCCCGACACCCGCCAACACCCGCTGACGCGCCCTGACGGGCTTGTCTGCTCCCGGCATCCGCTTACAGACAAGCTGTGACCGTCTCCGGGAGCTGCATGTGTCAGAGGTTTTCACCGTCATCACCGAAACGCGCGAGACGAAAGGGCCTCGTGATACGCCTATTTTTATAGGTTAATGTCATGATAATAATGGTTTCTTAGACGTCAGGTGGCACTTTTCGGGGAAATGTGCGCGGAACCCCTATTTGTTTATTTTTCTAAATACATTCAAATATGTATCCGCTCATGAGACAATAACCCTGATAAATGCTTCAATAATATTGAAAAAGGAAGAGTATGAGTATTCAACATTTCCGTGTCGCCCTTATTCCCTTTTTTGCGGCATTTTGCCTTCCTGTTTTTGCTCACCCAGAAACGCTGGTGAAAGTAAAAGATGCTGAAGATCAGTTGGGTGCACGAGTGGGTTACATCGAACTGGATCTCAACAGCGGTAAGATCCTTGAGAGTTTTCGCCCCGAAGAACGTTTTCCAATGATGAGCACTTTTAAAGTTCTGCTATGTGGCGCGGTATTATCCCGTATTGACGCCGGGCAAGAGCAACTCGGTCGCCGCATACACTATTCTCAGAATGACTTGGTTGAGTACTCACCAGTCACAGAAAAGCATCTTACGGATGGCATGACAGTAAGAGAATTATGCAGTGCTGCCATAACCATGAGTGATAACACTGCGGCCAACTTACTTCTGACAACGATCGGAGGACCGAAGGAGCTAACCGCTTTTTTGCACAACATGGGGGATCATGTAACTCGCCTTGATCGTTGGGAACCGGAGCTGAATGAAGCCATACCAAACGACGAGCGTGACACCACGATGCCTGTAGCAATGGCAACAACGTTGCGCAAACTATTAACTGGCGAACTACTTACTCTAGCTTCCCGGCAACAATTAATAGACTGGATGGAGGCGGATAAAGTTGCAGGACCACTTCTGCGCTCGGCCCTTCCGGCTGGCTGGTTTATTGCTGATAAATCTGGAGCCGGTGAGCGTGGGTCTCGCGGTATCATTGCAGCACTGGGGCCAGATGGTAAGCCCTCCCGTATCGTAGTTATCTACACGACGGGGAGTCAGGCAACTATGGATGAACGAAATAGACAGATCGCTGAGATAGGTGCCTCACTGATTAAGCATTGGTAACTGTCAGACCAAGTTTACTCATATATACTTTAGATTGATTTAAAACTTCATTTTTAATTTAAAAGGATCTAGGTGAAGATCCTTTTTGATAATCTCATGACCAAAATCCCTTAACGTGAGTTTTCGTTCCACTGAGCGTCAGACCCCGTAGAAAAGATCAAAGGATCTTCTTGAGATCCTTTTTTTCTGCGCGTAATCTGCTGCTTGCAAACAAAAAAACCACCGCTACCAGCGGTGGTTTGTTTGCCGGATCAAGAGCTACCAACTCTTTTTCCGAAGGTAACTGGCTTCAGCAGAGCGCAGATACCAAATACTGTCCTTCTAGTGTAGCCGTAGTTAGGCCACCACTTCAAGAACTCTGTAGCACCGCCTACATACCTCGCTCTGCTAATCCTGTTACCAGTGGCTGCTGCCAGTGGCGATAAGTCGTGTCTTACCGGGTTGGACTCAAGACGATAGTTACCGGATAAGGCGCAGCGGTCGGGCTGAACGGGGGGTTCGTGCACACAGCCCAGCTTGGAGCGAACGACCTACACCGAACTGAGATACCTACAGCGTGAGCTATGAGAAAGCGCCACGCTTCCCGAAGGGAGAAAGGCGGACAGGTATCCGGTAAGCGGCAGGGTCGGAACAGGAGAGCGCACGAGGGAGCTTCCAGGGGGAAACGCCTGGTATCTTTATAGTCCTGTCGGGTTTCGCCACCTCTGACTTGAGCGTCGATTTTTGTGATGCTCGTCAGGGGGGCGGAGCCTATGGAAAAACGCCAGCAACGCGGCCTTTTTACGGTTCCTGGCCTTTTGCTGGCCTTTTGCTCACATGTTCTTTCCTGCGTTATCCCCTGATTCTGTGGATAACCGTATTACCGCCTTTGAGTGAGCTGATACCGCTCGCCGCAGCCGAACGACCGAGCGCAGCGAGTCAGTGAGCGAGGAAGCGGAAGAGCGCCCAATACGCAAACCGCCTCTCCCCGCGCGTTGGCCGATTCATTAATGCAGCTGGCACGACAGGTTTCCCGACTGGAAAGCGGGCAGTGAGCGCAACGCAATTAATGTGAGTTAGCTCACTCATTAGGCACCCCAGGCTTTACACTTTATGCTTCCGGCTCGTATGTTGTGTGGAATTGTGAGCGGATAACAATTTCACACAGGAAACAGCTATGACCATGATTACGCCAAGCTTGCATGCCTGCAGGTCGACTCTAGAGGATCCCCGGGTACCGAGCTCGAATTCGTAATCATGGTCATAGCTGTTTCCTGTGTGAAATTGTTATCCGCTCACAATTCCACACAACATACGAGCCGGAAGCATAAAGTGTAAAGCCTGGGGTGCCTAATGAGTGAGCTAACTCACATTAATTGCGTTGCGCTCACTGCCCGCTTTCCAGTCGGGAAACCTGTCGTGCCAGCTGCATTAATGAATCGGCCAACGCGCGGGGAGAGGCGGTTTGCGTATTGGGCGCTCTTCCGCTTCCTCGCTCACTGACTCGCTGCGCTCGGTCGTTCGGCTGCGGCGAGCGGTATCAGCTCACTCAAAGGCGGTAATACGGTTATCCACAGAATCAGGGGATAACGCAGGAAAGAACATGTGAGCAAAAGGCCAGCAAAAGGCCAGGAACCGTAAAAAGGCCGCGTTGCTGGCGTTTTTCCATAGGCTCCGCCCCCCTGACGAGCATCACAAAAATCGACGCTCAAGTCAGAGGTGGCGAAACCCGACAGGACTATAAAGATACCAGGCGTTTCCCCCTGGAAGCTCCCTCGTGCGCTCTCCTGTTCCGACCCTGCCGCTTACCGGATACCTGTCCGCCTTTCTCCCTTCGGGAAGCGTGGCGCTTTCTCATAGCTCACGCTGTAGGTATCTCAGTTCGGTGTAGGTCGTTCGCTCCAAGCTGGGCTGTGTGCACGAACCCCCCGTTCAGCCCGACCGCTGCGCCTTATCCGGTAACTATCGTCTTGAGTCCAACCCGGTAAGACACGACTTATCGCCACTGGCAGCAGCCACTGGTAACAGGATTAGCAGAGCGAGGTATGTAGGCGGTGCTACAGAGTTCTTGAAGTGGTGGCCTAACTACGGCTACACTAGAAGGACAGTATTTGGTATCTGCGCTCTGCTGAAGCCAGTTACCTTCGGAAAAAGAGTTGGTAGCTCTTGATCCGGCAAACAAACCACCGCTGGTAGCGGTGGTTTTTTTGTTTGCAAGCAGCAGATTACGCGCAGAAAAAAAGGATCTCAAGAAGATCCTTTGATCTTTTCTACGGGGTCTGACGCTCAGTGGAACGAAAACTCACGTTAAGGGATTTTGGTCATGAGATTATCAAAAAGGATCTTCACCTAGATCCTTTTAAATTAAAAATGAAGTTTTAAATCAATCTAAAGTATATATGAGTAAACTTGGTCTGACAGTTACCAATGCTTAATCAGTGAGGCACCTATCTCAGCGATCTGTCTATTTCGTTCATCCATAGTTGCCTGACTCCCCGTCGTGTAGATAACTACGATACGGGAGGGCTTACCATCTGGCCCCAGTGCTGCAATGATACCGCGAGACCCACGCTCACCGGCTCCAGATTTATCAGCAATAAACCAGCCAGCCGGAAGGGCCGAGCGCAGAAGTGGTCCTGCAACTTTATCCGCCTCCATCCAGTCTATTAATTGTTGCCGGGAAGCTAGAGTAAGTAGTTCGCCAGTTAATAGTTTGCGCAACGTTGTTGCCATTGCTACAGGCATCGTGGTGTCACGCTCGTCGTTTGGTATGGCTTCATTCAGCTCCGGTTCCCAACGATCAAGGCGAGTTACATGATCCCCCATGTTGTGCAAAAAAGCGGTTAGCTCCTTCGGTCCTCCGATCGTTGTCAGAAGTAAGTTGGCCGCAGTGTTATCACTCATGGTTATGGCAGCACTGCATAATTCTCTTACTGTCATGCCATCCGTAAGATGCTTTTCTGTGACTGGTGAGTACTCAACCAAGTCATTCTGAGAATAGTGTATGCGGCGACCGAGTTGCTCTTGCCCGGCGTCAATACGGGATAATACCGCGCCACATAGCAGAACTTTAAAAGTGCTCATCATTGGAAAACGTTCTTCGGGGCGAAAACTCTCAAGGATCTTACCGCTGTTGAGATCCAGTTCGATGTAACCCACTCGTGCACCCAACTGATCTTCAGCATCTTTTACTTTCACCAGCGTTTCTGGGTGAGCAAAAACAGGAAGGCAAAATGCCGCAAAAAAGGGAATAAGGGCGACACGGAAATGTTGAATACTCATACTCTTCCTTTTTCAATATTATTGAAGCATTTATCAGGGTTATTGTCTCATGAGCGGATACATATTTGAATGTATTTAGAAAAATAAACAAATAGGGGTTCCGCGCACATTTCCCCGAAAAGTGCCACCTGACGTCTAAGAAACCATTATTATCATGACATTAACCTATAAAAATAGGCGTATCACGAGGCCCTTTCGTCTCGCGCGTTTCGGTGATGACGGTGAAAACCTCTGACACATGCAGCTCCCGGAGACGGTCACAGCTTGTCTGTAAGCGGATGCCGGGAGCAGACAAGCCCGTCAGGGCGCGTCAGCGGGTGTTGGCGGGTGTCGGGGCTGGCTTAACTATGCGGCATCAGAGCAGATTGTACTGAGAGTGCACCATATGCGGTGTGAAATACCGCACAGATGCGTAAGGAGAAAATACCGCATCAGGCGCCATTCGCCATTCAGGCTGCGCAACTGTTGGGAAGGGCGATCGGTGCGGGCCTCTTCGCTATTACGCCAGCTGGCGAAAGGGGGATGTGCTGCAAGGCGATTAAGTTGGGTAACGCCAGGGTTTTCCCAGTCACGACGTTGTAAAACGACGGCCAGTGAATCCGTAATCATGGTCATAGCTGTTTCCTGTGTGAAATTGTTATCCGCTCACAATTCCACACAACATACGAGCCGGAAGCATAAAGTGTAAAGCCTGGGGTGCCTAATGAGTGAGCTAACTCACATTAATTGCGTTGCGCTCACTGCCCGCTTTCCAGTCGGGAAACCTGTCGTGCCAGCTGCATTAATGAATCGGCCAACGCGCGGGGAGAGGCGGTTTGCGTATTGGGCGCTCTTCCGCTTCCTCGCTCACTGACTCGCTGCGCTCGGTCGTTCGGCTGCGGCGAGCGGTATCAGCTCACTCAAAGGCGGTAATACGGTTATCCACAGAATCAGGGGATAACGCAGGAAAGAACATGTGAGCAAAAGGCCAGCAAAAGGCCAGGAACCGTAAAAAGGCCGCGTTGCTGGCGTTTTTCCATAGGCTCCGCCCCCCTGACGAGCATCACAAAAATCGACGCTCAAGTCAGAGGTGGCGAAACCCGACAGGACTATAAAGATACCAGGCGTTTCCCCCTGGAAGCTCCCTCGTGCGCTCTCCTGTTCCGACCCTGCCGCTTACCGGATACCTGTCCGCCTTTCTCCCTTCGGGAAGCGTGGCGCTTTCTCATAGCTCACGCTGTAGGTATCTCAGTTCGGTGTAGGTCGTTCGCTCCAAGCTGGGCTGTGTGCACGAACCCCCCGTTCAGCCCGACCGCTGCGCCTTATCCGGTAACTATCGTCTTGAGTCCAACCCGGTAAGACACGACTTATCGCCACTGGCAGCAGCCACTGGTAACAGGATTAGCAGAGCGAGGTATGTAGGCGGTGCTACAGAGTTCTTGAAGTGGTGGCCTAACTACGGCTACACTAGAAGGACAGTATTTGGTATCTGCGCTCTGCTGAAGCCAGTTACCTTCGGAAAAAGAGTTGGTAGCTCTTGATCCGGCAAACAAACCACCGCTGGTAGCGGTGGTTTTTTTGTTTGCAAGCAGCAGATTACGCGCAGAAAAAAAGGATCTCAAGAAGATCCTTTGATCTTTTCTACGGGGTCTGACGCTCAGTGGAACGAAAACTCACGTTAAGGGATTTTGGTCATGAG"
        ]
        
        return sequences
    
    def extract_codons(self, sequence):
        """
        Extract codons from a DNA sequence.
        
        Args:
            sequence: DNA sequence string
            
        Returns:
            List of codons (triplets)
        """
        # Clean sequence: convert to uppercase, remove whitespace
        sequence = sequence.upper().replace(' ', '').replace('\n', '')
        
        # Extract codons (triplets)
        codons = []
        for i in range(0, len(sequence) - 2, 3):
            codon = sequence[i:i+3]
            if len(codon) == 3 and codon in self.genetic_code:
                codons.append(codon)
        
        return codons
    
    def calculate_codon_usage(self, codons):
        """
        Calculate codon usage frequencies.
        
        Args:
            codons: List of codons
            
        Returns:
            Dictionary mapping codon -> frequency
        """
        counts = Counter(codons)
        total = len(codons)
        
        if total == 0:
            return {}
        
        usage = {codon: count / total for codon, count in counts.items()}
        return usage
    
    def calculate_mutation_rates(self, codon_usage):
        """
        Calculate mutation rates for each codon based on usage patterns.
        
        This estimates the "mutation rate" as the variability in usage
        within synonymous codon groups. Higher variability suggests more
        mutation or selection pressure.
        
        Args:
            codon_usage: Dictionary mapping codon -> frequency
            
        Returns:
            Dictionary mapping codon -> estimated mutation rate
        """
        mutation_rates = {}
        
        for aa, codon_group in self.synonymous_groups.items():
            # Get frequencies for this amino acid's codons
            frequencies = []
            for codon in codon_group:
                freq = codon_usage.get(codon, 0.0)
                frequencies.append(freq)
            
            # Calculate variance as a proxy for mutation rate
            # Higher variance = more divergence from uniform usage
            if len(frequencies) > 1 and sum(frequencies) > 0:
                mean_freq = np.mean(frequencies)
                variance = np.var(frequencies)
                
                # Normalize by mean to get coefficient of variation
                if mean_freq > 0:
                    mutation_rate = np.sqrt(variance) / mean_freq
                else:
                    mutation_rate = 0.0
                
                # Assign same rate to all codons in this group
                for codon in codon_group:
                    mutation_rates[codon] = mutation_rate
            else:
                for codon in codon_group:
                    mutation_rates[codon] = 0.0
        
        return mutation_rates
    
    def apply_stadlmann_transform(self, codon_usage, theta=THETA_STADLMANN):
        """
        Apply a θ-dependent transform to codon usage.
        
        This tests if θ ≈ 0.525 correlates with mutation patterns.
        We use a mathematical transformation inspired by the Z Framework's
        use of θ in prime density predictions.
        
        Args:
            codon_usage: Dictionary mapping codon -> frequency
            theta: Distribution level parameter (default: Stadlmann's 0.525)
            
        Returns:
            Dictionary mapping codon -> transformed value
        """
        phi = (1 + np.sqrt(5)) / 2  # Golden ratio
        transformed = {}
        
        for codon, freq in codon_usage.items():
            # Apply a θ-modulated transformation
            # This uses the golden ratio geodesic concept from the Z Framework
            if freq > 0:
                # Transform: log-scale + θ-weighted adjustment
                base_value = np.log(freq + EPSILON)
                theta_adjustment = theta * np.log(freq * phi + 1)
                transformed[codon] = base_value + theta_adjustment
            else:
                transformed[codon] = 0.0
        
        return transformed
    
    def test_correlation(self, mutation_rates, theta_transformed, test_type='pearson'):
        """
        Test correlation between mutation rates and θ-transformed values.
        
        Args:
            mutation_rates: Dictionary of mutation rates
            theta_transformed: Dictionary of θ-transformed values
            test_type: 'pearson' or 'spearman'
            
        Returns:
            Tuple of (correlation, p_value)
        """
        # Get matching codons
        common_codons = set(mutation_rates.keys()) & set(theta_transformed.keys())
        
        if len(common_codons) < 3:
            return 0.0, 1.0  # Not enough data
        
        # Extract values in same order
        x = [mutation_rates[c] for c in common_codons]
        y = [theta_transformed[c] for c in common_codons]
        
        # Calculate correlation
        if test_type == 'pearson':
            r, p = pearsonr(x, y)
        elif test_type == 'spearman':
            r, p = spearmanr(x, y)
        else:
            raise ValueError(f"Unknown test type: {test_type}")
        
        return r, p
    
    def bootstrap_confidence_interval(self, data1, data2, n_bootstrap=1000, alpha=0.05):
        """
        Calculate bootstrap confidence interval for correlation.
        
        Args:
            data1: First dataset (mutation rates)
            data2: Second dataset (theta-transformed values)
            n_bootstrap: Number of bootstrap resamples
            alpha: Significance level (default 0.05 for 95% CI)
            
        Returns:
            Tuple of (lower_bound, upper_bound, correlations)
        """
        n = len(data1)
        correlations = []
        
        for _ in range(n_bootstrap):
            # Resample with replacement
            indices = np.random.choice(n, size=n, replace=True)
            sample1 = [data1[i] for i in indices]
            sample2 = [data2[i] for i in indices]
            
            # Calculate correlation
            r, _ = pearsonr(sample1, sample2)
            correlations.append(r)
        
        # Calculate confidence interval
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100
        
        lower_bound = np.percentile(correlations, lower_percentile)
        upper_bound = np.percentile(correlations, upper_percentile)
        
        return lower_bound, upper_bound, correlations
    
    def run_experiment(self, n_bootstrap=1000):
        """
        Run the complete falsification experiment.
        
        Args:
            n_bootstrap: Number of bootstrap resamples
            
        Returns:
            Dictionary containing all results
        """
        print("="*70)
        print("CODON MUTATION RATE FALSIFICATION EXPERIMENT")
        print("="*70)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Seed: {self.seed}")
        print(f"Hypothesis: θ ≈ {THETA_STADLMANN} bounds mutation rates with r ≥ 0.90")
        print(f"Bootstrap resamples: {n_bootstrap}")
        print("="*70)
        print()
        
        results = {
            'metadata': {
                'date': datetime.now().isoformat(),
                'seed': self.seed,
                'theta_stadlmann': THETA_STADLMANN,
                'n_bootstrap': n_bootstrap,
                'hypothesis': 'θ ≈ 0.525 bounds mutation rates with r ≥ 0.90'
            }
        }
        
        # Step 1: Get sequences
        print("Step 1: Loading biological sequences...")
        sequences = self.get_sample_sequences()
        print(f"  Loaded {len(sequences)} sequences")
        print(f"  Total length: {sum(len(s) for s in sequences):,} bp")
        print()
        
        # Step 2: Extract codons
        print("Step 2: Extracting codons...")
        all_codons = []
        for seq in sequences:
            codons = self.extract_codons(seq)
            all_codons.extend(codons)
        print(f"  Extracted {len(all_codons):,} codons")
        print()
        
        # Step 3: Calculate codon usage
        print("Step 3: Calculating codon usage frequencies...")
        codon_usage = self.calculate_codon_usage(all_codons)
        print(f"  Analyzed {len(codon_usage)} unique codons")
        print()
        
        # Step 4: Calculate mutation rates
        print("Step 4: Estimating mutation rates from usage patterns...")
        mutation_rates = self.calculate_mutation_rates(codon_usage)
        print(f"  Computed rates for {len(mutation_rates)} codons")
        avg_mutation_rate = np.mean(list(mutation_rates.values()))
        print(f"  Average mutation rate: {avg_mutation_rate:.6f}")
        print()
        
        # Step 5: Apply Stadlmann transform
        print(f"Step 5: Applying Stadlmann θ={THETA_STADLMANN} transformation...")
        theta_transformed = self.apply_stadlmann_transform(codon_usage, THETA_STADLMANN)
        print(f"  Transformed {len(theta_transformed)} codon frequencies")
        print()
        
        # Step 6: Test correlation
        print("Step 6: Testing correlation between mutation rates and θ-transform...")
        
        # Get data for correlation
        common_codons = set(mutation_rates.keys()) & set(theta_transformed.keys())
        mutation_data = [mutation_rates[c] for c in common_codons]
        theta_data = [theta_transformed[c] for c in common_codons]
        
        # Pearson correlation
        r_pearson, p_pearson = self.test_correlation(
            mutation_rates, theta_transformed, 'pearson'
        )
        print(f"  Pearson correlation: r = {r_pearson:.6f}, p = {p_pearson:.6e}")
        
        # Spearman correlation
        r_spearman, p_spearman = self.test_correlation(
            mutation_rates, theta_transformed, 'spearman'
        )
        print(f"  Spearman correlation: r = {r_spearman:.6f}, p = {p_spearman:.6e}")
        print()
        
        # Step 7: Bootstrap confidence intervals
        print(f"Step 7: Computing bootstrap confidence intervals ({n_bootstrap} resamples)...")
        ci_lower, ci_upper, bootstrap_correlations = self.bootstrap_confidence_interval(
            mutation_data, theta_data, n_bootstrap=n_bootstrap
        )
        print(f"  95% CI: [{ci_lower:.6f}, {ci_upper:.6f}]")
        print(f"  Mean bootstrap r: {np.mean(bootstrap_correlations):.6f}")
        print(f"  Std bootstrap r: {np.std(bootstrap_correlations):.6f}")
        print()
        
        # Step 8: Hypothesis test
        print("="*70)
        print("HYPOTHESIS TEST RESULTS")
        print("="*70)
        
        hypothesis_claim = 0.90  # Claimed correlation r ≥ 0.90
        
        # Test if observed correlation meets claimed threshold
        meets_threshold = abs(r_pearson) >= hypothesis_claim
        ci_contains_threshold = ci_lower <= hypothesis_claim <= ci_upper
        ci_above_threshold = ci_lower >= hypothesis_claim
        
        print(f"\nClaimed threshold: r ≥ {hypothesis_claim}")
        print(f"Observed correlation: r = {r_pearson:.6f}")
        print(f"Bootstrap 95% CI: [{ci_lower:.6f}, {ci_upper:.6f}]")
        print()
        
        if meets_threshold:
            verdict = f"WARNING: {VERDICT_NOT_FALSIFIED}"
            falsified = False
        else:
            verdict = f"REJECTED: {VERDICT_FALSIFIED}"
            falsified = True
        
        if not ci_contains_threshold and not ci_above_threshold:
            verdict += " - High confidence"
        elif ci_contains_threshold:
            verdict += " - Moderate confidence (CI crosses threshold)"
        
        print(f"VERDICT: {verdict}")
        print()
        
        # Additional tests
        print("Additional Evidence:")
        print(f"  - Correlation significant? (p<0.05): {p_pearson < 0.05}")
        print(f"  - Effect size: {'Large' if abs(r_pearson) >= 0.5 else 'Medium' if abs(r_pearson) >= 0.3 else 'Small'}")
        print(f"  - CI excludes threshold: {not ci_contains_threshold and not ci_above_threshold}")
        print()
        
        # Store results
        results['sequences'] = {
            'n_sequences': len(sequences),
            'total_length': sum(len(s) for s in sequences),
            'n_codons': len(all_codons)
        }
        
        results['codon_analysis'] = {
            'n_unique_codons': len(codon_usage),
            'average_mutation_rate': float(avg_mutation_rate)
        }
        
        results['correlation'] = {
            'pearson_r': float(r_pearson),
            'pearson_p': float(p_pearson),
            'spearman_r': float(r_spearman),
            'spearman_p': float(p_spearman)
        }
        
        results['bootstrap'] = {
            'n_resamples': n_bootstrap,
            'ci_lower': float(ci_lower),
            'ci_upper': float(ci_upper),
            'mean_correlation': float(np.mean(bootstrap_correlations)),
            'std_correlation': float(np.std(bootstrap_correlations))
        }
        
        results['hypothesis_test'] = {
            'claimed_threshold': hypothesis_claim,
            'observed_correlation': float(r_pearson),
            'meets_threshold': bool(meets_threshold),
            'ci_contains_threshold': bool(ci_contains_threshold),
            'ci_above_threshold': bool(ci_above_threshold),
            'falsified': bool(falsified),
            'verdict': verdict,
            'statistically_significant': bool(p_pearson < 0.05)
        }
        
        results['raw_data'] = {
            'mutation_rates': {k: float(v) for k, v in mutation_rates.items()},
            'theta_transformed': {k: float(v) for k, v in theta_transformed.items()},
            'codon_usage': {k: float(v) for k, v in codon_usage.items()}
        }
        
        self.results = results
        return results
    
    def save_results(self, filename='results.json'):
        """
        Save results to JSON file.
        
        Args:
            filename: Output filename
        """
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"Results saved to: {filename}")


def main():
    """Run the falsification experiment."""
    # Create analyzer
    analyzer = CodonMutationAnalysis(seed=SEED)
    
    # Run experiment
    results = analyzer.run_experiment(n_bootstrap=1000)
    
    # Save results
    analyzer.save_results('results.json')
    
    print("="*70)
    print("EXPERIMENT COMPLETE")
    print("="*70)
    
    return results


if __name__ == '__main__':
    main()
