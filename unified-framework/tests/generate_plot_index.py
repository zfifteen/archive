#!/usr/bin/env python3
"""
Plot Index Generator
===================

Creates an HTML index of all generated plots for easy browsing.
"""

import os
from pathlib import Path
import json
from datetime import datetime

def generate_plot_index():
    """Generate an HTML index of all plots."""
    
    plots_dir = Path("tests/plots")
    index_file = plots_dir / "index.html"
    
    # Scan for all plot files
    plot_files = []
    for root, dirs, files in os.walk(plots_dir):
        for file in files:
            if file.endswith(('.png', '.html', '.jpg', '.jpeg', '.svg')):
                rel_path = os.path.relpath(os.path.join(root, file), plots_dir)
                plot_files.append(rel_path)
    
    # Group by directory
    plot_groups = {}
    for plot_file in sorted(plot_files):
        if plot_file == "index.html":
            continue
            
        parts = plot_file.split(os.sep)
        if len(parts) > 1:
            group = parts[0]
            filename = "/".join(parts[1:])
        else:
            group = "root"
            filename = plot_file
        
        if group not in plot_groups:
            plot_groups[group] = []
        plot_groups[group].append(filename)
    
    # Generate HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unified Framework - Plot Gallery</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        
        .subtitle {{
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 30px;
            font-style: italic;
        }}
        
        .stats {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .stat-item {{
            display: inline-block;
            margin: 0 20px;
            padding: 10px;
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
        }}
        
        .stat-label {{
            font-size: 0.9em;
            color: #7f8c8d;
            text-transform: uppercase;
        }}
        
        .plot-group {{
            margin-bottom: 40px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .group-header {{
            background: #3498db;
            color: white;
            padding: 15px 20px;
            margin: 0;
            font-size: 1.3em;
            font-weight: bold;
        }}
        
        .group-content {{
            padding: 20px;
        }}
        
        .plot-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .plot-item {{
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            background: #fafafa;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .plot-item:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .plot-title {{
            font-weight: bold;
            margin-bottom: 10px;
            color: #2c3e50;
        }}
        
        .plot-type {{
            font-size: 0.8em;
            color: #7f8c8d;
            text-transform: uppercase;
            margin-bottom: 10px;
        }}
        
        .plot-link {{
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 4px;
            transition: background 0.2s;
        }}
        
        .plot-link:hover {{
            background: #2980b9;
        }}
        
        .interactive-badge {{
            background: #e74c3c;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.7em;
            margin-left: 10px;
        }}
        
        .static-badge {{
            background: #27ae60;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.7em;
            margin-left: 10px;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            color: #7f8c8d;
        }}
        
        .description {{
            background: #e8f6ff;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            border-left: 4px solid #3498db;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Unified Framework Plot Gallery</h1>
        <p class="subtitle">Comprehensive 2D and 3D Visualizations for Mathematical Analysis</p>
        
        <div class="description">
            <strong>About this Gallery:</strong> This collection contains copious 2D and 3D plots generated 
            for all testing components of the Unified Framework, including Z5D predictor analysis, 
            interactive 3D helical visualizations, modular topology analysis, geodesic mapping, 
            and cross-domain physical-discrete connections.
        </div>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{len(plot_files)}</div>
                <div class="stat-label">Total Plots</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{len(plot_groups)}</div>
                <div class="stat-label">Categories</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{len([f for f in plot_files if f.endswith('.html')])}</div>
                <div class="stat-label">Interactive</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{len([f for f in plot_files if f.endswith('.png')])}</div>
                <div class="stat-label">Static</div>
            </div>
        </div>
"""
    
    # Add each plot group
    group_descriptions = {
        "root": "Core Z5D Analysis",
        "z5d_analysis": "Z5D Scientific Test Bed Results",
        "z5d_enhanced": "Enhanced Z5D Visualization Suite",
        "comprehensive_3d": "Comprehensive 3D Mathematical Visualizations",
        "interactive_3d": "Interactive 3D Helix Visualizations",
        "topology_suite": "Modular Topology Analysis",
        "geodesic_mapping": "Geodesic Mapping and Density Enhancement",
        "statistical_analysis": "Statistical Analysis and Correlations",
        "performance_benchmarks": "Performance Benchmark Analysis",
        "numerical_validation": "Numerical Validation and Stability"
    }
    
    for group, files in plot_groups.items():
        description = group_descriptions.get(group, group.replace('_', ' ').title())
        
        html_content += f"""
        <div class="plot-group">
            <h2 class="group-header">{description}</h2>
            <div class="group-content">
                <div class="plot-grid">
"""
        
        for filename in sorted(files):
            plot_title = filename.replace('_', ' ').replace('.png', '').replace('.html', '').title()
            file_ext = filename.split('.')[-1].lower()
            
            if file_ext == 'html':
                plot_type = "Interactive"
                badge = '<span class="interactive-badge">Interactive</span>'
            else:
                plot_type = "Static"
                badge = '<span class="static-badge">Static</span>'
            
            if group == "root":
                file_path = filename
            else:
                file_path = f"{group}/{filename}"
            
            html_content += f"""
                    <div class="plot-item">
                        <div class="plot-title">{plot_title}{badge}</div>
                        <div class="plot-type">{file_ext.upper()} File</div>
                        <a href="{file_path}" class="plot-link" target="_blank">View Plot</a>
                    </div>
"""
        
        html_content += """
                </div>
            </div>
        </div>
"""
    
    # Footer
    html_content += f"""
        <div class="footer">
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Unified Framework - Comprehensive Mathematical Visualization Suite</p>
        </div>
    </div>
</body>
</html>"""
    
    # Write the index file
    with open(index_file, 'w') as f:
        f.write(html_content)
    
    print(f"📝 Plot index generated: {index_file}")
    print(f"📊 Total plots indexed: {len(plot_files)}")
    print(f"🗂️  Categories: {len(plot_groups)}")

if __name__ == "__main__":
    generate_plot_index()