import numpy as np
import os

def lj_force(r_vecs, epsilon=1.0, sigma=1.0):
    n = len(r_vecs)
    forces = np.zeros_like(r_vecs)
    potential_energy = 0.0
    
    for i in range(n):
        for j in range(i + 1, n):
            rij_vec = r_vecs[i] - r_vecs[j]
            r = np.linalg.norm(rij_vec)
            if r < 0.1: r = 0.1 
            sr6 = (sigma / r)**6
            sr12 = sr6 * sr6
            potential_energy += 4 * epsilon * (sr12 - sr6)
            f_mag = 24 * epsilon * (2 * sr12 - sr6) / (r**2)
            f_vec = f_mag * rij_vec
            forces[i] += f_vec
            forces[j] -= f_vec
    return forces, potential_energy

def run_experiment_export():
    print("--- Generating Trajectory for C++ Analyzer ---")
    
    n_atoms = 13
    positions = []
    spacing = 1.12
    side = 2
    for x in range(side+1):
        for y in range(side+1):
            for z in range(side+1):
                if len(positions) < n_atoms:
                    positions.append([x*spacing, y*spacing, z*spacing])
    positions = np.array(positions)
    positions -= np.mean(positions, axis=0)
    
    velocities = np.random.normal(0, 0.1, (n_atoms, 3))
    velocities -= np.mean(velocities, axis=0)
    
    mass = 1.0
    dt = 0.005
    n_steps = 1000
    
    forces, pe = lj_force(positions)
    
    # Open output file
    with open("cluster_traj.xyz", "w") as f:
        for step in range(n_steps):
            # Integrate
            velocities += 0.5 * forces / mass * dt
            positions += velocities * dt
            new_forces, pe = lj_force(positions)
            velocities += 0.5 * new_forces / mass * dt
            forces = new_forces
            
            ke = 0.5 * mass * np.sum(velocities**2)
            total_energy = pe + ke
            
            # Write XYZ Frame
            # Line 1: N atoms
            f.write(f"{n_atoms}\n")
            # Line 2: Comment with Time and Energy
            f.write(f"Time={step*dt:.4f} Energy={total_energy:.6f}\n")
            # Lines 3+: Type X Y Z VX VY VZ
            for i in range(n_atoms):
                f.write(f"Ar {positions[i,0]:.4f} {positions[i,1]:.4f} {positions[i,2]:.4f} "
                        f"{velocities[i,0]:.4f} {velocities[i,1]:.4f} {velocities[i,2]:.4f}\n")
                        
    print("Trajectory saved to 'cluster_traj.xyz'")

if __name__ == "__main__":
    run_experiment_export()
