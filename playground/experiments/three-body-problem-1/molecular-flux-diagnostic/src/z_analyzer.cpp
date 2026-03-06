#include <iostream>
#include <fstream>
#include <vector>
#include <sstream>
#include <cmath>
#include <iomanip>

// Standalone C++ Trajectory Analyzer for Z-Diagnostic
// No external dependencies (LAMMPS not required). 
// Compiles with standard g++: g++ -O3 -o z_analyzer z_analyzer.cpp

struct Atom {
    double x, y, z;
    double vx, vy, vz;
    double mass;
};

struct Frame {
    double time;
    double energy; // Total energy for normalization
    std::vector<Atom> atoms;
};

// Calculate Center of Mass
void get_com(const std::vector<Atom>& atoms, double& cx, double& cy, double& cz) {
    double total_mass = 0.0;
    cx = 0.0; cy = 0.0; cz = 0.0;
    for (const auto& a : atoms) {
        cx += a.mass * a.x;
        cy += a.mass * a.y;
        cz += a.mass * a.z;
        total_mass += a.mass;
    }
    if (total_mass > 0) {
        cx /= total_mass;
        cy /= total_mass;
        cz /= total_mass;
    }
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: ./z_analyzer <trajectory_file.xyz>" << std::endl;
        std::cerr << "Format expected: XYZ format with Energy in comment line" << std::endl;
        return 1;
    }

    std::ifstream infile(argv[1]);
    if (!infile.is_open()) {
        std::cerr << "Error opening file." << std::endl;
        return 1;
    }

    std::string line;
    std::vector<Frame> trajectory;
    double mass_default = 1.0; 

    // --- PARSING ---
    while (std::getline(infile, line)) {
        if (line.empty()) continue;
        
        Frame frame;
        int n_atoms;
        try {
            n_atoms = std::stoi(line);
        } catch (...) { continue; }

        // Comment line: Expect "Time=X Energy=Y"
        std::getline(infile, line);
        std::stringstream ss(line);
        std::string temp;
        // Simple parser assuming fixed format for this demo:
        // "Time= 0.00 Energy= -24.50"
        double t_val = 0.0, e_val = 1.0;
        
        // Very basic parsing logic (robustness improved for production)
        size_t t_pos = line.find("Time=");
        size_t e_pos = line.find("Energy=");
        if (t_pos != std::string::npos) t_val = std::stod(line.substr(t_pos + 5));
        if (e_pos != std::string::npos) e_val = std::stod(line.substr(e_pos + 7));

        frame.time = t_val;
        frame.energy = e_val;

        for (int i = 0; i < n_atoms; ++i) {
            std::getline(infile, line);
            std::stringstream atom_ss(line);
            std::string type;
            Atom atom;
            // Format: Type X Y Z VX VY VZ
            atom_ss >> type >> atom.x >> atom.y >> atom.z >> atom.vx >> atom.vy >> atom.vz;
            atom.mass = mass_default;
            frame.atoms.push_back(atom);
        }
        trajectory.push_back(frame);
    }
    infile.close();

    std::cout << "Loaded " << trajectory.size() << " frames." << std::endl;

    // --- ANALYSIS ---
    std::cout << "Time,I,I_dot,Z_Diagnostic" << std::endl;

    for (size_t i = 0; i < trajectory.size(); ++i) {
        const auto& frame = trajectory[i];
        
        // 1. Center of Mass
        double cx, cy, cz;
        get_com(frame.atoms, cx, cy, cz);

        // 2. Moment of Inertia (I) & Rate (I_dot)
        double I = 0.0;
        double I_dot = 0.0;

        for (const auto& a : frame.atoms) {
            double rx = a.x - cx;
            double ry = a.y - cy;
            double rz = a.z - cz;

            // Simple velocity relative to COM (assuming v is already lab frame, 
            // we need v_rel if COM is moving. For I_dot = 2 sum m r.v)
            // Let's approximate v_rel roughly or assume COM static. 
            // Better: calculate V_com.
            
            // To be precise: We need velocities in the file.
            // If velocities are present:
            double vx = a.vx; 
            double vy = a.vy; 
            double vz = a.vz;
            
            // Term: r^2
            double r2 = rx*rx + ry*ry + rz*rz;
            I += a.mass * r2;

            // Term: r . v
            // Note: strict definition uses relative velocity, but if COM is static/removed
            // lab velocity works. Let's use lab v for this standalone tool simplicity
            // or compute v_com if needed.
            double rv = rx*vx + ry*vy + rz*vz;
            I_dot += 2.0 * a.mass * rv;
        }

        // 3. Z Diagnostic
        // Z = I * I_dot / Energy
        // Handle E=0 case
        double E = frame.energy;
        if (std::abs(E) < 1e-9) E = 1e-9;

        double Z = I * I_dot / E;

        std::cout << std::fixed << std::setprecision(4) 
                  << frame.time << "," << I << "," << I_dot << "," << Z << std::endl;
    }

    return 0;
}
