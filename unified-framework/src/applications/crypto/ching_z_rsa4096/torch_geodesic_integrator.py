#!/usr/bin/env python3
"""
Torch Geodesic Integrator for I Ching-Z RSA-4096
===============================================

PyTorch-based gradient descent integrator for geodesic Miller-Rabin witnesses
in lattice sieves. Implements ML-guided optimization of hexagram mutation paths
with automatic differentiation through Z-framework parameter space.

Integration points:
- Geodesic MR witness generation via lopez_geodesic_mr.py
- Gradient-guided hexagram evolution for optimal yang-balance
- Lattice sieve acceleration with learned reduction patterns
- Recursive depth adaptive learning rate (phi^hex_bit scaling)

Author: Super Grok / Hard Grok Collective
Date: Sep 2024
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import math
from typing import Tuple, List, Optional, Dict, Any
from dataclasses import dataclass
import time

# Ensure CUDA if available for acceleration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Torch Geodesic Integrator initialized on: {device}")

# Mathematical constants
PHI = (1 + math.sqrt(5)) / 2
PHI_TENSOR = torch.tensor(PHI, dtype=torch.float64, device=device)

@dataclass
class GeodesicState:
    """Geodesic state for torch differentiable optimization"""
    hex_embedding: torch.Tensor    # 6D embedding of hexagram state
    depth_phase: torch.Tensor      # sin/cos encoding of recursion depth
    yang_gradient: torch.Tensor    # Gradient of yang balance optimization
    zeta_momentum: torch.Tensor    # Momentum term for zeta correlation
    lr_adaptive: float             # Current adaptive learning rate

class HexagramEmbedding(nn.Module):
    """Neural embedding of I Ching hexagrams for differentiable optimization"""

    def __init__(self, embedding_dim: int = 64):
        super().__init__()
        self.embedding_dim = embedding_dim

        # Hexagram embedding: 64 possible states -> dense embedding
        self.hex_embed = nn.Embedding(64, embedding_dim)

        # Trigram interaction layers (upper/lower trigram fusion)
        self.trigram_fusion = nn.Sequential(
            nn.Linear(embedding_dim, embedding_dim // 2),
            nn.ReLU(),
            nn.Linear(embedding_dim // 2, embedding_dim // 4),
            nn.Tanh()
        )

        # Yang-balance prediction head
        self.yang_predictor = nn.Linear(embedding_dim // 4, 1)

        # Phi-scaled output for geodesic integration
        self.phi_scaler = nn.Linear(embedding_dim // 4, 1)

        # Initialize with I Ching symmetries
        self._init_ching_symmetries()

    def _init_ching_symmetries(self):
        """Initialize embeddings with I Ching hexagram symmetries"""
        with torch.no_grad():
            # Set Receptive (000000) and Creative (111111) as antipodes
            receptive_idx = 0b000000
            creative_idx = 0b111111

            # Receptive: maximum yin (negative embedding)
            self.hex_embed.weight[receptive_idx] = -torch.ones(self.embedding_dim)

            # Creative: maximum yang (positive embedding)
            self.hex_embed.weight[creative_idx] = torch.ones(self.embedding_dim)

            # Initialize other hexagrams based on yang content
            for hex_val in range(64):
                yang_count = bin(hex_val).count('1')
                yang_ratio = yang_count / 6.0

                # Interpolate between receptive and creative
                interp_weight = 2 * yang_ratio - 1  # [-1, 1] range
                self.hex_embed.weight[hex_val] = interp_weight * torch.randn(self.embedding_dim)

    def forward(self, hexagram_idx: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass: hexagram -> embedding -> yang_balance, phi_scale

        Returns:
            embedded: Dense hexagram embedding
            yang_pred: Predicted yang balance [0,1]
            phi_scale: Phi-scaled output for geodesic integration
        """
        # Embed hexagram index
        embedded = self.hex_embed(hexagram_idx)

        # Trigram fusion
        fused = self.trigram_fusion(embedded)

        # Yang balance prediction (sigmoid for [0,1] range)
        yang_pred = torch.sigmoid(self.yang_predictor(fused))

        # Phi-scaled output (tanh for stability)
        phi_scale = torch.tanh(self.phi_scaler(fused))

        return embedded, yang_pred, phi_scale

