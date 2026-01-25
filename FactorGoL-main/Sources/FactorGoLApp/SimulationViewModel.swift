import SwiftUI
import FactorGoLCore

class SimulationViewModel: ObservableObject {
    @Published var currentGrid: [UInt8]? = nil
    @Published var generation: Int = 0
    @Published var population: Int = 0
    @Published var entropy: Float = 0.0
    @Published var signals: [DynamicSignal] = []
    @Published var isRunning: Bool = false
    @Published var n: UInt64 = 10403  // Default resonant case
    @Published var gridSize: Int = 101
    @Published var maxGens: Int = 1000
    @Published var chaosThreshold: Float = 0.4
    @Published var encodingStrategy: Int = 0  // 0: binary fractal, etc.

    private var engine: ComputeEngine?
    private var timer: Timer?

    init() {
        engine = ComputeEngine()
    }

    func startSimulation() {
        guard let engine = engine else { return }
        isRunning = true
        signals = []
        generation = 0
        population = 0
        entropy = 0.0

        // Set initial grid based on selected encoding strategy
        switch encodingStrategy {
        case 0: // Binary Fractal
            currentGrid = BlindEncoder.encode(n, gridSize: gridSize)
        case 1: // Residue Waves
            currentGrid = BlindEncoder.encode(n, gridSize: gridSize)
        case 2: // Dimensional Seeds
            currentGrid = BlindEncoder.encode(n, gridSize: gridSize)
        default:
            currentGrid = BlindEncoder.encode(n, gridSize: gridSize)
        }

        // Capture all parameters locally to avoid race conditions with UI changes
        let maxGenerations = self.maxGens
        let capturedN = self.n
        let capturedGridSize = self.gridSize
        let capturedChaosThreshold = self.chaosThreshold

        // Run simulation in background
        DispatchQueue.global(qos: .userInitiated).async {
            let (simSignals, finalGrid) = engine.simulateGoL(n: capturedN, size: capturedGridSize, maxGens: maxGenerations, debrisThreshold: capturedChaosThreshold)
            DispatchQueue.main.async {
                self.stopSimulation()
                self.signals = simSignals
                self.currentGrid = finalGrid
                self.generation = maxGenerations
                
                // Update stats from last signal, or reset if no signals
                if let lastSignal = simSignals.last {
                    self.population = lastSignal.population
                    self.entropy = lastSignal.entropy
                } else {
                    self.population = 0
                    self.entropy = 0.0
                }
            }
        }

        // For UI updates, simulate step-by-step (simplified)
        // Timer approximates progress but doesn't control the actual simulation
        timer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { [weak self] _ in
            guard let self = self else { return }
            if self.generation < maxGenerations {
                self.generation += 1
            }
        }
    }

    func stopSimulation() {
        isRunning = false
        timer?.invalidate()
        timer = nil
    }

    func reset() {
        stopSimulation()
        currentGrid = nil
        generation = 0
        population = 0
        entropy = 0.0
        signals = []
    }
}