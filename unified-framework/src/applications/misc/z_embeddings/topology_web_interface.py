"""
Web Interface for Modular Topology Visualization Suite

This module provides an interactive web interface for the modular topology
visualization suite using Dash and Flask. It enables researchers and educators
to upload datasets, configure visualizations, and export results through a
user-friendly web interface.

FEATURES:
- Interactive parameter controls for θ′(n, k) transformations
- Real-time 3D/5D visualization updates
- Dataset upload and preprocessing
- Pattern analysis with cluster/anomaly detection
- Publication-quality export functionality
- Educational tutorials and examples
"""

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import io
import base64
import json
from datetime import datetime
import os
import sys

# Add the applications directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modular_topology_suite import (
    GeneralizedEmbedding, TopologyAnalyzer, VisualizationEngine, DataExporter,
    generate_prime_sequence, generate_fibonacci_sequence, generate_mersenne_numbers
)

# Initialize Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Modular Topology Visualization Suite"

# Global components
embedding = GeneralizedEmbedding()
analyzer = TopologyAnalyzer()
visualizer = VisualizationEngine(theme='plotly_white')
exporter = DataExporter()

# Application layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Modular Topology Visualization Suite", className="text-center mb-4"),
            html.P([
                "Interactive visualization of discrete data using helical and modular-geodesic embeddings. ",
                "Based on the Z Framework's θ′(n, k) transformations for geometric analysis of ",
                "integer sequences, prime distributions, and network data."
            ], className="text-center text-muted mb-4")
        ], width=12)
    ]),
    
    dbc.Row([
        # Control Panel
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Dataset & Parameters")),
                dbc.CardBody([
                    # Dataset Selection
                    html.H6("Dataset Selection"),
                    dcc.Dropdown(
                        id='dataset-selector',
                        options=[
                            {'label': 'Prime Numbers', 'value': 'primes'},
                            {'label': 'Fibonacci Sequence', 'value': 'fibonacci'},
                            {'label': 'Mersenne Numbers', 'value': 'mersenne'},
                            {'label': 'Custom Upload', 'value': 'custom'}
                        ],
                        value='primes'
                    ),
                    
                    # Custom upload area
                    html.Div(id='upload-area', style={'display': 'none'}, children=[
                        html.Hr(),
                        dcc.Upload(
                            id='upload-data',
                            children=html.Div([
                                'Drag and Drop or ',
                                html.A('Select Files')
                            ]),
                            style={
                                'width': '100%',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '10px'
                            },
                            multiple=False
                        )
                    ]),
                    
                    html.Hr(),
                    
                    # Parameter Controls
                    html.H6("Transformation Parameters"),
                    
                    html.Label("Curvature Parameter (k)"),
                    dcc.Slider(
                        id='k-parameter',
                        min=0.1, max=1.0, step=0.05, value=0.3,
                        marks={i/10: f'{i/10:.1f}' for i in range(1, 11)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                    
                    html.Label("Modulus (φ for golden ratio)"),
                    dcc.Input(
                        id='modulus-input',
                        type='number',
                        value=1.618,
                        step=0.001,
                        style={'width': '100%', 'margin': '5px 0'}
                    ),
                    
                    html.Label("Sequence Limit"),
                    dcc.Input(
                        id='sequence-limit',
                        type='number',
                        value=200,
                        min=10, max=10000,
                        style={'width': '100%', 'margin': '5px 0'}
                    ),
                    
                    html.Label("Helical Frequency"),
                    dcc.Slider(
                        id='helical-frequency',
                        min=0.01, max=0.5, step=0.01, value=0.1,
                        marks={i/100: f'{i/100:.2f}' for i in range(1, 51, 10)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                    
                    html.Hr(),
                    
                    # Analysis Controls
                    html.H6("Pattern Analysis"),
                    
                    html.Label("Clustering Method"),
                    dcc.Dropdown(
                        id='clustering-method',
                        options=[
                            {'label': 'DBSCAN', 'value': 'dbscan'},
                            {'label': 'K-Means', 'value': 'kmeans'},
                            {'label': 'Hierarchical', 'value': 'hierarchical'}
                        ],
                        value='dbscan'
                    ),
                    
                    html.Label("Number of Clusters (K-Means/Hierarchical)"),
                    dcc.Input(
                        id='n-clusters',
                        type='number',
                        value=5,
                        min=2, max=20,
                        style={'width': '100%', 'margin': '5px 0'}
                    ),
                    
                    dbc.Button(
                        "Update Visualization",
                        id='update-button',
                        color="primary",
                        className="w-100 mt-3"
                    )
                ])
            ])
        ], width=3),
        
        # Main Visualization Area
        dbc.Col([
            dbc.Tabs([
                dbc.Tab(label="3D Helical Embedding", tab_id="3d-helix"),
                dbc.Tab(label="5D Projection", tab_id="5d-projection"),
                dbc.Tab(label="Modular Spiral", tab_id="spiral"),
                dbc.Tab(label="Cluster Analysis", tab_id="clusters"),
                dbc.Tab(label="Anomaly Detection", tab_id="anomalies"),
                dbc.Tab(label="Data Export", tab_id="export")
            ], id="visualization-tabs", active_tab="3d-helix"),
            
            html.Div(id="tab-content", className="mt-3")
        ], width=9)
    ]),
    
    # Status and Information Panel
    dbc.Row([
        dbc.Col([
            dbc.Alert(
                id="status-alert",
                children="Ready to visualize data",
                color="info",
                className="mt-3"
            )
        ], width=12)
    ]),
    
    # Store components for data persistence
    dcc.Store(id='current-data'),
    dcc.Store(id='current-coordinates'),
    dcc.Store(id='current-analysis')
], fluid=True)