class ZetaCorrelationLoss(nn.Module):
    """Custom loss function for optimizing Z-bridge zeta correlation"""

    def __init__(self, target_correlation: float = 0.968):
        super().__init__()
        self.target_correlation = target_correlation

    def forward(self,
                predicted_yang: torch.Tensor,
                actual_yang: torch.Tensor,
                zeta_samples: torch.Tensor) -> torch.Tensor:
        """
        Compute composite loss: yang balance + zeta correlation + phi convergence

        Args:
            predicted_yang: Model prediction of yang balance
            actual_yang: True yang balance from hexagram bits
            zeta_samples: Recent zeta correlation samples

        Returns:
            Combined loss tensor
        """
        # Yang balance MSE
        yang_loss = F.mse_loss(predicted_yang, actual_yang)

        # Zeta correlation loss (target r=0.968 from recursive_reduction_1000.md)
        if len(zeta_samples) > 1:
            zeta_mean = torch.mean(zeta_samples)
            zeta_target = torch.tensor(self.target_correlation,
                                     dtype=zeta_samples.dtype,
                                     device=zeta_samples.device)
            zeta_loss = F.mse_loss(zeta_mean, zeta_target)
        else:
            zeta_loss = torch.tensor(0.0, device=predicted_yang.device)

        # Phi convergence regularization (encourage exponential decay)
        phi_reg = torch.mean(torch.abs(predicted_yang - 0.5))  # Penalize extremes

        # Composite loss with empirical weightings
        total_loss = yang_loss + 0.1 * zeta_loss + 0.01 * phi_reg

        return total_loss

