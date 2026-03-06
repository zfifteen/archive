import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
from statsmodels.tsa.stattools import acf
import os

# Set up plotting style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def plot_distribution_comparison(real_data, synthetic_data_dict, save_path=None):
    """Plot histogram overlays of real vs synthetic distributions"""
    plt.figure(figsize=(12, 8))

    # Plot real data
    plt.hist(real_data, bins=50, alpha=0.7, density=True, label='Real Prime Gaps',
             color='black', edgecolor='black', linewidth=1.5)

    colors = plt.cm.tab10(np.linspace(0, 1, len(synthetic_data_dict)))

    for i, (model_name, synth_data) in enumerate(synthetic_data_dict.items()):
        plt.hist(synth_data, bins=50, alpha=0.5, density=True,
                label=model_name, color=colors[i])

    plt.xlabel('Log Gap Value')
    plt.ylabel('Density')
    plt.title('Distribution Comparison: Real vs Synthetic Models')
    plt.legend()
    plt.grid(True, alpha=0.3)

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def plot_acf_comparison(real_data, synthetic_data_dict, max_lag=20, save_path=None):
    """Plot ACF comparison for real vs synthetic data"""
    n_models = len(synthetic_data_dict)
    n_cols = 3
    n_rows = (n_models + 1 + n_cols - 1) // n_cols  # +1 for real data

    plt.figure(figsize=(15, 5 * n_rows))

    real_acf = acf(real_data, nlags=max_lag, fft=True)

    plt.subplot(n_rows, n_cols, 1)
    plt.bar(range(max_lag+1), real_acf, color='black', alpha=0.7)
    plt.title('Real Prime Gaps ACF')
    plt.xlabel('Lag')
    plt.ylabel('ACF')
    plt.grid(True, alpha=0.3)

    colors = plt.cm.tab10(np.linspace(0, 1, n_models))

    for i, (model_name, synth_data) in enumerate(synthetic_data_dict.items()):
        plt.subplot(n_rows, n_cols, i+2)
        synth_acf = acf(synth_data, nlags=max_lag, fft=True)
        plt.bar(range(max_lag+1), synth_acf, color=colors[i], alpha=0.7)
        plt.title(f'{model_name} ACF')
        plt.xlabel('Lag')
        plt.ylabel('ACF')
        plt.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def plot_qq_comparison(real_data, synthetic_data_dict, save_path=None):
    """Plot QQ-plots for each synthetic model vs real data"""
    n_models = len(synthetic_data_dict)
    n_cols = 3
    n_rows = (n_models + n_cols - 1) // n_cols

    plt.figure(figsize=(15, 5 * n_rows))

    colors = plt.cm.tab10(np.linspace(0, 1, n_models))

    for i, (model_name, synth_data) in enumerate(synthetic_data_dict.items()):
        plt.subplot(n_rows, n_cols, i+1)

        # QQ plot
        real_sorted = np.sort(real_data)
        synth_sorted = np.sort(synth_data)

        # Ensure same length
        min_len = min(len(real_sorted), len(synth_sorted))
        real_sorted = real_sorted[:min_len]
        synth_sorted = synth_sorted[:min_len]

        plt.scatter(real_sorted, synth_sorted, alpha=0.6, color=colors[i], s=1)
        plt.plot([real_sorted.min(), real_sorted.max()],
                [real_sorted.min(), real_sorted.max()],
                'k--', alpha=0.7)

        plt.xlabel('Real Quantiles')
        plt.ylabel('Synthetic Quantiles')
        plt.title(f'QQ Plot: {model_name}')
        plt.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def plot_model_ranking(results_list, save_path=None):
    """Plot bar chart of model performance metrics"""
    models = [r['model'] for r in results_list]
    d_ks = [r['d_ks'] for r in results_list]
    acf_errors = [r['acf_error'] for r in results_list]

    x = np.arange(len(models))
    width = 0.35

    plt.figure(figsize=(12, 6))

    plt.bar(x - width/2, d_ks, width, label='KS Distance', alpha=0.8, color='skyblue')
    plt.bar(x + width/2, acf_errors, width, label='ACF Error', alpha=0.8, color='lightcoral')

    plt.xlabel('Models')
    plt.ylabel('Error Metrics')
    plt.title('Model Performance Comparison')
    plt.xticks(x, models, rotation=45, ha='right')
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')

    # Add value labels
    for i, v in enumerate(d_ks):
        plt.text(i - width/2, v + 0.01, f'{v:.3f}', ha='center', va='bottom', fontsize=8)
    for i, v in enumerate(acf_errors):
        plt.text(i + width/2, v + 0.01, f'{v:.3f}', ha='center', va='bottom', fontsize=8)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def plot_parameter_sensitivity(model, param_ranges, target_stats, save_path=None):
    """Plot parameter sensitivity heatmap (simplified example)"""
    # This is a placeholder - would need actual sensitivity analysis
    plt.figure(figsize=(8, 6))
    plt.text(0.5, 0.5, 'Parameter Sensitivity Analysis\n(Not implemented in this version)',
            ha='center', va='center', fontsize=14)
    plt.axis('off')

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def create_all_plots(real_data, synthetic_data_dict, results_list, output_dir):
    """Create all comparison plots"""
    os.makedirs(output_dir, exist_ok=True)

    plot_distribution_comparison(
        real_data, synthetic_data_dict,
        save_path=os.path.join(output_dir, 'distribution_comparison.png')
    )

    plot_acf_comparison(
        real_data, synthetic_data_dict,
        save_path=os.path.join(output_dir, 'acf_comparison.png')
    )

    plot_qq_comparison(
        real_data, synthetic_data_dict,
        save_path=os.path.join(output_dir, 'qq_plots.png')
    )

    plot_model_ranking(
        results_list,
        save_path=os.path.join(output_dir, 'model_ranking.png')
    )

    # Parameter sensitivity (placeholder)
    plot_parameter_sensitivity(
        None, None, None,
        save_path=os.path.join(output_dir, 'parameter_sensitivity.png')
    )
