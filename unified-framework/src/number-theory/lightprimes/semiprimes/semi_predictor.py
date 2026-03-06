#!/usr/bin/env python3
"""
Train ZPredictor to estimate the frame-shift Δₚ for balanced semiprimes.
"""

import math
import random
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, random_split
from tqdm import tqdm

# 1. Model Definition
class ZPredictor(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(2, 64)
        self.fc2 = nn.Linear(64, 1)

    def forward(self, x_n, x_delta):
        x = torch.cat([x_n, x_delta], dim=-1)
        h = torch.relu(self.fc1(x))
        return self.fc2(h)  # raw Δₚ output

# 2. Dataset for Balanced Semiprimes
class BalancedSemiprimeDataset(Dataset):
    def __init__(self, n_samples, n_min=10**6, n_max=10**10, balance_tol=0.1):
        super().__init__()
        self.data = []
        for _ in range(n_samples):
            # pick sqrt(n) in [sqrt(n_min), sqrt(n_max)]
            r = random.uniform(math.sqrt(n_min), math.sqrt(n_max))
            # choose p within ±balance_tol fraction of r
            p = int(max(2, r * (1 - balance_tol) + random.random() * r * balance_tol * 2))
            # find next prime ≥ p
            while not self._is_prime(p):
                p += 1
            # choose q similarly
            q = int(max(p, r * (1 - balance_tol) + random.random() * r * balance_tol * 2))
            while not self._is_prime(q):
                q += 1
            n = p * q
            sqrt_n = math.sqrt(n)

            # features
            x_n     = sqrt_n / math.e**2
            x_delta = math.log(n) / 2

            # target Δₚ
            delta_p = sqrt_n - p

            self.data.append((x_n, x_delta, delta_p))

    def _is_prime(self, k):
        if k < 2:
            return False
        if k % 2 == 0 and k > 2:
            return False
        r = int(math.sqrt(k))
        for i in range(3, r+1, 2):
            if k % i == 0:
                return False
        return True

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        x_n, x_delta, delta_p = self.data[idx]
        return (
            torch.tensor([x_n], dtype=torch.float32),
            torch.tensor([x_delta], dtype=torch.float32),
            torch.tensor([delta_p], dtype=torch.float32)
        )

# 3. Training Function
def train(model, loader, opt, loss_fn, device):
    model.train()
    total_loss = 0.0
    for x_n, x_delta, target in loader:
        x_n, x_delta, target = x_n.to(device), x_delta.to(device), target.to(device)
        pred = model(x_n, x_delta).squeeze(-1)
        loss = loss_fn(pred, target)
        opt.zero_grad()
        loss.backward()
        opt.step()
        total_loss += loss.item() * x_n.size(0)
    return total_loss / len(loader.dataset)

# 4. Validation Function
def evaluate(model, loader, loss_fn, device):
    model.eval()
    total_loss = 0.0
    with torch.no_grad():
        for x_n, x_delta, target in loader:
            x_n, x_delta, target = x_n.to(device), x_delta.to(device), target.to(device)
            pred = model(x_n, x_delta).squeeze(-1)
            loss = loss_fn(pred, target)
            total_loss += loss.item() * x_n.size(0)
    return total_loss / len(loader.dataset)

# 5. Main Training Loop
def main():
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # Hyperparameters
    N_SAMPLES   = 200_000    # total semiprime examples
    BATCH_SIZE  = 512
    EPOCHS      = 30
    LR          = 1e-3
    VAL_SPLIT   = 0.2

    # Prepare dataset and loaders
    dataset = BalancedSemiprimeDataset(N_SAMPLES)
    n_val = int(len(dataset) * VAL_SPLIT)
    n_train = len(dataset) - n_val
    train_ds, val_ds = random_split(dataset, [n_train, n_val])
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False)

    # Model, optimizer, and loss
    model   = ZPredictor().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    loss_fn   = nn.MSELoss()

    best_val = float('inf')
    for epoch in range(1, EPOCHS + 1):
        train_loss = train(model, train_loader, optimizer, loss_fn, device)
        val_loss   = evaluate(model, val_loader, loss_fn, device)

        print(f"Epoch {epoch:02d}  Train Loss: {train_loss:.4e}  Val Loss: {val_loss:.4e}")

        # Save best model
        if val_loss < best_val:
            best_val = val_loss
            torch.save(model.state_dict(), "zpredictor_best.pt")

    print("Training complete. Best validation loss:", best_val)

if __name__ == "__main__":
    main()
