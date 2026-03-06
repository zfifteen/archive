"""
CRISPR Guide Visualization Module

This module provides comprehensive visualization capabilities for the Z-Invariant 
CRISPR Guide Designer, including 3D/5D coordinate plotting, clustering analysis,
and comparative scoring visualizations.

FEATURES:
- Interactive 3D visualization of guide clustering in modular-geodesic space
- 5D coordinate projection and dimensionality reduction plots
- Comparative analysis of conventional vs Z-framework approaches
- Guide quality heatmaps and scoring distributions
- Off-target risk visualization and validation plots
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
import seaborn as sns
from typing import List, Dict, Optional
import warnings
warnings.filterwarnings('ignore')

# Set matplotlib backend for headless environments
plt.switch_backend('Agg')

class CRISPRVisualization:
    """
    Comprehensive visualization suite for CRISPR guide analysis results.
    """
    
    def __init__(self, figsize=(12, 8), style='plotly'):
        """
        Initialize visualization engine.
        
        Args:
            figsize (tuple): Default figure size for matplotlib plots
            style (str): Plotting style ('plotly', 'seaborn', 'matplotlib')
        """
        self.figsize = figsize
        self.style = style
        self.color_palette = px.colors.qualitative.Set1
        
        # Set style defaults
        if style == 'seaborn':
            sns.set_style("whitegrid")
            plt.style.use('seaborn-v0_8')
    
    def plot_5d_coordinate_clusters(self, guides_data: List[Dict], 
                                  save_path: Optional[str] = None) -> go.Figure:
        """
        Create interactive 3D visualization of guide clusters in reduced 5D space.
        
        Args:
            guides_data (List[Dict]): Guide data with 5D coordinates
            save_path (Optional[str]): Path to save plot
            
        Returns:
            go.Figure: Plotly 3D scatter plot
        """
        if not guides_data:
            return None
        
        # Extract 5D coordinates
        coords_5d = []
        guide_info = []
        
        for guide in guides_data:
            if 'coordinates_5d' in guide:
                coords = guide['coordinates_5d']
                # Use mean values for each dimension
                coord_point = [
                    np.mean(coords['x']), np.mean(coords['y']), np.mean(coords['z']),
                    np.mean(coords['w']), np.mean(coords['u'])
                ]
                coords_5d.append(coord_point)
                guide_info.append({
                    'sequence': guide['sequence'],
                    'position': guide['position'],
                    'score': guide.get('composite_score', 0),
                    'risk': guide.get('off_target_risk', 0)
                })
        
        if not coords_5d:
            return None
        
        # Apply PCA to reduce 5D to 3D for visualization
        coords_array = np.array(coords_5d)
        pca = PCA(n_components=3)
        coords_3d = pca.fit_transform(coords_array)
        
        # Extract visualization data
        x, y, z = coords_3d[:, 0], coords_3d[:, 1], coords_3d[:, 2]
        scores = [info['score'] for info in guide_info]
        sequences = [info['sequence'] for info in guide_info]
        positions = [info['position'] for info in guide_info]
        risks = [info['risk'] for info in guide_info]
        
        # Create 3D scatter plot
        fig = go.Figure(data=go.Scatter3d(
            x=x, y=y, z=z,
            mode='markers+text',
            marker=dict(
                size=8,
                color=scores,
                colorscale='Viridis',
                colorbar=dict(title="Composite Score"),
                line=dict(width=1, color='black')
            ),
            text=[f"Pos: {pos}<br>Score: {score:.3f}" for pos, score in zip(positions, scores)],
            textposition="top center",
            hovertemplate=(
                "<b>Guide RNA</b><br>" +
                "Sequence: %{customdata[0]}<br>" +
                "Position: %{customdata[1]}<br>" +
                "Score: %{customdata[2]:.3f}<br>" +
                "Risk: %{customdata[3]:.3f}<br>" +
                "PC1: %{x:.3f}<br>" +
                "PC2: %{y:.3f}<br>" +
                "PC3: %{z:.3f}<extra></extra>"
            ),
            customdata=list(zip(sequences, positions, scores, risks))
        ))
        
        # Update layout
        fig.update_layout(
            title={
                'text': "CRISPR Guide Clustering in Modular-Geodesic Space<br>" +
                       "<sub>5D → 3D PCA Projection of θ′(n, k) Embeddings</sub>",
                'x': 0.5,
                'xanchor': 'center'
            },
            scene=dict(
                xaxis_title=f"PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)",
                yaxis_title=f"PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)",
                zaxis_title=f"PC3 ({pca.explained_variance_ratio_[2]:.1%} variance)",
                camera=dict(eye=dict(x=1.2, y=1.2, z=1.2))
            ),
            width=800,
            height=600
        )
        
        if save_path:
            fig.write_html(save_path)
            
        return fig
    
    def plot_score_comparison(self, guides_data: List[Dict], 
                            save_path: Optional[str] = None) -> go.Figure:
        """
        Create comparative visualization of scoring metrics.
        
        Args:
            guides_data (List[Dict]): Guide data with scores
            save_path (Optional[str]): Path to save plot
            
        Returns:
            go.Figure: Plotly subplot figure
        """
        if not guides_data:
            return None
        
        # Extract scoring data
        positions = [guide['position'] for guide in guides_data]
        z_scores = [guide.get('z_framework_score', 0) for guide in guides_data]
        density_scores = [guide.get('density_enhancement', 0) for guide in guides_data]
        composite_scores = [guide.get('composite_score', 0) for guide in guides_data]
        off_target_risks = [guide.get('off_target_risk', 0) for guide in guides_data]
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                "Z Framework Score vs Position",
                "Density Enhancement vs Position", 
                "Composite Score Distribution",
                "Off-Target Risk vs Composite Score"
            ],
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Z Framework Score scatter
        fig.add_trace(
            go.Scatter(x=positions, y=z_scores, mode='markers',
                      name='Z Framework Score',
                      marker=dict(color='blue', size=6),
                      hovertemplate="Position: %{x}<br>Z Score: %{y:.3f}<extra></extra>"),
            row=1, col=1
        )
        
        # Density Enhancement scatter
        fig.add_trace(
            go.Scatter(x=positions, y=density_scores, mode='markers',
                      name='Density Enhancement',
                      marker=dict(color='green', size=6),
                      hovertemplate="Position: %{x}<br>Density: %{y:.3f}<extra></extra>"),
            row=1, col=2
        )
        
        # Composite Score histogram
        fig.add_trace(
            go.Histogram(x=composite_scores, nbinsx=20,
                        name='Score Distribution',
                        marker=dict(color='purple', opacity=0.7)),
            row=2, col=1
        )
        
        # Risk vs Score scatter
        fig.add_trace(
            go.Scatter(x=composite_scores, y=off_target_risks, mode='markers',
                      name='Risk vs Score',
                      marker=dict(color='red', size=6),
                      hovertemplate="Score: %{x:.3f}<br>Risk: %{y:.3f}<extra></extra>"),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title_text="CRISPR Guide Scoring Analysis Dashboard",
            showlegend=False,
            height=600,
            width=1000
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="Position in Target", row=1, col=1)
        fig.update_xaxes(title_text="Position in Target", row=1, col=2)
        fig.update_xaxes(title_text="Composite Score", row=2, col=1)
        fig.update_xaxes(title_text="Composite Score", row=2, col=2)
        
        fig.update_yaxes(title_text="Z Framework Score", row=1, col=1)
        fig.update_yaxes(title_text="Density Enhancement", row=1, col=2)
        fig.update_yaxes(title_text="Frequency", row=2, col=1)
        fig.update_yaxes(title_text="Off-Target Risk", row=2, col=2)
        
        if save_path:
            fig.write_html(save_path)
            
        return fig
    
    def plot_guide_quality_heatmap(self, guides_data: List[Dict],
                                 save_path: Optional[str] = None) -> plt.Figure:
        """
        Create heatmap visualization of guide quality metrics.
        
        Args:
            guides_data (List[Dict]): Guide data with quality metrics
            save_path (Optional[str]): Path to save plot
            
        Returns:
            plt.Figure: Matplotlib figure
        """
        if not guides_data:
            return None
        
        # Prepare data for heatmap
        metrics_data = []
        guide_labels = []
        
        for i, guide in enumerate(guides_data):
            metrics_data.append([
                guide.get('z_framework_score', 0),
                guide.get('density_enhancement', 0),
                guide.get('geodesic_complexity', 0),
                1.0 / (1.0 + guide.get('off_target_risk', 0)),  # Invert risk for display
                guide.get('composite_score', 0)
            ])
            guide_labels.append(f"Pos{guide['position']}")
        
        # Convert to DataFrame
        df = pd.DataFrame(
            metrics_data,
            index=guide_labels,
            columns=['Z Score', 'Density', 'Complexity', 'Safety', 'Composite']
        )
        
        # Normalize data for better visualization
        df_normalized = (df - df.min()) / (df.max() - df.min())
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=self.figsize)
        sns.heatmap(df_normalized.T, annot=True, cmap='RdYlBu_r', 
                   center=0.5, square=True, ax=ax, 
                   cbar_kws={'label': 'Normalized Score'})
        
        ax.set_title('CRISPR Guide Quality Metrics Heatmap\n'
                    'Higher values indicate better performance')
        ax.set_xlabel('Guide RNA Candidates')
        ax.set_ylabel('Quality Metrics')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        return fig
    
    def plot_conventional_vs_zframework_comparison(self, 
                                                 guides_data: List[Dict],
                                                 save_path: Optional[str] = None) -> go.Figure:
        """
        Compare Z-framework approach with conventional CRISPR scoring.
        
        Args:
            guides_data (List[Dict]): Guide data with both scoring approaches
            save_path (Optional[str]): Path to save plot
            
        Returns:
            go.Figure: Plotly comparison plot
        """
        if not guides_data:
            return None
        
        # Simulate conventional scores for comparison (simplified)
        conventional_scores = []
        z_framework_scores = []
        guide_names = []
        
        for guide in guides_data:
            # Conventional score: basic GC content + position weight
            gc_content = (guide['sequence'].count('G') + guide['sequence'].count('C')) / len(guide['sequence'])
            position_weight = 1.0 / (1.0 + guide['position'] / 1000.0)  # Prefer earlier positions
            conv_score = gc_content * 0.6 + position_weight * 0.4
            
            conventional_scores.append(conv_score)
            z_framework_scores.append(guide.get('composite_score', 0))
            guide_names.append(f"Guide@{guide['position']}")
        
        # Create comparison plot
        fig = go.Figure()
        
        # Add conventional scores
        fig.add_trace(go.Bar(
            name='Conventional Approach',
            x=guide_names,
            y=conventional_scores,
            marker_color='lightblue',
            opacity=0.7,
            hovertemplate="Guide: %{x}<br>Conventional Score: %{y:.3f}<extra></extra>"
        ))
        
        # Add Z-framework scores
        fig.add_trace(go.Bar(
            name='Z-Framework Approach',
            x=guide_names,
            y=z_framework_scores,
            marker_color='darkblue',
            opacity=0.8,
            hovertemplate="Guide: %{x}<br>Z-Framework Score: %{y:.3f}<extra></extra>"
        ))
        
        # Update layout
        fig.update_layout(
            title={
                'text': "Conventional vs Z-Framework CRISPR Guide Scoring<br>" +
                       "<sub>Enhanced precision through modular-geodesic embeddings</sub>",
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis_title="Guide RNA Candidates",
            yaxis_title="Scoring Metric",
            barmode='group',
            legend=dict(x=0.7, y=0.95),
            width=800,
            height=500
        )
        
        if save_path:
            fig.write_html(save_path)
            
        return fig
    
    def create_analysis_dashboard(self, analysis_results: Dict,
                                save_directory: Optional[str] = None) -> Dict:
        """
        Create comprehensive visualization dashboard for analysis results.
        
        Args:
            analysis_results (Dict): Complete analysis results from CRISPRGuideDesigner
            save_directory (Optional[str]): Directory to save all plots
            
        Returns:
            Dict: Dictionary of generated figures
        """
        figures = {}
        embedded_guides = analysis_results.get('embedded_guides', [])
        optimized_guides = analysis_results.get('optimized_guides', [])
        
        if not embedded_guides:
            print("No embedded guides found for visualization")
            return figures
        
        print("Generating visualization dashboard...")
        
        # 1. 5D Coordinate Clusters
        print("- Creating 5D coordinate cluster plot...")
        cluster_fig = self.plot_5d_coordinate_clusters(embedded_guides)
        if cluster_fig:
            figures['cluster_plot'] = cluster_fig
            if save_directory:
                cluster_fig.write_html(f"{save_directory}/cluster_analysis.html")
        
        # 2. Score Comparison Dashboard
        print("- Creating score comparison dashboard...")
        score_fig = self.plot_score_comparison(embedded_guides)
        if score_fig:
            figures['score_dashboard'] = score_fig
            if save_directory:
                score_fig.write_html(f"{save_directory}/score_dashboard.html")
        
        # 3. Quality Heatmap
        print("- Creating quality heatmap...")
        heatmap_fig = self.plot_guide_quality_heatmap(optimized_guides)
        if heatmap_fig:
            figures['quality_heatmap'] = heatmap_fig
            if save_directory:
                heatmap_fig.savefig(f"{save_directory}/quality_heatmap.png", 
                                  dpi=300, bbox_inches='tight')
        
        # 4. Conventional vs Z-Framework Comparison
        print("- Creating methodology comparison...")
        comparison_fig = self.plot_conventional_vs_zframework_comparison(optimized_guides)
        if comparison_fig:
            figures['methodology_comparison'] = comparison_fig
            if save_directory:
                comparison_fig.write_html(f"{save_directory}/methodology_comparison.html")
        
        print(f"Generated {len(figures)} visualization components")
        return figures
    
    def save_analysis_report(self, analysis_results: Dict, figures: Dict,
                           output_path: str):
        """
        Generate and save comprehensive HTML analysis report.
        
        Args:
            analysis_results (Dict): Analysis results
            figures (Dict): Generated figures
            output_path (str): Path for output HTML file
        """
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Z-Invariant CRISPR Guide Designer Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; 
                          background-color: #e8f4fd; border-radius: 3px; }}
                pre {{ background-color: #f8f8f8; padding: 10px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Z-Invariant CRISPR Guide Designer Analysis Report</h1>
                <p>Enhanced genome editing precision through modular-geodesic embeddings</p>
            </div>
            
            <div class="section">
                <h2>Analysis Summary</h2>
                <div class="metric">
                    <strong>Target Length:</strong> {len(analysis_results.get('target_sequence', ''))} bp
                </div>
                <div class="metric">
                    <strong>Potential Guides:</strong> {len(analysis_results.get('potential_guides', []))}
                </div>
                <div class="metric">
                    <strong>Optimized Guides:</strong> {len(analysis_results.get('optimized_guides', []))}
                </div>
            </div>
            
            <div class="section">
                <h2>Detailed Analysis</h2>
                <pre>{analysis_results.get('analysis_summary', 'No summary available')}</pre>
            </div>
            
            <div class="section">
                <h2>Interactive Visualizations</h2>
                <p>The following visualizations have been generated:</p>
                <ul>
                    {''.join([f'<li>{name.replace("_", " ").title()}</li>' for name in figures.keys()])}
                </ul>
            </div>
        </body>
        </html>
        """
        
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        print(f"Analysis report saved to: {output_path}")

