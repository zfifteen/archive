#!/usr/bin/env python3
"""
I Ching Hexagram State Management for Z Framework Integration
===========================================================

Implements the 64 hexagram state space (000000 → 111111) with:
- Trigram weight computation using five-element theory
- Yang-balance heuristics for optimization (~0.618 ratio)
- Line change mutations for recursive branching
- Golden ratio (φ) scaling integration

Based on the hypothesis that I Ching turnover cycles mirror
recursive reduction patterns in RSA factorization.
"""

import mpmath
import numpy as np
from typing import Tuple, List, Dict
from dataclasses import dataclass
from enum import Enum

# Set high precision for cryptographic calculations
mpmath.mp.dps = 50

# Golden ratio (φ) - central to the I Ching-Z integration
PHI = mpmath.mpf((1 + mpmath.sqrt(5)) / 2)

class Element(Enum):
    """Five-element theory mapping for trigram weights"""
    WOOD = 0    # 木 - Growth, expansion
    FIRE = 1    # 火 - Energy, transformation  
    EARTH = 2   # 土 - Stability, center
    METAL = 3   # 金 - Structure, contraction
    WATER = 4   # 水 - Flow, adaptation

# Five-element weights for geometric scaling (optimized for warp sensitivity)
ELEMENT_WEIGHTS = {
    Element.WOOD: mpmath.mpf(1.618),   # φ - natural growth
    Element.FIRE: mpmath.mpf(2.718),   # e - exponential transformation
    Element.EARTH: mpmath.mpf(1.000),  # 1 - stability baseline
    Element.METAL: mpmath.mpf(0.618),  # 1/φ - contraction ratio
    Element.WATER: mpmath.mpf(1.414),  # √2 - adaptive flow
}

@dataclass
class Trigram:
    """Represents a 3-line trigram (bottom to top)"""
    lines: Tuple[int, int, int]  # 0=yin (broken), 1=yang (solid)
    
    @property
    def binary_value(self) -> int:
        """Convert trigram to binary integer (0-7)"""
        return self.lines[0] + 2*self.lines[1] + 4*self.lines[2]
    
    @property
    def element(self) -> Element:
        """Map trigram to five-element classification"""
        # Classical I Ching trigram-element mapping
        mapping = {
            0b000: Element.EARTH,  # ☷ Kun (Earth)
            0b001: Element.WATER,  # ☵ Kan (Water)  
            0b010: Element.FIRE,   # ☲ Li (Fire)
            0b011: Element.WATER,  # ☱ Dui (Lake/Water)
            0b100: Element.WOOD,   # ☳ Zhen (Thunder/Wood)
            0b101: Element.WOOD,   # ☴ Xun (Wind/Wood)
            0b110: Element.FIRE,   # ☰ Qian (Heaven/Fire)
            0b111: Element.METAL,  # ☶ Gen (Mountain/Metal)
        }
        return mapping[self.binary_value]
    
    @property
    def weight(self) -> mpmath.mpf:
        """Get five-element weight for this trigram"""
        return ELEMENT_WEIGHTS[self.element]
    
    @property
    def yang_count(self) -> int:
        """Count yang lines (solid lines = 1)"""
        return sum(self.lines)
    
    @property
    def yang_balance(self) -> mpmath.mpf:
        """Calculate yang balance ratio (0.0 to 1.0)"""
        return mpmath.mpf(self.yang_count) / 3

@dataclass  
class Hexagram:
    """Represents a 6-line hexagram (bottom to top)"""
    lines: Tuple[int, int, int, int, int, int]  # 0=yin, 1=yang
    
    def __post_init__(self):
        """Validate hexagram structure"""
        if len(self.lines) != 6 or not all(line in (0, 1) for line in self.lines):
            raise ValueError("Hexagram must have exactly 6 lines, each 0 or 1")
    
    @property
    def binary_value(self) -> int:
        """Convert hexagram to binary integer (0-63)"""
        return sum(line * (2 ** i) for i, line in enumerate(self.lines))
    
    @property
    def lower_trigram(self) -> Trigram:
        """Bottom three lines"""
        return Trigram(self.lines[:3])
    
    @property
    def upper_trigram(self) -> Trigram:
        """Top three lines"""
        return Trigram(self.lines[3:])
    
    @property
    def yang_balance(self) -> mpmath.mpf:
        """Overall yang balance for the hexagram"""
        yang_count = sum(self.lines)
        return mpmath.mpf(yang_count) / 6
    
    @property
    def is_balanced(self) -> bool:
        """Check if hexagram has optimal yang balance (~0.618)"""
        return abs(self.yang_balance - (1/PHI)) < mpmath.mpf(0.1)
    
    def trigram_weight_product(self) -> mpmath.mpf:
        """Product of upper and lower trigram weights"""
        return self.lower_trigram.weight * self.upper_trigram.weight
    
    def geometric_scaling_factor(self, depth: int, sigma: mpmath.mpf = mpmath.mpf(1.0)) -> mpmath.mpf:
        """
        Compute r_i = trigram_weight(hex) * σ * φ^(depth % 6)
        
        Args:
            depth: Current recursion depth
            sigma: Base scaling parameter
            
        Returns:
            Geometric scaling factor for this hexagram at given depth
        """
        phi_power = mpmath.power(PHI, depth % 6)
        return self.trigram_weight_product() * sigma * phi_power
    
    def mutate_line(self, position: int) -> 'Hexagram':
        """
        Create new hexagram by flipping line at position (0-5, bottom to top)
        
        This represents a line change in I Ching divination, driving
        the recursive branching in factorization attempts.
        """
        if not 0 <= position <= 5:
            raise ValueError("Line position must be 0-5")
        
        new_lines = list(self.lines)
        new_lines[position] = 1 - new_lines[position]  # Flip 0→1 or 1→0
        return Hexagram(tuple(new_lines))
    
    def generate_mutations(self) -> List['Hexagram']:
        """Generate all single-line mutations of this hexagram"""
        return [self.mutate_line(i) for i in range(6)]
    
    def hex_int_for_weyl(self) -> int:
        """
        Convert hexagram to integer for Weyl sequence generation:
        trial = floor(φ * prev + hex_int) % floor(sqrt(N))
        """
        return self.binary_value

