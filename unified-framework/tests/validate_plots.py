#!/usr/bin/env python3
"""
Plot Validation and Summary
==========================

Validates all generated plots and provides comprehensive summary.
"""

import os
from pathlib import Path
import json
from datetime import datetime

def validate_plots():
    """Validate and summarize all generated plots."""
    
    plots_dir = Path("tests/plots")
    
    # Count plots by type and category
    plot_summary = {
        'total_plots': 0,
        'interactive_plots': 0,
        'static_plots': 0,
        'categories': {},
        'file_types': {},
        'validation_time': datetime.now().isoformat()
    }
    
    print("🔍 PLOT VALIDATION AND SUMMARY")
    print("=" * 50)
    
    # Scan all plot files
    for root, dirs, files in os.walk(plots_dir):
        for file in files:
            if file.endswith(('.png', '.html', '.jpg', '.jpeg', '.svg')):
                if file == 'index.html':
                    continue
                    
                full_path = Path(root) / file
                rel_path = full_path.relative_to(plots_dir)
                
                # Get category (subdirectory)
                if len(rel_path.parts) > 1:
                    category = rel_path.parts[0]
                else:
                    category = 'root'
                
                # Get file type
                file_ext = file.split('.')[-1].lower()
                
                # Update counters
                plot_summary['total_plots'] += 1
                
                if file_ext == 'html':
                    plot_summary['interactive_plots'] += 1
                else:
                    plot_summary['static_plots'] += 1
                
                # Category counter
                if category not in plot_summary['categories']:
                    plot_summary['categories'][category] = {'total': 0, 'interactive': 0, 'static': 0}
                
                plot_summary['categories'][category]['total'] += 1
                if file_ext == 'html':
                    plot_summary['categories'][category]['interactive'] += 1
                else:
                    plot_summary['categories'][category]['static'] += 1
                
                # File type counter
                if file_ext not in plot_summary['file_types']:
                    plot_summary['file_types'][file_ext] = 0
                plot_summary['file_types'][file_ext] += 1
    
    # Print summary
    print(f"📊 Total Plots Generated: {plot_summary['total_plots']}")
    print(f"🌐 Interactive Plots (HTML): {plot_summary['interactive_plots']}")
    print(f"🖼️  Static Plots (PNG/etc): {plot_summary['static_plots']}")
    print()
    
    print("📁 BY CATEGORY:")
    for category, counts in sorted(plot_summary['categories'].items()):
        print(f"   {category:25} | Total: {counts['total']:2d} | Interactive: {counts['interactive']:2d} | Static: {counts['static']:2d}")
    
    print()
    print("🗂️  BY FILE TYPE:")
    for file_type, count in sorted(plot_summary['file_types'].items()):
        print(f"   .{file_type:10} {count:3d} files")
    
    # Save summary to JSON
    summary_file = plots_dir / 'validation_summary.json'
    with open(summary_file, 'w') as f:
        json.dump(plot_summary, f, indent=2)
    
    print(f"\n💾 Validation summary saved to: {summary_file}")
    
    # Check for expected key plots
    expected_plots = [
        'z5d_comprehensive_summary.png',
        'interactive_3d/interactive_helix_main.html', 
        'z5d_enhanced/parameter_space_3d_interactive.html',
        'comprehensive_3d/helical_embeddings/prime_helix_3d_k_0.3.html',
        'topology_suite/3d_helical_embedding.html'
    ]
    
    print("\n✅ KEY PLOT VALIDATION:")
    missing_plots = []
    for expected in expected_plots:
        plot_path = plots_dir / expected
        if plot_path.exists():
            print(f"   ✅ {expected}")
        else:
            print(f"   ❌ {expected}")
            missing_plots.append(expected)
    
    if missing_plots:
        print(f"\n⚠️  Missing {len(missing_plots)} expected plots")
    else:
        print("\n🎉 All key plots validated successfully!")
    
    return plot_summary