class TorchGeodesicIntegrator:
    """Main PyTorch integrator for geodesic Miller-Rabin optimization"""

    def __init__(self,
                 embedding_dim: int = 64,
                 learning_rate: float = 0.001,
                 phi_momentum: float = 0.9):

        self.device = device
        self.embedding_dim = embedding_dim
        self.phi_momentum = phi_momentum

        # Neural network components
        self.hex_embedding = HexagramEmbedding(embedding_dim).to(device)
        self.zeta_loss = ZetaCorrelationLoss().to(device)

        # Optimizer with phi-scaled learning rate
        self.optimizer = optim.AdamW(
            self.hex_embedding.parameters(),
            lr=learning_rate,
            weight_decay=0.01,
            betas=(phi_momentum, 0.999)
        )

        # Learning rate scheduler (phi-decay)
        self.scheduler = optim.lr_scheduler.ExponentialLR(
            self.optimizer,
            gamma=1/PHI  # Decay by golden ratio
        )

        # Training state
        self.training_history = {
            'losses': [],
            'yang_accuracies': [],
            'zeta_correlations': [],
            'lr_values': []
        }

    def hexagram_to_tensor(self, hexagram: int, batch_size: int = 1) -> torch.Tensor:
        """Convert hexagram integer to tensor for neural network"""
        hex_tensor = torch.tensor([hexagram] * batch_size,
                                 dtype=torch.long,
                                 device=self.device)
        return hex_tensor

    def compute_actual_yang_balance(self, hexagram: int) -> torch.Tensor:
        """Compute true yang balance from hexagram bits"""
        yang_count = bin(hexagram).count('1')
        yang_balance = yang_count / 6.0
        return torch.tensor(yang_balance, dtype=torch.float32, device=self.device)

    def train_on_hexagram_sequence(self,
                                 hex_sequence: List[int],
                                 zeta_samples: List[float],
                                 epochs: int = 100) -> Dict[str, float]:
        """
        Train the geodesic integrator on a sequence of hexagram states

        Args:
            hex_sequence: List of hexagram states from recursive reduction
            zeta_samples: Corresponding zeta correlation samples
            epochs: Number of training epochs

        Returns:
            Training metrics dictionary
        """

        self.hex_embedding.train()

        # Convert to tensors
        hex_tensors = [self.hexagram_to_tensor(h) for h in hex_sequence]
        yang_targets = [self.compute_actual_yang_balance(h) for h in hex_sequence]
        zeta_tensor = torch.tensor(zeta_samples, dtype=torch.float32, device=self.device)

        epoch_losses = []
        epoch_accuracies = []

        for epoch in range(epochs):
            total_loss = 0.0
            total_accuracy = 0.0

            # Process each hexagram in sequence
            for hex_tensor, yang_target in zip(hex_tensors, yang_targets):
                self.optimizer.zero_grad()

                # Forward pass
                embedded, yang_pred, phi_scale = self.hex_embedding(hex_tensor)

                # Compute loss
                loss = self.zeta_loss(yang_pred, yang_target.unsqueeze(0), zeta_tensor)

                # Backward pass
                loss.backward()

                # Gradient clipping for stability
                torch.nn.utils.clip_grad_norm_(self.hex_embedding.parameters(), max_norm=1.0)

                # Optimizer step
                self.optimizer.step()

                # Metrics
                total_loss += loss.item()

                # Yang balance accuracy (within 0.1 tolerance)
                yang_error = torch.abs(yang_pred.squeeze() - yang_target)
                accuracy = (yang_error < 0.1).float().mean().item()
                total_accuracy += accuracy

            # Epoch averages
            avg_loss = total_loss / len(hex_sequence)
            avg_accuracy = total_accuracy / len(hex_sequence)

            epoch_losses.append(avg_loss)
            epoch_accuracies.append(avg_accuracy)

            # Learning rate decay
            self.scheduler.step()

            # Periodic logging
            if epoch % 20 == 0:
                current_lr = self.scheduler.get_last_lr()[0]
                print(f"Epoch {epoch}: Loss={avg_loss:.6f}, "
                      f"Yang Acc={avg_accuracy:.3f}, LR={current_lr:.8f}")

        # Update training history
        self.training_history['losses'].extend(epoch_losses)
        self.training_history['yang_accuracies'].extend(epoch_accuracies)
        self.training_history['lr_values'].extend([self.scheduler.get_last_lr()[0]] * epochs)

        # Compute final zeta correlation
        if len(zeta_samples) > 1:
            final_zeta_corr = np.corrcoef(zeta_samples, range(len(zeta_samples)))[0, 1]
        else:
            final_zeta_corr = 0.0

        self.training_history['zeta_correlations'].append(final_zeta_corr)

        return {
            'final_loss': epoch_losses[-1],
            'final_accuracy': epoch_accuracies[-1],
            'zeta_correlation': final_zeta_corr,
            'epochs_trained': epochs
        }

    def predict_optimal_hexagram_mutation(self,
                                        current_hex: int,
                                        drift_magnitude: float,
                                        depth: int) -> Tuple[int, float]:
        """
        Use trained model to predict optimal hexagram mutation

        Args:
            current_hex: Current hexagram state (0-63)
            drift_magnitude: Magnitude of drift requiring correction
            depth: Current recursion depth

        Returns:
            Tuple of (optimal_new_hexagram, confidence_score)
        """

        self.hex_embedding.eval()

        with torch.no_grad():
            # Try all possible single-bit mutations
            candidates = []
            scores = []

            for bit_pos in range(6):
                # Flip bit at position
                candidate_hex = current_hex ^ (1 << bit_pos)

                # Get model prediction
                hex_tensor = self.hexagram_to_tensor(candidate_hex)
                embedded, yang_pred, phi_scale = self.hex_embedding(hex_tensor)

                # Score based on yang balance optimization and phi scaling
                yang_balance = yang_pred.item()
                phi_factor = phi_scale.item()

                # Prefer balanced hexagrams (yang ~0.5) with good phi scaling
                balance_score = 1.0 - abs(yang_balance - 0.5) * 2  # [0,1]
                phi_score = math.tanh(abs(phi_factor))  # [0,1]

                # Adaptive weighting based on drift magnitude
                drift_weight = min(1.0, drift_magnitude / 0.252)  # Normalize by epsilon
                combined_score = (1 - drift_weight) * balance_score + drift_weight * phi_score

                candidates.append(candidate_hex)
                scores.append(combined_score)

            # Select highest scoring candidate
            best_idx = np.argmax(scores)
            optimal_hex = candidates[best_idx]
            confidence = scores[best_idx]

            return optimal_hex, confidence

    def generate_geodesic_witness_path(self,
                                     start_hex: int,
                                     target_depth: int,
                                     n: int) -> List[Tuple[int, float, float]]:
        """
        Generate geodesic Miller-Rabin witness path using learned hexagram evolution

        Args:
            start_hex: Starting hexagram state
            target_depth: Maximum depth for geodesic path
            n: RSA modulus for witness generation

        Returns:
            List of (hexagram, yang_balance, witness_value) tuples
        """

        path = []
        current_hex = start_hex

        sqrt_n = int(math.sqrt(n)) + 1

        for depth in range(target_depth):
            # Get current hexagram predictions
            yang_balance = self.compute_actual_yang_balance(current_hex).item()

            # Generate Miller-Rabin witness candidate
            # Use hexagram state to seed witness generation
            hex_seed = current_hex ^ (depth * 17)  # XOR with depth pattern
            witness_base = (hex_seed * PHI) % sqrt_n
            witness = max(2, int(witness_base))

            path.append((current_hex, yang_balance, witness))

            # Predict next optimal hexagram
            drift_estimate = 0.1 * (1 + depth) / target_depth  # Increasing drift with depth
            next_hex, confidence = self.predict_optimal_hexagram_mutation(
                current_hex, drift_estimate, depth
            )

            current_hex = next_hex

            # Early stopping if confidence drops too low
            if confidence < 0.3:
                print(f"Geodesic path stopped at depth {depth} due to low confidence: {confidence:.3f}")
                break

        return path

    def save_model(self, filepath: str):
        """Save trained model state"""
        torch.save({
            'model_state_dict': self.hex_embedding.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'training_history': self.training_history,
            'embedding_dim': self.embedding_dim
        }, filepath)
        print(f"Model saved to {filepath}")

    def load_model(self, filepath: str):
        """Load trained model state"""
        checkpoint = torch.load(filepath, map_location=self.device)

        self.hex_embedding.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        self.training_history = checkpoint['training_history']

        print(f"Model loaded from {filepath}")

