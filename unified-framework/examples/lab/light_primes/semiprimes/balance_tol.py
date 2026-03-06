#!/usr/bin/env python3
"""
Grid-search balance_tol for ZPredictor on balanced semiprimes.
"""

import math
import torch
import torch.nn as nn
from torch.utils.data import random_split, DataLoader
from tqdm import tqdm
from semi_predictor import BalancedSemiprimeDataset  # assume imported
from semi_predictor   import ZPredictor              # assume imported

def train_epoch(model, loader, opt, loss_fn, device):
    model.train()
    total = 0
    for x_n, x_d, target in loader:
        x_n, x_d, target = x_n.to(device), x_d.to(device), target.to(device)
        pred = model(x_n, x_d).squeeze(-1)
        loss = loss_fn(pred, target)
        opt.zero_grad(); loss.backward(); opt.step()
        total += loss.item() * x_n.size(0)
    return total / len(loader.dataset)

def eval_epoch(model, loader, loss_fn, device):
    model.eval()
    total = 0
    with torch.no_grad():
        for x_n, x_d, target in loader:
            x_n, x_d, target = x_n.to(device), x_d.to(device), target.to(device)
            pred = model(x_n, x_d).squeeze(-1)
            total += loss_fn(pred, target).item() * x_n.size(0)
    return total / len(loader.dataset)

def grid_search(tols, n_samples=100_000, epochs=10):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    results = {}

    for tol in tols:
        # Prepare dataset
        ds = BalancedSemiprimeDataset(n_samples, balance_tol=tol)
        n_val = int(len(ds)*0.2)
        train_ds, val_ds = random_split(ds, [len(ds)-n_val, n_val])
        train_loader = DataLoader(train_ds, batch_size=512, shuffle=True)
        val_loader   = DataLoader(val_ds,   batch_size=512)

        # Model & optimizer
        model = ZPredictor().to(device)
        opt   = torch.optim.Adam(model.parameters(), lr=1e-3)
        loss_fn = nn.MSELoss()

        # Training loop
        best_val = float('inf')
        for _ in range(epochs):
            train_epoch(model, train_loader, opt, loss_fn, device)
            val_loss = eval_epoch(model, val_loader, loss_fn, device)
            best_val = min(best_val, val_loss)

        results[tol] = best_val
        print(f"tol={tol:.2f}  best_val_loss={best_val:.4e}")

    return results

if __name__ == "__main__":
    tols = [0.01, 0.05, 0.1, 0.2, 0.3]
    stats = grid_search(tols)
    print("\nGrid Search Results:", stats)