def generate_readme():
    """Generate README for plots directory."""
    
    plots_dir = Path("tests/plots")
    readme_file = plots_dir / "README.md"
    
    readme_content = f"""# Unified Framework - Comprehensive Plot Gallery

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

This directory contains copious 2D and 3D plots for all testing components of the Unified Framework, as requested in issue #317. The plots are organized into logical categories for easy navigation.

## Quick Access

- **🌐 Browse All Plots**: Open [`index.html`](index.html) for a comprehensive web gallery
- **📊 Plot Statistics**: See [`validation_summary.json`](validation_summary.json) for detailed metrics

## Plot Categories

### Core Analysis
- **root/**: Core Z5D scientific testbed results
- **z5d_analysis/**: Z5D predictor validation plots
- **z5d_enhanced/**: Enhanced Z5D visualization suite

### 3D Visualizations  
- **interactive_3d/**: Interactive 3D helix visualizations
- **comprehensive_3d/**: Comprehensive 3D mathematical visualizations
  - `helical_embeddings/`: Prime helical embeddings
  - `riemann_zeta/`: Riemann zeta zero visualizations
  - `prime_distributions/`: Prime distribution analysis
  - `modular_topology/`: Modular arithmetic topology
  - `physical_discrete/`: Physical-discrete bridge visualizations

### Advanced Analysis
- **topology_suite/**: Modular topology analysis
- **geodesic_mapping/**: Geodesic mapping and density enhancement
- **statistical_analysis/**: Statistical correlations and distributions
- **performance_benchmarks/**: Performance comparison analysis

## Plot Types

### Interactive Plots (HTML)
- 3D surface plots with rotation and zoom
- Parameter sweep animations
- Quantum correlation analysis
- Interactive scatter plots with hover information

### Static Plots (PNG)
- High-quality publication-ready figures
- Statistical analysis charts
- Comparative performance plots
- Error analysis visualizations

## Technical Details

### Visualization Technologies
- **matplotlib**: High-quality static plots with scientific styling
- **plotly**: Interactive 3D visualizations with web interface
- **seaborn**: Statistical visualization enhancements

### Mathematical Components Visualized
- Z5D predictor accuracy and convergence analysis
- Prime helical embeddings with quantum correlations  
- Riemann zeta zero distributions in 3D space
- Modular arithmetic topology on toroidal surfaces
- Physical-discrete domain bridging visualizations
- Geodesic curvature and density enhancement analysis

### Data Sources
- Z Framework discrete predictor results
- Prime number sequences and gap analysis
- Riemann zeta function computational results
- Modular arithmetic pattern analysis
- Physical constants mapping to discrete domains

## Usage

1. **Web Gallery**: Open `index.html` in a web browser for organized access
2. **Direct Access**: Navigate to category subdirectories for specific plot types
3. **Interactive Plots**: HTML files can be opened directly in web browsers
4. **Static Plots**: PNG files suitable for presentations and publications

## Reproducibility

All plots are generated by automated scripts in the `tests/` directory:
- `generate_all_plots.py`: Main orchestrator for all plot generation
- `test_z5d_enhanced_visualizations.py`: Enhanced Z5D analysis plots
- `test_comprehensive_3d_visualizations.py`: 3D mathematical visualizations
- `generate_plot_index.py`: Web gallery index generation

Run any of these scripts to regenerate the corresponding plots.

---

*This comprehensive visualization suite demonstrates the mathematical rigor and empirical validation capabilities of the Unified Framework across multiple domains of analysis.*
"""
    
    with open(readme_file, 'w') as f:
        f.write(readme_content)
    
    print(f"📝 README generated: {readme_file}")

if __name__ == "__main__":
    summary = validate_plots()
    generate_readme()
    
    print(f"\n🎨 COMPREHENSIVE PLOT GENERATION COMPLETE!")
    print(f"   📊 {summary['total_plots']} total plots generated")
    print(f"   🌐 {summary['interactive_plots']} interactive visualizations")
    print(f"   🖼️  {summary['static_plots']} static plots")
    print(f"   📁 {len(summary['categories'])} organized categories")
    print(f"   🌐 Web gallery: tests/plots/index.html")