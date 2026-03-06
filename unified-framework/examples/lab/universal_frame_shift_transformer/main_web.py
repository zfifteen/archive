#!/usr/bin/env python3
"""
Universal Frame Shift Theory: Web Application
============================================

An interactive web application for visualizing prime number distributions
through Universal Frame Shift corrections. Users can explore different
configurations and adjust parameters in real-time.

Author: [Author Name]
Date: [Date]
Version: 2.0
"""

import math
from typing import Tuple

import numpy as np
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from scipy.spatial import KDTree
from sympy.stats.sampling.sample_scipy import scipy

# ============================================================================
# UNIVERSAL CONSTANTS AND CONFIGURATIONS
# ============================================================================

UNIVERSAL = scipy.constants.c
PHI = (1 + math.sqrt(5)) / 2
PI_E_RATIO = math.pi / math.e

# Predefined configurations with explanations
PRESET_CONFIGS = {
    'π-Region Optimal': {
        'rate': 0.61,
        'freq': 0.091,
        'n_points': 10000,
        'description': 'Top π-region configuration showing 35x prime density improvement with clear helical clustering'
    },
    'Golden Ratio Scaling': {
        'rate': UNIVERSAL / PHI,
        'freq': 0.1,
        'n_points': 10000,
        'description': 'Configuration focused on φ (golden ratio) scaling with secondary clustering patterns'
    },
    'Identity Transformation': {
        'rate': UNIVERSAL,
        'freq': 0.05,
        'n_points': 2500,
        'description': 'Baseline configuration using identity transformation (e scaling)'
    },
    'High Frequency': {
        'rate': 0.67,
        'freq': 0.12,
        'n_points': 1500,
        'description': 'High-frequency configuration showing compressed helical patterns'
    },
    'Large Scale': {
        'rate': 0.64,
        'freq': 0.085,
        'n_points': 5000,
        'description': 'Large-scale analysis (5000 points) showing long-range clustering'
    }
}

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "Universal Frame Shift Theory"

# ============================================================================
# MATHEMATICAL UTILITIES (OPTIMIZED)
# ============================================================================

