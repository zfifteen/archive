#!/usr/bin/env python3
"""
Prime Geodesic Visualization Web Interface

Interactive 3D web-based visualization system for modular geodesic spirals
with color-mapping for density enhancement and clustering analysis.

Features:
- Interactive 3D visualization using Plotly
- Real-time color-mapping based on density enhancement
- Prime cluster highlighting and analysis
- Search interface for specific patterns
- Export functionality for visualizations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify, send_file
import plotly.graph_objects as go
import plotly.express as px
import plotly.offline as pyo
import numpy as np
import json
from typing import Dict, List, Any, Optional
import io
import base64

from applications.prime_geodesic_search import PrimeGeodesicSearchEngine, GeodesicPoint

app = Flask(__name__)


class PrimeGeodesicVisualizer:
    """
    Web-based visualization system for prime geodesic spirals.
    
    Provides interactive 3D visualizations with color-mapping, clustering analysis,
    and real-time search capabilities for mathematical research and exploration.
    """
    
    def __init__(self):
        self.engine = PrimeGeodesicSearchEngine(k_optimal=0.3)
        self.current_points: List[GeodesicPoint] = []
        self.current_clusters: List[List[GeodesicPoint]] = []
        
    def create_3d_spiral_visualization(self, points: List[GeodesicPoint], 
                                     color_by: str = 'density_enhancement',
                                     show_clusters: bool = True) -> str:
        """
        Create interactive 3D spiral visualization.
        
        Args:
            points: List of GeodesicPoint objects to visualize
            color_by: Color mapping criteria ('density_enhancement', 'curvature', 'prime_status')
            show_clusters: Whether to highlight prime clusters
            
        Returns:
            HTML string for the interactive plot
        """
        if not points:
            return self._create_empty_plot()
        
        # Extract coordinates and metadata
        x_coords = [p.coordinates_3d[0] for p in points]
        y_coords = [p.coordinates_3d[1] for p in points]
        z_coords = [p.coordinates_3d[2] for p in points]
        
        # Determine color mapping
        if color_by == 'density_enhancement':
            colors = [p.density_enhancement for p in points]
            colorscale = 'Viridis'
            color_label = 'Density Enhancement (%)'
        elif color_by == 'curvature':
            colors = [p.curvature for p in points]
            colorscale = 'Plasma'
            color_label = 'Geodesic Curvature'
        elif color_by == 'prime_status':
            colors = [1 if p.is_prime else 0 for p in points]
            colorscale = [[0, 'blue'], [1, 'red']]
            color_label = 'Prime Status'
        else:
            colors = [p.n for p in points]
            colorscale = 'Cividis'
            color_label = 'Integer Value'
        
        # Create hover text with detailed information
        hover_text = []
        for p in points:
            text = (
                f"n = {p.n}<br>"
                f"Prime: {p.is_prime}<br>"
                f"Curvature: {p.curvature:.4f}<br>"
                f"Density Enhancement: {p.density_enhancement:.2f}%<br>"
                f"Type: {p.geodesic_type}<br>"
                f"3D: ({p.coordinates_3d[0]:.3f}, {p.coordinates_3d[1]:.3f}, {p.coordinates_3d[2]:.3f})"
            )
            hover_text.append(text)
        
        # Create main scatter plot
        fig = go.Figure()
        
        # Add main spiral points
        fig.add_trace(go.Scatter3d(
            x=x_coords,
            y=y_coords,
            z=z_coords,
            mode='markers',
            marker=dict(
                size=[8 if p.is_prime else 5 for p in points],
                color=colors,
                colorscale=colorscale,
                colorbar=dict(title=color_label),
                opacity=0.8,
                symbol=['cross' if p.is_prime else 'circle' for p in points]
            ),
            text=[str(p.n) for p in points],
            hovertext=hover_text,
            hoverinfo='text',
            name='Geodesic Spiral'
        ))
        
        # Add cluster highlights if requested
        if show_clusters and self.current_clusters:
            cluster_colors = px.colors.qualitative.Set1
            for i, cluster in enumerate(self.current_clusters):
                if cluster:  # Non-empty cluster
                    cluster_x = [p.coordinates_3d[0] for p in cluster]
                    cluster_y = [p.coordinates_3d[1] for p in cluster]
                    cluster_z = [p.coordinates_3d[2] for p in cluster]
                    
                    fig.add_trace(go.Scatter3d(
                        x=cluster_x,
                        y=cluster_y,
                        z=cluster_z,
                        mode='markers',
                        marker=dict(
                            size=12,
                            color=cluster_colors[i % len(cluster_colors)],
                            symbol='cross',
                            opacity=0.9,
                            line=dict(width=2, color='black')
                        ),
                        name=f'Prime Cluster {i+1}',
                        hovertext=[f"Cluster {i+1}: n={p.n}" for p in cluster],
                        hoverinfo='text'
                    ))
        
        # Update layout for better visualization
        fig.update_layout(
            title={
                'text': f'Prime Geodesic Spiral Visualization (k* = {self.engine.k_optimal})',
                'x': 0.5,
                'xanchor': 'center'
            },
            scene=dict(
                xaxis_title='X (Geodesic)',
                yaxis_title='Y (Geodesic)',
                zaxis_title='Z (Curvature)',
                camera=dict(
                    up=dict(x=0, y=0, z=1),
                    center=dict(x=0, y=0, z=0),
                    eye=dict(x=1.5, y=1.5, z=1.5)
                ),
                aspectmode='cube'
            ),
            width=1000,
            height=700,
            hovermode='closest'
        )
        
        # Convert to HTML
        return pyo.plot(fig, output_type='div', include_plotlyjs=True)
    
    def create_density_heatmap(self, points: List[GeodesicPoint]) -> str:
        """
        Create 2D density heatmap showing enhancement patterns.
        """
        if not points:
            return self._create_empty_plot()
        
        # Project 3D coordinates to 2D for heatmap
        x_coords = [p.coordinates_3d[0] for p in points]
        y_coords = [p.coordinates_3d[1] for p in points]
        densities = [p.density_enhancement for p in points]
        
        fig = go.Figure()
        
        # Create scatter plot with density color mapping
        fig.add_trace(go.Scatter(
            x=x_coords,
            y=y_coords,
            mode='markers',
            marker=dict(
                size=[10 if p.is_prime else 6 for p in points],
                color=densities,
                colorscale='Hot',
                colorbar=dict(title='Density Enhancement (%)'),
                opacity=0.7,
                symbol=['cross' if p.is_prime else 'circle' for p in points]
            ),
            text=[f"n={p.n}, Prime: {p.is_prime}" for p in points],
            hoverinfo='text',
            name='Density Mapping'
        ))
        
        fig.update_layout(
            title='Prime Density Enhancement Heatmap',
            xaxis_title='X Coordinate',
            yaxis_title='Y Coordinate',
            width=800,
            height=600
        )
        
        return pyo.plot(fig, output_type='div', include_plotlyjs=True)
    
    def create_curvature_analysis_plot(self, points: List[GeodesicPoint]) -> str:
        """
        Create curvature analysis plot comparing primes vs composites.
        """
        if not points:
            return self._create_empty_plot()
        
        primes = [p for p in points if p.is_prime]
        composites = [p for p in points if not p.is_prime]
        
        fig = go.Figure()
        
        # Add prime curvature distribution
        if primes:
            fig.add_trace(go.Histogram(
                x=[p.curvature for p in primes],
                name='Primes',
                opacity=0.7,
                nbinsx=20,
                marker_color='red'
            ))
        
        # Add composite curvature distribution
        if composites:
            fig.add_trace(go.Histogram(
                x=[p.curvature for p in composites],
                name='Composites',
                opacity=0.7,
                nbinsx=20,
                marker_color='blue'
            ))
        
        fig.update_layout(
            title='Curvature Distribution: Primes vs Composites',
            xaxis_title='Geodesic Curvature',
            yaxis_title='Count',
            barmode='overlay',
            width=800,
            height=500
        )
        
        return pyo.plot(fig, output_type='div', include_plotlyjs=True)
    
    def _create_empty_plot(self) -> str:
        """Create empty plot placeholder."""
        fig = go.Figure()
        fig.add_annotation(
            text="No data to display. Generate coordinates first.",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            title="Prime Geodesic Visualization",
            width=800,
            height=600
        )
        return pyo.plot(fig, output_type='div', include_plotlyjs=True)


# Global visualizer instance
visualizer = PrimeGeodesicVisualizer()


@app.route('/')
def index():
    """Main page with visualization interface."""
    return render_template('index.html')


@app.route('/api/generate_coordinates', methods=['POST'])
def generate_coordinates():
    """API endpoint to generate geodesic coordinates."""
    try:
        data = request.get_json()
        start = data.get('start', 2)
        end = data.get('end', 102)
        step = data.get('step', 1)
        
        # Validate input
        if end - start > 1000:
            return jsonify({'error': 'Range too large. Maximum 1000 points.'}), 400
        
        # Generate coordinates
        points = visualizer.engine.generate_sequence_coordinates(start, end, step)
        visualizer.current_points = points
        
        # Find clusters
        visualizer.current_clusters = visualizer.engine.search_prime_clusters(
            points, eps=0.2, min_samples=3
        )
        
        # Return summary information
        result = {
            'success': True,
            'total_points': len(points),
            'prime_count': len([p for p in points if p.is_prime]),
            'cluster_count': len(visualizer.current_clusters),
            'range': {'start': start, 'end': end, 'step': step}
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/visualize', methods=['POST'])
def visualize():
    """API endpoint to create visualization."""
    try:
        data = request.get_json()
        viz_type = data.get('type', '3d_spiral')
        color_by = data.get('color_by', 'density_enhancement')
        show_clusters = data.get('show_clusters', True)
        
        if not visualizer.current_points:
            return jsonify({'error': 'No data available. Generate coordinates first.'}), 400
        
        if viz_type == '3d_spiral':
            plot_html = visualizer.create_3d_spiral_visualization(
                visualizer.current_points, color_by, show_clusters
            )
        elif viz_type == 'density_heatmap':
            plot_html = visualizer.create_density_heatmap(visualizer.current_points)
        elif viz_type == 'curvature_analysis':
            plot_html = visualizer.create_curvature_analysis_plot(visualizer.current_points)
        else:
            return jsonify({'error': 'Unknown visualization type'}), 400
        
        return jsonify({
            'success': True,
            'plot_html': plot_html
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/search', methods=['POST'])
def search():
    """API endpoint for advanced search functionality."""
    try:
        data = request.get_json()
        criteria = data.get('criteria', {})
        
        if not visualizer.current_points:
            return jsonify({'error': 'No data available. Generate coordinates first.'}), 400
        
        # Apply search on current points
        filtered_points = []
        for point in visualizer.current_points:
            matches = True
            
            # Apply filters
            if criteria.get('primes_only', False) and not point.is_prime:
                matches = False
            
            if 'curvature_min' in criteria and point.curvature < criteria['curvature_min']:
                matches = False
                
            if 'curvature_max' in criteria and point.curvature > criteria['curvature_max']:
                matches = False
            
            if 'density_min' in criteria and point.density_enhancement < criteria['density_min']:
                matches = False
            
            if matches:
                filtered_points.append(point)
        
        # Update current points for visualization
        visualizer.current_points = filtered_points
        
        return jsonify({
            'success': True,
            'total_found': len(filtered_points),
            'prime_count': len([p for p in filtered_points if p.is_prime]),
            'criteria': criteria
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export', methods=['POST'])
def export_data():
    """API endpoint to export current data."""
    try:
        data = request.get_json()
        format_type = data.get('format', 'csv')
        filename = data.get('filename', 'geodesic_export')
        
        if not visualizer.current_points:
            return jsonify({'error': 'No data available to export.'}), 400
        
        # Export data
        file_path = visualizer.engine.export_coordinates(
            visualizer.current_points, filename, format_type
        )
        
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/statistics')
def get_statistics():
    """API endpoint to get statistical analysis."""
    try:
        if not visualizer.current_points:
            return jsonify({'error': 'No data available.'}), 400
        
        # Generate comprehensive statistics
        report = visualizer.engine.generate_statistical_report(visualizer.current_points)
        
        # Add cluster information
        report['clustering'] = {
            'cluster_count': len(visualizer.current_clusters),
            'clustered_primes': sum(len(cluster) for cluster in visualizer.current_clusters),
            'clusters': [
                {
                    'id': i,
                    'size': len(cluster),
                    'primes': [p.n for p in cluster]
                }
                for i, cluster in enumerate(visualizer.current_clusters)
            ]
        }
        
        return jsonify({
            'success': True,
            'statistics': report
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Create templates directory and HTML template
def create_template():
    """Create the HTML template for the web interface."""
    import os
    
    # Create templates directory if it doesn't exist
    template_dir = os.path.join(app.root_path, 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    # HTML template content
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prime Geodesic Search Engine</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            color: #333;
        }
        .controls {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .control-panel {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }
        .control-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #495057;
        }
        input, select, button {
            width: 100%;
            padding: 8px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-size: 14px;
        }
        button {
            background-color: #007bff;
            color: white;
            border: none;
            cursor: pointer;
            margin-top: 10px;
        }
        button:hover {
            background-color: #0056b3;
        }
        .export-btn {
            background-color: #28a745;
        }
        .export-btn:hover {
            background-color: #1e7e34;
        }
        .visualization {
            margin: 20px 0;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            overflow: hidden;
        }
        .status {
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
        }
        .status.success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .statistics {
            background-color: #e7f3ff;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #6c757d;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Prime Geodesic Search Engine</h1>
            <p>Interactive visualization of modular spiral mapping using θ'(n,k) = φ·{n/φ}^k</p>
        </div>
        
        <div class="controls">
            <!-- Generation Controls -->
            <div class="control-panel">
                <h3>Generate Coordinates</h3>
                <div class="control-group">
                    <label for="start">Start Integer:</label>
                    <input type="number" id="start" value="2" min="1">
                </div>
                <div class="control-group">
                    <label for="end">End Integer:</label>
                    <input type="number" id="end" value="102" min="2">
                </div>
                <div class="control-group">
                    <label for="step">Step Size:</label>
                    <input type="number" id="step" value="1" min="1">
                </div>
                <button onclick="generateCoordinates()">Generate Geodesic Coordinates</button>
            </div>
            
            <!-- Visualization Controls -->
            <div class="control-panel">
                <h3>Visualization Options</h3>
                <div class="control-group">
                    <label for="vizType">Visualization Type:</label>
                    <select id="vizType">
                        <option value="3d_spiral">3D Spiral</option>
                        <option value="density_heatmap">Density Heatmap</option>
                        <option value="curvature_analysis">Curvature Analysis</option>
                    </select>
                </div>
                <div class="control-group">
                    <label for="colorBy">Color Mapping:</label>
                    <select id="colorBy">
                        <option value="density_enhancement">Density Enhancement</option>
                        <option value="curvature">Curvature</option>
                        <option value="prime_status">Prime Status</option>
                    </select>
                </div>
                <div class="control-group">
                    <label>
                        <input type="checkbox" id="showClusters" checked> Show Prime Clusters
                    </label>
                </div>
                <button onclick="createVisualization()">Create Visualization</button>
            </div>
            
            <!-- Search Controls -->
            <div class="control-panel">
                <h3>Search & Filter</h3>
                <div class="control-group">
                    <label>
                        <input type="checkbox" id="primesOnly"> Primes Only
                    </label>
                </div>
                <div class="control-group">
                    <label for="curvatureMin">Min Curvature:</label>
                    <input type="number" id="curvatureMin" step="0.1" placeholder="Optional">
                </div>
                <div class="control-group">
                    <label for="curvatureMax">Max Curvature:</label>
                    <input type="number" id="curvatureMax" step="0.1" placeholder="Optional">
                </div>
                <div class="control-group">
                    <label for="densityMin">Min Density Enhancement:</label>
                    <input type="number" id="densityMin" step="0.5" placeholder="Optional">
                </div>
                <button onclick="searchFilter()">Apply Search Filter</button>
            </div>
            
            <!-- Export Controls -->
            <div class="control-panel">
                <h3>Export Data</h3>
                <div class="control-group">
                    <label for="exportFormat">Export Format:</label>
                    <select id="exportFormat">
                        <option value="csv">CSV</option>
                        <option value="json">JSON</option>
                        <option value="npy">NumPy</option>
                    </select>
                </div>
                <div class="control-group">
                    <label for="filename">Filename:</label>
                    <input type="text" id="filename" value="geodesic_data" placeholder="filename">
                </div>
                <button class="export-btn" onclick="exportData()">Export Current Data</button>
                <button onclick="getStatistics()">Show Statistics</button>
            </div>
        </div>
        
        <div id="status"></div>
        <div id="statistics"></div>
        <div id="visualization" class="visualization"></div>
    </div>

    <script>
        function showStatus(message, isError = false) {
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = `<div class="status ${isError ? 'error' : 'success'}">${message}</div>`;
            setTimeout(() => statusDiv.innerHTML = '', 5000);
        }
        
        function showLoading(message) {
            document.getElementById('visualization').innerHTML = `<div class="loading">${message}</div>`;
        }
        
        async function generateCoordinates() {
            const start = parseInt(document.getElementById('start').value);
            const end = parseInt(document.getElementById('end').value);
            const step = parseInt(document.getElementById('step').value);
            
            if (start >= end) {
                showStatus('Start must be less than end', true);
                return;
            }
            
            showLoading('Generating geodesic coordinates...');
            
            try {
                const response = await fetch('/api/generate_coordinates', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ start, end, step })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showStatus(`Generated ${result.total_points} points (${result.prime_count} primes, ${result.cluster_count} clusters)`);
                    document.getElementById('visualization').innerHTML = '<div class="loading">Click "Create Visualization" to see the results</div>';
                } else {
                    showStatus(result.error, true);
                }
            } catch (error) {
                showStatus('Error generating coordinates: ' + error.message, true);
            }
        }
        
        async function createVisualization() {
            const vizType = document.getElementById('vizType').value;
            const colorBy = document.getElementById('colorBy').value;
            const showClusters = document.getElementById('showClusters').checked;
            
            showLoading('Creating visualization...');
            
            try {
                const response = await fetch('/api/visualize', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ type: vizType, color_by: colorBy, show_clusters: showClusters })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    document.getElementById('visualization').innerHTML = result.plot_html;
                    showStatus('Visualization created successfully');
                } else {
                    showStatus(result.error, true);
                }
            } catch (error) {
                showStatus('Error creating visualization: ' + error.message, true);
            }
        }
        
        async function searchFilter() {
            const criteria = {
                primes_only: document.getElementById('primesOnly').checked
            };
            
            const curvatureMin = document.getElementById('curvatureMin').value;
            const curvatureMax = document.getElementById('curvatureMax').value;
            const densityMin = document.getElementById('densityMin').value;
            
            if (curvatureMin) criteria.curvature_min = parseFloat(curvatureMin);
            if (curvatureMax) criteria.curvature_max = parseFloat(curvatureMax);
            if (densityMin) criteria.density_min = parseFloat(densityMin);
            
            showLoading('Applying search filter...');
            
            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ criteria })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showStatus(`Filter applied: ${result.total_found} points found (${result.prime_count} primes)`);
                    document.getElementById('visualization').innerHTML = '<div class="loading">Click "Create Visualization" to see filtered results</div>';
                } else {
                    showStatus(result.error, true);
                }
            } catch (error) {
                showStatus('Error applying filter: ' + error.message, true);
            }
        }
        
        async function exportData() {
            const format = document.getElementById('exportFormat').value;
            const filename = document.getElementById('filename').value || 'geodesic_data';
            
            try {
                const response = await fetch('/api/export', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ format, filename })
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `${filename}.${format}`;
                    a.click();
                    window.URL.revokeObjectURL(url);
                    showStatus('Data exported successfully');
                } else {
                    const result = await response.json();
                    showStatus(result.error, true);
                }
            } catch (error) {
                showStatus('Error exporting data: ' + error.message, true);
            }
        }
        
        async function getStatistics() {
            try {
                const response = await fetch('/api/statistics');
                const result = await response.json();
                
                if (result.success) {
                    const stats = result.statistics;
                    const statsHtml = `
                        <div class="statistics">
                            <h3>Statistical Analysis</h3>
                            <p><strong>Total Points:</strong> ${stats.summary.total_points}</p>
                            <p><strong>Primes:</strong> ${stats.summary.prime_count} (${(stats.summary.prime_ratio * 100).toFixed(2)}%)</p>
                            <p><strong>Prime Clusters:</strong> ${stats.clustering.cluster_count}</p>
                            <p><strong>Mean Density Enhancement:</strong> ${stats.density_enhancement.mean_enhancement.toFixed(2)}%</p>
                            <p><strong>Average Curvature (Primes):</strong> ${stats.curvature_analysis.prime_curvature_mean.toFixed(4)}</p>
                            <p><strong>Average Curvature (Composites):</strong> ${stats.curvature_analysis.composite_curvature_mean.toFixed(4)}</p>
                            <p><strong>Validation Target:</strong> ${stats.validation_metrics.expected_prime_enhancement}% (Expected)</p>
                            <p><strong>Achieved Enhancement:</strong> ${stats.validation_metrics.achieved_enhancement.toFixed(2)}%</p>
                        </div>
                    `;
                    document.getElementById('statistics').innerHTML = statsHtml;
                    showStatus('Statistics updated');
                } else {
                    showStatus(result.error, true);
                }
            } catch (error) {
                showStatus('Error getting statistics: ' + error.message, true);
            }
        }
        
        // Auto-generate initial data on page load
        window.onload = function() {
            generateCoordinates();
        };
    </script>
</body>
</html>'''
    
    # Write template file
    template_path = os.path.join(template_dir, 'index.html')
    with open(template_path, 'w') as f:
        f.write(html_content)


if __name__ == '__main__':
    # Create templates before running
    create_template()
    
    print("Starting Prime Geodesic Search Engine Web Interface...")
    print("Access the application at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)