def demo_visualization():
    """
    Demonstration of CRISPR visualization capabilities.
    """
    # Import here to avoid circular imports
    from crispr_guide_designer import CRISPRGuideDesigner
    
    # Sample target sequence
    target_sequence = (
        "ATGCTGCGGAGACCTGGAGAGAAAGCAGTGGCCGGGGCAGTGGGAGGAGGAGGAGCTGGAAGAGGAGAGAAAGGAGGAGCTGCAGGAGGAGAGGAGGAGGAGGGAGAGGAGGAGCTGGAGCTGAAGCTGGAGCTGGAGCTGGAGAGGAGAGAGGG"
        "CCCAGGAGCAGCTGCGGCTGGAGCAGCAGCTGCGGCTGGAGCTGCAGCTGCGGCTGGAGCAGCAGCTGCGGCTGGAGCTGCAGCTGCGGCTGGAGCAGCAGCTGCGGCTGGAGCTGCAGCTGCGGCTGGAGCAGCAGCTGCGGCTGGAGCTGCAG"
    )
    
    print("CRISPR Visualization Demo")
    print("=" * 30)
    
    # Run analysis
    designer = CRISPRGuideDesigner(precision=30, k_parameter=0.3)
    results = designer.analyze_target_sequence(target_sequence, max_guides=5)
    
    # Create visualizations
    viz = CRISPRVisualization()
    figures = viz.create_analysis_dashboard(results)
    
    print(f"\nGenerated {len(figures)} visualization components")
    return results, figures

if __name__ == "__main__":
    demo_results, demo_figures = demo_visualization()