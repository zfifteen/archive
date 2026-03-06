import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

def invert_point(x, y):
    """Invert a point through the unit circle"""
    r_squared = x**2 + y**2
    if r_squared == 0:  # Avoid division by zero
        return float('inf'), float('inf')
    return x / r_squared, y / r_squared

def create_grid_inversion_plot():
    """Create visualization of square grid inversion"""
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
    
    # Create original square grid
    x_vals = np.linspace(-2, 2, 15)
    y_vals = np.linspace(-2, 2, 15)
    
    # Plot 1: Original square grid
    for x in x_vals:
        ax1.plot([x, x], [y_vals[0], y_vals[-1]], 'b-', alpha=0.7, linewidth=0.8)
    for y in y_vals:
        ax1.plot([x_vals[0], x_vals[-1]], [y, y], 'b-', alpha=0.7, linewidth=0.8)
    
    # Add unit circle
    unit_circle = Circle((0, 0), 1, fill=False, color='red', linewidth=2, linestyle='--')
    ax1.add_patch(unit_circle)
    ax1.set_xlim(-2.2, 2.2)
    ax1.set_ylim(-2.2, 2.2)
    ax1.set_aspect('equal')
    ax1.set_title('Original Square Grid\nwith Unit Circle', fontsize=12)
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Inverted grid
    for x in x_vals:
        for y in y_vals:
            if abs(x) > 1e-10 or abs(y) > 1e-10:  # Avoid origin
                x_inv, y_inv = invert_point(x, y)
                # Only plot if not too far out
                if abs(x_inv) < 10 and abs(y_inv) < 10:
                    # Plot horizontal lines
                    if abs(x) > 1e-10:
                        x_neighbor = x + (x_vals[1] - x_vals[0])
                        x_neighbor_inv, y_neighbor_inv = invert_point(x_neighbor, y)
                        if (abs(x_neighbor_inv) < 10 and abs(y_neighbor_inv) < 10 and 
                            abs(x_inv) < 10 and abs(y_inv) < 10):
                            ax2.plot([x_inv, x_neighbor_inv], [y_inv, y_neighbor_inv], 
                                   'b-', alpha=0.7, linewidth=0.8)
                    
                    # Plot vertical lines  
                    if abs(y) > 1e-10:
                        y_neighbor = y + (y_vals[1] - y_vals[0])
                        x_neighbor_inv, y_neighbor_inv = invert_point(x, y_neighbor)
                        if (abs(x_neighbor_inv) < 10 and abs(y_neighbor_inv) < 10 and 
                            abs(x_inv) < 10 and abs(y_inv) < 10):
                            ax2.plot([x_inv, x_neighbor_inv], [y_inv, y_neighbor_inv], 
                                   'b-', alpha=0.7, linewidth=0.8)
    
    # Add unit circle
    unit_circle2 = Circle((0, 0), 1, fill=False, color='red', linewidth=2, linestyle='--')
    ax2.add_patch(unit_circle2)
    ax2.set_xlim(-3, 3)
    ax2.set_ylim(-3, 3)
    ax2.set_aspect('equal')
    ax2.set_title('Inverted Grid\n(Flower-like Pattern)', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Z formula visualization
    scenarios = [
        {'A': 5, 'B': 2, 'C': 10, 'label': 'Balanced\nZ = 1.0'},
        {'A': 7, 'B': 1, 'C': 10, 'label': 'Diminishing\nZ = 0.7'},
        {'A': 3, 'B': 3, 'C': 10, 'label': 'Developing\nZ = 0.9'}
    ]
    
    colors = ['green', 'orange', 'blue']
    for i, scenario in enumerate(scenarios):
        A, B, C = scenario['A'], scenario['B'], scenario['C']
        Z = A * (B / C)
        
        # Create nested arcs visualization
        theta = np.linspace(0, 2*np.pi, 100)
        for j in range(A):
            radius = 1 - (j * 0.15)
            complexity = min(B * (j + 1), C)
            wave_amplitude = 0.1 * (complexity / C)
            
            # Add waviness to show complexity
            r_wave = radius + wave_amplitude * np.sin(B * theta)
            x_arc = r_wave * np.cos(theta)
            y_arc = r_wave * np.sin(theta)
            
            ax3.plot(x_arc, y_arc, color=colors[i], alpha=0.7, 
                    label=scenario['label'] if j == 0 else "")
    
    ax3.set_xlim(-1.5, 1.5)
    ax3.set_ylim(-1.5, 1.5)
    ax3.set_aspect('equal')
    ax3.set_title('Z Formula Visualization\nComplexity Scenarios', fontsize=12)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('grid_inversion_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return fig

def calculate_z_scenarios():
    """Calculate and display Z values for different scenarios"""
    print("Z Formula Analysis: Z = A × (B / C)")
    print("=" * 40)
    
    scenarios = [
        {"A": 5, "B": 2, "C": 10, "description": "Balanced development"},
        {"A": 7, "B": 1, "C": 10, "description": "Diminishing returns"},
        {"A": 3, "B": 3, "C": 10, "description": "Rapid development"},
        {"A": 8, "B": 2, "C": 10, "description": "High complexity"},
        {"A": 2, "B": 1, "C": 10, "description": "Early stage"}
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        A, B, C = scenario["A"], scenario["B"], scenario["C"]
        Z = A * (B / C)
        
        print(f"Scenario {i}: A={A}, B={B}, C={C}")
        print(f"  Z = {A} × ({B}/{C}) = {Z:.2f}")
        print(f"  Interpretation: {scenario['description']}")
        
        if Z > 1.2:
            status = "OVER-DEVELOPED (may lose structure)"
        elif Z > 0.8:
            status = "WELL-DEVELOPED (optimal)"
        elif Z > 0.5:
            status = "DEVELOPING (growing complexity)"
        else:
            status = "EARLY STAGE (potential for growth)"
        
        print(f"  Status: {status}")
        print("-" * 40)

if __name__ == "__main__":
    # Generate the visualization
    print("Generating grid inversion visualization...")
    fig = create_grid_inversion_plot()
    
    # Calculate and display Z scenarios
    calculate_z_scenarios()
    
    # Additional analysis
    print("\nGeometric Properties Revealed:")
    print("• Straight lines become circular arcs")
    print("• Grid symmetry transforms to radial symmetry") 
    print("• Outer regions compress toward circle boundary")
    print("• Inner regions expand and create nested patterns")
    print("• The unit circle remains invariant under inversion")
    