@app.callback(
    Output('upload-area', 'style'),
    Input('dataset-selector', 'value')
)
def toggle_upload_area(dataset_type):
    """Show/hide upload area based on dataset selection."""
    if dataset_type == 'custom':
        return {'display': 'block'}
    return {'display': 'none'}

@app.callback(
    [Output('current-data', 'data'),
     Output('status-alert', 'children'),
     Output('status-alert', 'color')],
    [Input('update-button', 'n_clicks')],
    [State('dataset-selector', 'value'),
     State('sequence-limit', 'value'),
     State('upload-data', 'contents'),
     State('upload-data', 'filename')]
)
def update_dataset(n_clicks, dataset_type, limit, upload_contents, upload_filename):
    """Update the current dataset based on user selection."""
    if n_clicks is None:
        n_clicks = 0
        
    try:
        if dataset_type == 'primes':
            data = generate_prime_sequence(limit)
            status = f"Generated {len(data)} prime numbers up to {limit}"
            color = "success"
            
        elif dataset_type == 'fibonacci':
            data = generate_fibonacci_sequence(limit)
            status = f"Generated {len(data)} Fibonacci numbers"
            color = "success"
            
        elif dataset_type == 'mersenne':
            max_exp = min(20, limit // 10)  # Reasonable limit for Mersenne
            data = generate_mersenne_numbers(max_exp)
            status = f"Generated {len(data)} Mersenne numbers"
            color = "success"
            
        elif dataset_type == 'custom' and upload_contents is not None:
            # Parse uploaded file
            content_type, content_string = upload_contents.split(',')
            decoded = base64.b64decode(content_string)
            
            try:
                if 'csv' in upload_filename:
                    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                elif 'txt' in upload_filename:
                    content = decoded.decode('utf-8')
                    data = [float(x.strip()) for x in content.split('\n') if x.strip()]
                elif 'json' in upload_filename:
                    data = json.loads(decoded.decode('utf-8'))
                    if isinstance(data, dict) and 'sequence' in data:
                        data = data['sequence']
                else:
                    raise ValueError("Unsupported file format")
                
                if isinstance(data, pd.DataFrame):
                    data = data.iloc[:, 0].tolist()  # Take first column
                
                data = [int(x) for x in data if x > 0][:limit]  # Ensure positive integers
                status = f"Uploaded {len(data)} data points from {upload_filename}"
                color = "success"
                
            except Exception as e:
                data = generate_prime_sequence(100)  # Fallback
                status = f"Error parsing file: {str(e)}. Using default primes."
                color = "warning"
                
        else:
            data = generate_prime_sequence(100)  # Default fallback
            status = "Using default prime sequence"
            color = "info"
            
        return data, status, color
        
    except Exception as e:
        data = generate_prime_sequence(100)
        status = f"Error generating data: {str(e)}. Using default primes."
        color = "danger"
        return data, status, color

@app.callback(
    [Output('current-coordinates', 'data'),
     Output('current-analysis', 'data')],
    [Input('current-data', 'data'),
     Input('k-parameter', 'value'),
     Input('modulus-input', 'value'),
     Input('helical-frequency', 'value'),
     Input('clustering-method', 'value'),
     Input('n-clusters', 'value')]
)
def compute_coordinates_and_analysis(data, k_param, modulus, frequency, 
                                   clustering_method, n_clusters):
    """Compute embeddings and analysis based on current parameters."""
    if data is None or len(data) == 0:
        return {}, {}
    
    try:
        # Initialize embedding with custom modulus
        embedding_custom = GeneralizedEmbedding(modulus=modulus)
        
        # Compute transformations
        theta_transformed = embedding_custom.theta_prime_transform(data, k=k_param)
        helix_coords = embedding_custom.helical_5d_embedding(data, theta_transformed, frequency=frequency)
        spiral_coords = embedding_custom.modular_spiral_coordinates(data)
        
        # Add spiral coordinates to main coordinate dict
        helix_coords['spiral_x'] = spiral_coords['x']
        helix_coords['spiral_y'] = spiral_coords['y']
        helix_coords['spiral_z'] = spiral_coords['z']
        
        # Perform analysis
        cluster_kwargs = {'n_clusters': n_clusters} if clustering_method != 'dbscan' else {}
        clusters, cluster_stats = analyzer.detect_clusters(helix_coords, method=clustering_method, **cluster_kwargs)
        symmetries = analyzer.detect_symmetries(helix_coords)
        anomalies, anomaly_scores = analyzer.detect_anomalies(helix_coords)
        
        # Convert numpy arrays to lists for JSON serialization
        coords_serializable = {}
        for key, value in helix_coords.items():
            if isinstance(value, np.ndarray):
                coords_serializable[key] = value.tolist()
            else:
                coords_serializable[key] = value
        
        analysis_serializable = {
            'clusters': clusters.tolist(),
            'cluster_stats': cluster_stats,
            'symmetries': symmetries,
            'anomalies': anomalies.tolist(),
            'anomaly_scores': anomaly_scores.tolist()
        }
        
        return coords_serializable, analysis_serializable
        
    except Exception as e:
        print(f"Error in computation: {e}")
        return {}, {}

@app.callback(
    Output('tab-content', 'children'),
    [Input('visualization-tabs', 'active_tab'),
     Input('current-coordinates', 'data'),
     Input('current-analysis', 'data')]
)
def render_tab_content(active_tab, coordinates, analysis):
    """Render content for the active tab."""
    if not coordinates or not analysis:
        return html.Div("No data available. Please update the visualization.", 
                       className="text-center text-muted p-4")
    
    try:
        # Convert back to numpy arrays
        coords = {}
        for key, value in coordinates.items():
            if isinstance(value, list):
                coords[key] = np.array(value)
            else:
                coords[key] = value
        
        if active_tab == "3d-helix":
            fig = visualizer.plot_3d_helical_embedding(coords, coords, "3D Helical Embedding")
            return dcc.Graph(figure=fig, style={'height': '600px'})
            
        elif active_tab == "5d-projection":
            fig = visualizer.plot_5d_projection(coords)
            return dcc.Graph(figure=fig, style={'height': '600px'})
            
        elif active_tab == "spiral":
            spiral_coords = {
                'x': coords['spiral_x'],
                'y': coords['spiral_y'], 
                'z': coords['spiral_z'],
                'angles': np.linspace(0, 6*np.pi, len(coords['spiral_x']))
            }
            fig = visualizer.plot_modular_spiral(spiral_coords)
            return dcc.Graph(figure=fig, style={'height': '600px'})
            
        elif active_tab == "clusters":
            clusters = np.array(analysis['clusters'])
            cluster_stats = analysis['cluster_stats']
            fig = visualizer.plot_cluster_analysis(coords, clusters, cluster_stats)
            
            # Add cluster statistics table
            if cluster_stats:
                cluster_table = dbc.Table.from_dataframe(
                    pd.DataFrame(cluster_stats).T.round(3),
                    striped=True, bordered=True, hover=True
                )
                return html.Div([
                    dcc.Graph(figure=fig, style={'height': '500px'}),
                    html.H5("Cluster Statistics", className="mt-3"),
                    cluster_table
                ])
            else:
                return dcc.Graph(figure=fig, style={'height': '600px'})
            
        elif active_tab == "anomalies":
            anomalies = np.array(analysis['anomalies'])
            anomaly_scores = np.array(analysis['anomaly_scores'])
            fig = visualizer.plot_anomaly_detection(coords, anomalies, anomaly_scores)
            
            # Add anomaly statistics
            n_anomalies = np.sum(anomalies == -1)
            anomaly_rate = np.mean(anomalies == -1) * 100
            
            stats_card = dbc.Card([
                dbc.CardBody([
                    html.H5("Anomaly Detection Summary"),
                    html.P(f"Total Anomalies: {n_anomalies}"),
                    html.P(f"Anomaly Rate: {anomaly_rate:.2f}%"),
                    html.P(f"Detection Method: Isolation Forest")
                ])
            ])
            
            return html.Div([
                dcc.Graph(figure=fig, style={'height': '500px'}),
                stats_card
            ])
            
        elif active_tab == "export":
            return html.Div([
                dbc.Card([
                    dbc.CardHeader(html.H5("Export Options")),
                    dbc.CardBody([
                        html.H6("Coordinate Data"),
                        dbc.ButtonGroup([
                            dbc.Button("Download CSV", id="download-csv", color="outline-primary"),
                            dbc.Button("Download JSON", id="download-json", color="outline-primary"),
                        ]),
                        
                        html.Hr(),
                        
                        html.H6("Analysis Report"),
                        dbc.Button("Download Analysis Report", id="download-report", color="outline-success"),
                        
                        html.Hr(),
                        
                        html.H6("Visualizations"),
                        dbc.ButtonGroup([
                            dbc.Button("Export PNG", id="export-png", color="outline-secondary"),
                            dbc.Button("Export PDF", id="export-pdf", color="outline-secondary"),
                            dbc.Button("Export HTML", id="export-html", color="outline-secondary"),
                        ]),
                        
                        html.Hr(),
                        
                        html.H6("Current Parameters"),
                        html.Pre(id="parameter-summary", style={'background-color': '#f8f9fa', 'padding': '10px'})
                    ])
                ])
            ])
            
        else:
            return html.Div("Tab not implemented yet.")
            
    except Exception as e:
        return html.Div(f"Error rendering visualization: {str(e)}", 
                       className="text-center text-danger p-4")

@app.callback(
    Output('parameter-summary', 'children'),
    [Input('current-coordinates', 'data'),
     Input('k-parameter', 'value'),
     Input('modulus-input', 'value'),
     Input('helical-frequency', 'value'),
     Input('clustering-method', 'value'),
     Input('n-clusters', 'value')]
)
def update_parameter_summary(coordinates, k_param, modulus, frequency, clustering_method, n_clusters):
    """Update the parameter summary display."""
    if not coordinates:
        return "No data loaded"
    
    summary = f"""Current Configuration:
• Dataset Points: {len(coordinates.get('x', []))}
• Curvature Parameter (k): {k_param}
• Modulus: {modulus:.3f}
• Helical Frequency: {frequency}
• Clustering Method: {clustering_method}
• Number of Clusters: {n_clusters}
• Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    return summary

# Additional callbacks for export functionality would go here
# (Implementation would depend on specific requirements for file downloads)

# Run the application
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)