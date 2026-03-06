import numpy as np

def lj_force(r_vecs, epsilon=1.0, sigma=1.0):
    """Compute LJ forces and Energy"""
    n = len(r_vecs)
    forces = np.zeros_like(r_vecs)
    potential_energy = 0.0
    
    for i in range(n):
        for j in range(i + 1, n):
            rij_vec = r_vecs[i] - r_vecs[j]
            r = np.linalg.norm(rij_vec)
            
            # Repulsive core cutoff to prevent overflow if things get too close
            if r < 0.1: r = 0.1 
            
            sr6 = (sigma / r)**6
            sr12 = sr6 * sr6
            
            potential_energy += 4 * epsilon * (sr12 - sr6)
            
            f_mag = 24 * epsilon * (2 * sr12 - sr6) / (r**2)
            f_vec = f_mag * rij_vec
            
            forces[i] += f_vec
            forces[j] -= f_vec
            
    return forces, potential_energy

def compute_z_diag(r_vecs, v_vecs, energy, mass=1.0):
    rcm = np.mean(r_vecs, axis=0)
    vcm = np.mean(v_vecs, axis=0)
    r_rel = r_vecs - rcm
    v_rel = v_vecs - vcm
    
    # Moment of inertia I and its derivative I_dot
    I = np.sum(mass * np.sum(r_rel**2, axis=1))
    I_dot = 2 * np.sum(mass * np.sum(r_rel * v_rel, axis=1))
    
    return I * I_dot / energy

def run_experiment():
    print("--- Starting Molecular Experiment (Ar13 Cluster - Lattice Init) ---")
    
    # Grid initialization to avoid overlap
    n_atoms = 13
    positions = []
    spacing = 1.12 # 2^(1/6) is min of LJ, use slightly larger
    side = 2
    for x in range(side+1):
        for y in range(side+1):
            for z in range(side+1):
                if len(positions) < n_atoms:
                    positions.append([x*spacing, y*spacing, z*spacing])
    positions = np.array(positions)
    
    # Remove COM motion
    positions -= np.mean(positions, axis=0)
    
    velocities = np.random.normal(0, 0.1, (n_atoms, 3))
    velocities -= np.mean(velocities, axis=0)
    
    mass = 1.0
    dt = 0.005
    n_steps = 5000
    
    z_history = []
    energy_history = []
    
    forces, pe = lj_force(positions)
    print(f"Initial PE: {pe:.2f}")
    
    for step in range(n_steps):
        velocities += 0.5 * forces / mass * dt
        positions += velocities * dt
        new_forces, pe = lj_force(positions)
        velocities += 0.5 * new_forces / mass * dt
        forces = new_forces
        
        ke = 0.5 * mass * np.sum(velocities**2)
        total_energy = pe + ke
        energy_history.append(total_energy)
        
        z = compute_z_diag(positions, velocities, total_energy, mass)
        z_history.append(z)
        
    mean_z = np.mean(z_history[100:]) # Skip transient
    std_z = np.std(z_history[100:])
    mean_E = np.mean(energy_history)
    
    print(f"Mean Energy: {mean_E:.2f}")
    print(f"Mean Z: {mean_z:.4e}")
    print(f"Std Z:  {std_z:.4e}")
    
    # Check Stability
    if mean_E < 0 and abs(mean_z) < 10.0:
        print("[PASS] Cluster remained bound (Negative Energy, Bounded Z)")
    else:
        print("[FAIL] Cluster dissociated or unstable")

if __name__ == "__main__":
    run_experiment()