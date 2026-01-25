// GridAnalyzer.swift - BLINDED ANALYSIS ONLY
public struct DynamicSignal {
    public let hash: UInt32
    public let population: Int
    public let entropy: Float
    public let period: Int?
    public let generation: Int
}

public protocol DynamicsObserver {
    func signalDetected(_ signal: DynamicSignal)
}

public class GridAnalyzer: DynamicsObserver {
    private var stateHistory: [UInt32: Int] = [:]  // hash → generation
    private var signals: [DynamicSignal] = []
    
    public func signalDetected(_ signal: DynamicSignal) {
        if let priorGen = stateHistory[signal.hash] {
            let period = signal.generation - priorGen
            let cycledSignal = DynamicSignal(
                hash: signal.hash, population: signal.population,
                entropy: signal.entropy, period: period, generation: signal.generation
            )
            signals.append(cycledSignal)
        } else {
            stateHistory[signal.hash] = signal.generation
        }
    }
    
    public func getSignals() -> [DynamicSignal] { signals }
    func reset() { stateHistory.removeAll(); signals.removeAll() }
}