class IChingState:
    """Manages I Ching state transitions for recursive factorization"""
    
    def __init__(self, initial_hex: int = 0):
        """
        Initialize with hexagram state
        
        Args:
            initial_hex: Initial hexagram as integer (0-63), default Receptive 000000
        """
        self.current_hex = self._int_to_hexagram(initial_hex)
        self.mutation_history = [self.current_hex]
        self.depth = 0
        
    def _int_to_hexagram(self, hex_int: int) -> Hexagram:
        """Convert integer (0-63) to Hexagram"""
        if not 0 <= hex_int <= 63:
            raise ValueError("Hexagram integer must be 0-63")
        
        # Convert to 6-bit binary
        lines = tuple((hex_int >> i) & 1 for i in range(6))
        return Hexagram(lines)
    
    def should_mutate(self, drift_epsilon: mpmath.mpf) -> bool:
        """
        Determine if hexagram should mutate based on drift > ε
        
        In the hypothesis: "start Receptive 000000, mutate on drift > ε to branch"
        """
        # Simplified drift detection: check if current scaling factor
        # deviates significantly from golden ratio balance
        current_factor = self.current_hex.geometric_scaling_factor(self.depth)
        golden_target = PHI  # Target around φ for optimal balance
        
        drift = abs(current_factor - golden_target)
        return drift > drift_epsilon
    
    def advance_with_mutation(self, epsilon: mpmath.mpf = mpmath.mpf(0.1)) -> bool:
        """
        Advance state with potential mutation
        
        Args:
            epsilon: Drift threshold for mutation triggering
            
        Returns:
            True if mutation occurred, False if state remained stable
        """
        self.depth += 1
        
        if self.should_mutate(epsilon):
            # Select mutation that optimizes yang balance toward φ^(-1) ≈ 0.618
            mutations = self.current_hex.generate_mutations()
            
            # Choose mutation closest to ideal yang balance
            target_balance = 1 / PHI  # ≈ 0.618
            best_mutation = min(mutations, 
                              key=lambda h: abs(h.yang_balance - target_balance))
            
            self.current_hex = best_mutation
            self.mutation_history.append(self.current_hex)
            return True
        
        return False
    
    def prune_dead_branches(self, candidate_trials: List[int]) -> List[int]:
        """
        Apply yang-balance optimization to prune dead branches
        
        The hypothesis claims 38% faster pruning through balanced hexagrams.
        """
        if not self.current_hex.is_balanced:
            # Non-balanced hexagrams have poor pruning efficiency
            return candidate_trials
        
        # Apply yang-balance heuristic: keep candidates that align with
        # current hexagram's geometric scaling
        scaling_factor = self.current_hex.geometric_scaling_factor(self.depth)
        
        # Prune candidates that don't resonate with current hex scaling
        pruned = []
        for trial in candidate_trials:
            # Simple heuristic: keep if trial modulo scaling aligns with yang balance
            if (trial % int(scaling_factor)) / int(scaling_factor) <= self.current_hex.yang_balance:
                pruned.append(trial)
        
        return pruned

def create_receptive_hexagram() -> Hexagram:
    """Create initial Receptive hexagram (000000) as starting state"""
    return Hexagram((0, 0, 0, 0, 0, 0))

def demonstrate_iching_integration():
    """Demonstrate I Ching integration capabilities"""
    print("🌟 I Ching-Z Framework Integration Demo")
    print("=" * 50)
    
    # Start with Receptive hexagram (000000)
    state = IChingState(0)  # Receptive
    print(f"Initial State: {state.current_hex.binary_value:06b}")
    print(f"Yang Balance: {float(state.current_hex.yang_balance):.3f}")
    print(f"Trigram Weights: Lower={float(state.current_hex.lower_trigram.weight):.3f}, "
          f"Upper={float(state.current_hex.upper_trigram.weight):.3f}")
    
    # Demonstrate mutations
    print(f"\n🔄 Mutation Sequence (depth ≤ 10)")
    for i in range(10):
        mutated = state.advance_with_mutation(epsilon=mpmath.mpf(0.05))
        if mutated:
            hex_binary = f"{state.current_hex.binary_value:06b}"
            yang_bal = float(state.current_hex.yang_balance)
            scaling = float(state.current_hex.geometric_scaling_factor(state.depth))
            print(f"  Depth {state.depth}: {hex_binary} | Yang={yang_bal:.3f} | Scale={scaling:.3f}")
    
    # Demonstrate pruning
    test_candidates = list(range(100, 200, 10))
    pruned = state.prune_dead_branches(test_candidates)
    print(f"\n✂️ Branch Pruning Demo")
    print(f"Original candidates: {len(test_candidates)}")
    print(f"After yang-balance pruning: {len(pruned)}")
    print(f"Pruning efficiency: {100 * (1 - len(pruned)/len(test_candidates)):.1f}%")
    
    print(f"\n✅ I Ching integration ready for RSA-4096 testing")

if __name__ == "__main__":
    demonstrate_iching_integration()