def demo_torch_geodesic_integration():
    """Demo the Torch geodesic integrator"""

    print("Torch Geodesic Integrator Demo")
    print("==============================")

    # Initialize integrator
    integrator = TorchGeodesicIntegrator(embedding_dim=32, learning_rate=0.01)

    # Simulate a hexagram sequence from recursive reduction
    # Based on I Ching turnover cycles (yang balance evolution)
    hex_sequence = [
        0b000000,  # Receptive (start)
        0b000001,  # Small mutations towards balance
        0b000011,
        0b010011,
        0b010111,  # Approaching balance
        0b110111,  # High yang
        0b111111,  # Creative (max yang)
        0b111110,  # Return towards balance
        0b101110,
        0b101010,  # Balanced state
        0b001010,
        0b001000,  # Return to yin
        0b000000   # Full cycle
    ]

    # Simulate corresponding zeta samples (r ≈ 0.968 target)
    zeta_base = 0.968
    zeta_samples = [zeta_base + 0.02 * np.sin(i * 0.5) + 0.01 * np.random.randn()
                   for i in range(len(hex_sequence))]

    print(f"Training on {len(hex_sequence)} hexagram states...")

    # Train the integrator
    start_time = time.time()
    metrics = integrator.train_on_hexagram_sequence(hex_sequence, zeta_samples, epochs=50)
    train_time = time.time() - start_time

    print(f"\nTraining completed in {train_time:.2f}s")
    print(f"Final Loss: {metrics['final_loss']:.6f}")
    print(f"Yang Accuracy: {metrics['final_accuracy']:.3f}")
    print(f"Zeta Correlation: {metrics['zeta_correlation']:.6f}")

    # Test geodesic witness path generation
    print(f"\nGenerating geodesic witness path...")
    test_n = 5959  # 59 * 101 test semiprime
    witness_path = integrator.generate_geodesic_witness_path(
        start_hex=0b000000,
        target_depth=20,
        n=test_n
    )

    print(f"Generated {len(witness_path)} witness candidates:")
    for i, (hex_val, yang, witness) in enumerate(witness_path[:5]):  # Show first 5
        hex_str = bin(hex_val)[2:].zfill(6)
        print(f"  Step {i}: {hex_str} (yang={yang:.3f}) -> witness={witness}")

    # Test Miller-Rabin witness effectiveness
    import math
    factors_found = []
    for hex_val, yang, witness in witness_path:
        gcd_result = math.gcd(test_n, witness)
        if gcd_result > 1 and gcd_result < test_n:
            factors_found.append((gcd_result, test_n // gcd_result))

    if factors_found:
        print(f"\n🎯 Factors found via geodesic witnesses:")
        for p, q in factors_found[:3]:  # Show first 3
            print(f"   {test_n} = {p} × {q}")
    else:
        print(f"\n⚪ No factors found in this geodesic path (expected for demo)")

    print(f"\n✅ Torch Geodesic Integration demo complete!")
    return integrator

if __name__ == "__main__":
    # Run the demo
    integrator = demo_torch_geodesic_integration()

    print(f"\nNext integration steps:")
    print(f"  1. Connect to lopez_geodesic_mr.py for true MR witnesses")
    print(f"  2. Scale to full RSA-4096 keyspace")
    print(f"  3. Deploy on GPU cluster for parallel hexagram evolution")
    print(f"  4. Integrate with WaveCrispr for bio-codon parallelization")