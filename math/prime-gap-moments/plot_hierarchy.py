#!/usr/bin/env python3
"""
Visualization suite for: Reversed Convergence Hierarchy in Prime Gap Moments
Data: Cohen (2024), arXiv:2405.16019
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path

# In restricted environments (e.g. sandboxes), HOME cache paths may be read-only.
# Point plotting/font caches to writable temp locations before importing Matplotlib.
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", tempfile.gettempdir())

import numpy as np

def _ensure_matplotlib():
    """Fallback to common global site-packages when venv lacks matplotlib."""
    try:
        import matplotlib as _matplotlib
        return _matplotlib
    except ModuleNotFoundError:
        py_ver = f"python{sys.version_info.major}.{sys.version_info.minor}"
        candidates = [
            Path(sys.base_prefix) / "lib" / py_ver / "site-packages",
            Path("/Library/Frameworks/Python.framework/Versions")
            / f"{sys.version_info.major}.{sys.version_info.minor}"
            / "lib"
            / py_ver
            / "site-packages",
        ]
        for candidate in candidates:
            if candidate.exists():
                sys.path.append(str(candidate))
        try:
            import matplotlib as _matplotlib
            return _matplotlib
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "matplotlib is required. Install it in this environment with: "
                "python -m pip install matplotlib"
            ) from exc


matplotlib = _ensure_matplotlib()
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyArrowPatch
from math import factorial, log

# ─── Data ────────────────────────────────────────────────────────────────────

COHEN_DATA = [
    (3510,        9.3293,  136.2017,   2781.8,    74292.0),
    (22998,       11.3982, 210.7095,   5506.0,   185460.0),
    (155609,      13.4770, 304.1124,   9891.4,   425030.0),
    (1077869,     15.5652, 412.7866,  15776.0,   788630.0),
    (7603551,     17.6520, 539.4491,  23885.0,  1386400.0),
    (54400026,    19.7379, 683.2373,  34423.0,  2280600.0),
    (393615804,   21.8231, 844.1273,  47670.0,  3544000.0),
    (2.8744e9,    23.9074, 1022.2,    63972.0,  5277300.0),
    (2.1152e10,   25.9908, 1217.3,    83638.0,  7581900.0),
    (1.5666e11,   28.0736, 1429.6,   106990.0, 10574000.0),
    (1.1667e12,   30.1560, 1659.0,   134350.0, 14377000.0),
    (8.7312e12,   32.2379, 1905.6,   166030.0, 19127000.0),
]

ns       = np.array([r[0] for r in COHEN_DATA])
log_ns   = np.log(ns)
loglog_ns = np.log(log_ns)

def deviations():
    A = {}
    for k in range(1, 5):
        A[k] = []
        for row in COHEN_DATA:
            n, mu_k = row[0], row[k]
            expected = factorial(k) * (log(n) ** k)
            A[k].append(mu_k / expected - 1)
    return {k: np.array(v) for k, v in A.items()}

A = deviations()
absA = {k: np.abs(A[k]) for k in A}

# ─── Palette ─────────────────────────────────────────────────────────────────

BG      = "#0d0d14"
PANEL   = "#13131f"
BORDER  = "#1e1e30"
COLORS  = {1: "#ff6b6b", 2: "#ffd93d", 3: "#6bcb77", 4: "#4d96ff"}
LABELS  = {1: r"$k=1$  (mean)", 2: r"$k=2$  (transitional)", 
           3: r"$k=3$", 4: r"$k=4$"}
GREY    = "#444466"
WHITE   = "#e8e8f0"

plt.rcParams.update({
    "figure.facecolor":  BG,
    "axes.facecolor":    PANEL,
    "axes.edgecolor":    BORDER,
    "axes.labelcolor":   WHITE,
    "text.color":        WHITE,
    "xtick.color":       GREY,
    "ytick.color":       GREY,
    "grid.color":        BORDER,
    "grid.linewidth":    0.6,
    "font.family":       "monospace",
    "axes.spines.top":   False,
    "axes.spines.right": False,
})

# ─── Figure layout ───────────────────────────────────────────────────────────

fig = plt.figure(figsize=(18, 14), facecolor=BG)
gs  = gridspec.GridSpec(2, 3, figure=fig,
                        hspace=0.42, wspace=0.38,
                        left=0.06, right=0.97, top=0.91, bottom=0.07)

ax1 = fig.add_subplot(gs[0, :2])   # main: convergence curves  (wide)
ax2 = fig.add_subplot(gs[0, 2])    # convergence rates bar
ax3 = fig.add_subplot(gs[1, 0])    # signed deviations
ax4 = fig.add_subplot(gs[1, 1])    # rank heatmap
ax5 = fig.add_subplot(gs[1, 2])    # ratio portrait

fig.suptitle(
    "Reversed Convergence Hierarchy  ·  Prime Gap Moments  ·  Cohen (2024)",
    fontsize=13, color=WHITE, y=0.96, fontweight="bold"
)

x_label = r"$\log\log n$"

# ─── Plot 1: Main convergence curves ─────────────────────────────────────────

ax1.set_title("Relative Deviation from Exponential Asymptote  $|A_k(n)|$",
              fontsize=10, color=WHITE, pad=10)

# Reversal zone shading
reversal_start = loglog_ns[7]   # index 7: first YES
ax1.axvspan(reversal_start, loglog_ns[-1] + 0.05,
            color="#4d96ff", alpha=0.06, zorder=0)
ax1.axvline(reversal_start, color="#4d96ff", lw=0.8,
            linestyle="--", alpha=0.5, zorder=1)
ax1.text(reversal_start + 0.01, 0.295,
         "← reversal\n   regime", color="#4d96ff",
         fontsize=7.5, alpha=0.85, va="top")

for k in range(1, 5):
    lw   = 2.4 if k != 2 else 1.6
    ls   = "-"  if k != 2 else "--"
    ax1.plot(loglog_ns, absA[k],
             color=COLORS[k], lw=lw, ls=ls,
             marker="o", ms=4.5, markerfacecolor=COLORS[k],
             label=LABELS[k], zorder=3)

# Annotate final values
for k in range(1, 5):
    ax1.annotate(
        f"{absA[k][-1]:.4f}",
        xy=(loglog_ns[-1], absA[k][-1]),
        xytext=(8, 0), textcoords="offset points",
        color=COLORS[k], fontsize=8, va="center"
    )

ax1.axhline(0, color=GREY, lw=0.7, alpha=0.6)
ax1.set_xlabel(x_label, fontsize=9)
ax1.set_ylabel(r"$|A_k(n)|$", fontsize=9)
ax1.legend(loc="upper right", fontsize=8.5,
           facecolor=PANEL, edgecolor=BORDER, framealpha=0.9)
ax1.grid(True, axis="y", alpha=0.4)
ax1.set_xlim(loglog_ns[0] - 0.05, loglog_ns[-1] + 0.22)

# ─── Plot 2: Convergence rates bar chart ─────────────────────────────────────

ax2.set_title("Convergence Rate  $b_k$\n(slope vs $\\log\\log n$)",
              fontsize=10, color=WHITE, pad=10)

rates = {}
for k in range(1, 5):
    x0, xf = loglog_ns[0], loglog_ns[-1]
    rates[k] = (absA[k][-1] - absA[k][0]) / (xf - x0)

ks     = list(rates.keys())
rvals  = [rates[k] for k in ks]
colors = [COLORS[k] for k in ks]
hatches = [None, "///", None, None]

bars = ax2.barh(ks, rvals, color=colors, height=0.55,
                edgecolor=BORDER, linewidth=0.8)
for bar, h in zip(bars, hatches):
    if h:
        bar.set_hatch(h)
        bar.set_edgecolor("#ffd93d")

ax2.axvline(0, color=WHITE, lw=1.0, alpha=0.5)
ax2.set_xlabel("Rate  (× $10^{-2}$)", fontsize=9)
ax2.set_yticks(ks)
ax2.set_yticklabels([f"k = {k}" for k in ks], fontsize=9)
rate_ticks = ax2.get_xticks()
ax2.set_xticks(rate_ticks)
ax2.set_xticklabels([f"{v*100:.1f}" for v in rate_ticks], fontsize=8)

for k, v in rates.items():
    ax2.text(v + (0.002 if v >= 0 else -0.002),
             k,
             f"{v:.4f}",
             va="center",
             ha="left" if v >= 0 else "right",
             color=COLORS[k], fontsize=8)

ax2.text(0.02, 2, "diverging →", color=COLORS[2],
         fontsize=7.5, transform=ax2.get_yaxis_transform(), alpha=0.8)
ax2.grid(True, axis="x", alpha=0.35)

# ─── Plot 3: Signed deviations ────────────────────────────────────────────────

ax3.set_title("Signed Deviation  $A_k(n)$", fontsize=10, color=WHITE, pad=10)

for k in range(1, 5):
    lw = 2.2 if k != 2 else 1.4
    ls = "-"  if k != 2 else "--"
    ax3.plot(loglog_ns, A[k],
             color=COLORS[k], lw=lw, ls=ls,
             marker="o", ms=3.5, label=LABELS[k])

ax3.axhline(0, color=WHITE, lw=1.0, alpha=0.7, linestyle=":")
ax3.fill_between(loglog_ns, 0, 0.35, color="#ffffff", alpha=0.02)
ax3.set_xlabel(x_label, fontsize=9)
ax3.set_ylabel(r"$A_k(n)$", fontsize=9)
ax3.text(loglog_ns[0] + 0.02, 0.01,
         "all positive\n→ persistent overestimate",
         fontsize=7, color=GREY, alpha=0.9, va="bottom")
ax3.legend(fontsize=7.5, facecolor=PANEL, edgecolor=BORDER)
ax3.grid(True, alpha=0.35)

# ─── Plot 4: Rank heatmap ─────────────────────────────────────────────────────

ax4.set_title("Rank of $|A_k|$ at each scale\n(1 = smallest deviation)",
              fontsize=10, color=WHITE, pad=10)

n_scales = len(COHEN_DATA)
rank_matrix = np.zeros((4, n_scales))

for i in range(n_scales):
    vals = [(absA[k][i], k) for k in range(1, 5)]
    vals_sorted = sorted(vals)
    for rank, (_, k) in enumerate(vals_sorted, start=1):
        rank_matrix[k-1, i] = rank

cmap = LinearSegmentedColormap.from_list(
    "rank", ["#4d96ff", "#6bcb77", "#ffd93d", "#ff6b6b"])
im = ax4.imshow(rank_matrix, aspect="auto", cmap=cmap,
                vmin=1, vmax=4, interpolation="nearest")

ax4.set_yticks([0, 1, 2, 3])
ax4.set_yticklabels(["k=1", "k=2", "k=3", "k=4"], fontsize=9)
ax4.set_xticks(range(n_scales))
ax4.set_xticklabels(
    [f"{r[0]:.0e}".replace("e+0", "e").replace("e+", "e") for r in COHEN_DATA],
    rotation=60, ha="right", fontsize=7)

for i in range(n_scales):
    for j in range(4):
        ax4.text(i, j, str(int(rank_matrix[j, i])),
                 ha="center", va="center",
                 fontsize=9, color=BG, fontweight="bold")

ax4.axvline(6.5, color=WHITE, lw=1.2, alpha=0.6, linestyle="--")
ax4.text(6.6, -0.55, "reversal →", fontsize=7.5,
         color=WHITE, alpha=0.7, va="bottom")

cb = fig.colorbar(im, ax=ax4, fraction=0.046, pad=0.04)
cb.set_ticks([1, 2, 3, 4])
cb.set_label("Rank", fontsize=8, color=WHITE)
cb.ax.yaxis.set_tick_params(color=WHITE, labelcolor=WHITE, labelsize=8)

# ─── Plot 5: Ratio portrait k4/k1 ────────────────────────────────────────────

ax5.set_title(r"Ratio  $|A_4| \,/\, |A_1|$" + "\n(hierarchy strength)",
              fontsize=10, color=WHITE, pad=10)

ratio = absA[4] / absA[1]

ax5.fill_between(loglog_ns, ratio, 1.0,
                 where=(ratio < 1.0), alpha=0.15,
                 color="#4d96ff", label="reversed regime")
ax5.plot(loglog_ns, ratio,
         color="#4d96ff", lw=2.5, marker="o", ms=5)
ax5.axhline(1.0, color=WHITE, lw=1.0, linestyle=":", alpha=0.7,
            label=r"$|A_4| = |A_1|$")

# Annotate crossover
cross_idx = next(i for i, r in enumerate(ratio) if r < 1.0)
ax5.annotate("hierarchy\nemerges",
             xy=(loglog_ns[cross_idx], ratio[cross_idx]),
             xytext=(loglog_ns[cross_idx] - 0.15, ratio[cross_idx] + 0.18),
             arrowprops=dict(arrowstyle="->", color=WHITE, lw=0.9),
             color=WHITE, fontsize=8, ha="center")

ax5.set_xlabel(x_label, fontsize=9)
ax5.set_ylabel(r"$|A_4| / |A_1|$", fontsize=9)
ax5.legend(fontsize=8, facecolor=PANEL, edgecolor=BORDER)
ax5.grid(True, alpha=0.35)

# ─── Save ─────────────────────────────────────────────────────────────────────

parser = argparse.ArgumentParser(
    description="Render the prime gap moments hierarchy figure."
)
parser.add_argument(
    "--out",
    default=str(Path(__file__).with_name("prime_gap_moments.png")),
    help="Output PNG path. Parent directories are created automatically.",
)
args = parser.parse_args()

out_path = Path(args.out).expanduser()
out_path.parent.mkdir(parents=True, exist_ok=True)

plt.savefig(out_path, dpi=180, bbox_inches="tight", facecolor=BG)
print(f"Saved -> {out_path}")