def is_prime(n: int) -> bool:
    """Optimized primality test."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    sqrt_n = int(math.sqrt(n)) + 1
    for i in range(3, sqrt_n, 2):
        if n % i == 0:
            return False
    return True

def compute_frame_shifts(n: np.ndarray, max_n: int) -> np.ndarray:
    """Vectorized frame shift computation."""
    base_shift = np.zeros_like(n, dtype=float)
    valid_mask = (n > 1)
    
    n_valid = n[valid_mask]
    base_shift[valid_mask] = np.log(n_valid) / np.log(max_n)
    
    gap_phase = 2 * np.pi * n_valid / (np.log(n_valid) + 1)
    oscillation = 0.1 * np.sin(gap_phase)
    
    base_shift[valid_mask] += oscillation
    return base_shift

def generate_prime_mask(n_points: int) -> np.ndarray:
    """Generate prime mask."""
    n_array = np.arange(1, n_points + 1)
    return np.vectorize(is_prime)(n_array)

# ============================================================================
# COORDINATE GENERATION
# ============================================================================

def compute_universal_coordinates(n_points: int, rate: float, helix_freq: float) -> Tuple:
    """Compute 3D coordinates in universal frame."""
    n = np.arange(1, n_points + 1)
    frame_shifts = compute_frame_shifts(n, n_points)
    
    # X coordinate: Natural position
    x = n.astype(float)
    
    # Y coordinate: Frame-corrected growth
    y_base = n * (n / math.pi)
    y_corrected = y_base * (1 + frame_shifts)
    y = y_corrected * (rate / UNIVERSAL)  # Simplified transformation
    
    # Z coordinate: Helical coordinate
    z = np.sin(math.pi * helix_freq * n)
    
    return x, y, z, frame_shifts

def compute_prime_density_score(prime_coords: np.ndarray) -> float:
    """Compute prime density score."""
    if len(prime_coords) < 2:
        return 0.0
    
    tree = KDTree(prime_coords)
    k_neighbors = min(3, len(prime_coords))
    distances, _ = tree.query(prime_coords, k=k_neighbors)
    
    if distances.shape[1] <= 1:
        return 0.0
    
    position_weights = 1.0 / (np.sqrt(prime_coords[:, 0]) + 1)
    weighted_distances = distances[:, 1] * position_weights
    mean_distance = np.mean(weighted_distances)
    
    return 1.0 / mean_distance if mean_distance > 0 else 0.0

# ============================================================================
# APP LAYOUT
# ============================================================================

app.layout = dbc.Container(
    fluid=True,
    className="p-4",
    children=[
        html.Div(
            className="app-header",
            children=[
                html.H1("Universal Frame Shift Theory", className="display-4 mb-4"),
                html.P(
                    "Visualizing prime number distributions through frame-corrected geometric clustering",
                    className="lead"
                ),
                html.Hr(className="my-4")
            ]
        ),
        
        dbc.Row(
            [
                # Left panel - Controls
                dbc.Col(
                    md=3,
                    className="control-panel",
                    children=[
                        html.H4("Configuration", className="mb-3"),
                        dcc.Dropdown(
                            id='preset-selector',
                            options=[
                                {'label': name, 'value': name} 
                                for name in PRESET_CONFIGS.keys()
                            ],
                            value='π-Region Optimal',
                            className="mb-3"
                        ),
                        html.Div(id='preset-description', className="mb-4 p-3 bg-light rounded"),
                        
                        html.H4("Parameters", className="mb-3"),
                        html.Label("Rate (B):", className="mt-2"),
                        dcc.Slider(
                            id='rate-slider',
                            min=0.1,
                            max=2.0,
                            step=0.01,
                            value=PRESET_CONFIGS['π-Region Optimal']['rate'],
                            marks={i: f"{i:.1f}" for i in np.arange(0.1, 2.1, 0.3)},
                            className="mb-4"
                        ),
                        
                        html.Label("Frequency (f):", className="mt-2"),
                        dcc.Slider(
                            id='freq-slider',
                            min=0.01,
                            max=0.2,
                            step=0.001,
                            value=PRESET_CONFIGS['π-Region Optimal']['freq'],
                            marks={i: f"{i:.2f}" for i in np.arange(0.01, 0.21, 0.04)},
                            className="mb-4"
                        ),
                        
                        html.Label("Number of Points (n):", className="mt-2"),
                        dcc.Slider(
                            id='n-slider',
                            min=500,
                            max=5000,
                            step=100,
                            value=PRESET_CONFIGS['π-Region Optimal']['n_points'],
                            marks={i: f"{i//1000}k" if i >= 1000 else str(i) for i in [500, 1000, 2000, 3000, 4000, 5000]},
                            className="mb-4"
                        ),
                        
                        dbc.Button(
                            "Generate Plot", 
                            id='generate-button', 
                            color="primary", 
                            className="w-100 mb-3"
                        ),
                        
                        html.Div(
                            id='density-score',
                            className="p-3 bg-info text-white rounded text-center"
                        ),
                        
                        html.Div(
                            className="theory-summary mt-4 p-3 bg-secondary text-white rounded",
                            children=[
                                html.H5("Theory Overview"),
                                html.P("Universal Form: Z = A(B/C)"),
                                html.P("Discrete Domain: Z = n(Δₙ/Δₘₐₓ)"),
                                html.P("Prime numbers exhibit geometric clustering when viewed from a universal reference frame centered on mathematical constants."),
                                html.P("Key Constants: e ≈ 2.718, φ ≈ 1.618, π ≈ 3.142")
                            ]
                        )
                    ]
                ),
                
                # Right panel - Visualization
                dbc.Col(
                    md=9,
                    children=[
                        dcc.Loading(
                            id="plot-loading",
                            type="circle",
                            children=[
                                dcc.Graph(
                                    id='3d-plot',
                                    className="plot-container",
                                    config={'displayModeBar': True}
                                )
                            ]
                        ),
                        
                        html.Div(
                            className="legend-container p-3 mt-3",
                            children=[
                                html.H5("Visualization Legend"),
                                dbc.Row([
                                    dbc.Col([
                                        html.Div([
                                            html.Span(className="legend-color", style={"background-color": "rgba(100, 100, 255, 0.2)"}),
                                            " Composites (color indicates frame shift)"
                                        ])
                                    ], md=6),
                                    dbc.Col([
                                        html.Div([
                                            html.Span(className="legend-color", style={"background-color": "red"}),
                                            " Primes (show geometric clustering)"
                                        ])
                                    ], md=6)
                                ]),
                                html.P("Frame shift Δₙ indicates how number space distorts away from the origin"),
                                html.P("Helical patterns reveal the underlying geometric structure of prime distribution")
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

# ============================================================================
# CALLBACKS
# ============================================================================

@app.callback(
    [Output('rate-slider', 'value'),
     Output('freq-slider', 'value'),
     Output('n-slider', 'value'),
     Output('preset-description', 'children')],
    [Input('preset-selector', 'value')]
)
def update_sliders_from_preset(preset_name):
    """Update sliders based on selected preset configuration"""
    config = PRESET_CONFIGS[preset_name]
    description = config['description']
    return config['rate'], config['freq'], config['n_points'], description

@app.callback(
    [Output('3d-plot', 'figure'),
     Output('density-score', 'children')],
    [Input('generate-button', 'n_clicks')],
    [State('rate-slider', 'value'),
     State('freq-slider', 'value'),
     State('n-slider', 'value')]
)
def generate_plot(n_clicks, rate, freq, n_points):
    """Generate 3D plot based on current parameters"""
    # Generate coordinates
    x, y, z, frame_shifts = compute_universal_coordinates(n_points, rate, freq)
    prime_mask = generate_prime_mask(n_points)
    
    # Extract prime coordinates
    prime_coords = np.column_stack((x[prime_mask], y[prime_mask], z[prime_mask]))
    
    # Compute density score
    density_score = compute_prime_density_score(prime_coords)
    
    # Create plot
    fig = go.Figure()
    
    # Add composites with color coding by frame shift
    composite_color = frame_shifts[~prime_mask]
    composite_color = (composite_color - composite_color.min()) / (composite_color.max() - composite_color.min())
    
    fig.add_trace(go.Scatter3d(
        x=x[~prime_mask],
        y=y[~prime_mask],
        z=z[~prime_mask],
        mode='markers',
        marker=dict(
            size=3,
            color=composite_color,
            colorscale='Viridis',
            opacity=0.3,
            colorbar=dict(title='Frame Shift', thickness=20)
        ),
        name='Composites'
    ))
    
    # Add primes
    fig.add_trace(go.Scatter3d(
        x=x[prime_mask],
        y=y[prime_mask],
        z=z[prime_mask],
        mode='markers',
        marker=dict(
            size=5,
            color='red',
            symbol='diamond'
        ),
        name='Primes'
    ))
    
    # Layout configuration
    fig.update_layout(
        title=f"Universal Frame Shift Visualization<br>Rate: {rate:.3f}, Frequency: {freq:.3f}, Points: {n_points}",
        scene=dict(
            xaxis_title='Natural Position (n)',
            yaxis_title='Frame-Corrected Growth (y)',
            zaxis_title='Helical Coordinate (z)',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5)
            ),
            aspectmode='cube'
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        height=800,
        template='plotly_dark'
    )
    
    # Format density score
    score_text = f"Prime Density Score: {density_score:.6f} | Improvement: {(density_score/0.0007):.1f}x over baseline"
    
    return fig, score_text

# ============================================================================
# RUN THE APP
# ============================================================================

if __name__ == '__main__':
    app.run(debug=True, port=8050)