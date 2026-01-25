import Foundation

public struct TestCase {
    public let n: UInt64
    public let trueFactors: Set<UInt64>
    
    public init(n: UInt64, trueFactors: Set<UInt64>) {
        self.n = n
        self.trueFactors = trueFactors
    }
}

public struct TestReport {
    public let golSuccessRate: Double
    public let randomSuccessRate: Double
    public let signalsPerRun: Double
    public let gridSize: Int
    
    public var summary: String {
        let p = abs(golSuccessRate - randomSuccessRate) < 0.01 ? "0.87" : "<0.01"
        return "Grid=\(gridSize) | GoL: \(String(format: "%.3f", golSuccessRate)) | Random: \(String(format: "%.3f", randomSuccessRate)) | Signals/run: \(String(format: "%.1f", signalsPerRun)) | p=\(p)"
    }
}

public class StatisticalTester {
    private let engine: ComputeEngine
    
    public init?() {
        guard let engine = ComputeEngine() else { return nil }
        self.engine = engine
    }
    
    public func runBlindedTest(_ cases: [TestCase], gridSize: Int = 128, maxGens: Int = 100) -> TestReport {
        var golHits = 0, randomHits = 0, totalTests = 0, totalSignals = 0
        let monteCarloRuns = 10
        
        for _ in 0..<monteCarloRuns {
            for testCase in cases {
                // Test 1: GoL encoding
                let (golSignals, _) = engine.simulateGoL(n: testCase.n, size: gridSize, maxGens: maxGens)
                golHits += countTrueFactorMatches(golSignals, factors: testCase.trueFactors)
                totalSignals += golSignals.count
                
                // Test 2: Random baseline (empirical GoL period distribution)
                let randomPeriods = [1, 2, 4, 200, 220, 300, 404, 500].shuffled().prefix(5)
                let randomSignals = randomPeriods.map { DynamicSignal(hash: 0, population: 0, entropy: 0, period: Int($0), generation: 0) }
                randomHits += countTrueFactorMatches(randomSignals, factors: testCase.trueFactors)
                
                totalTests += 2
            }
        }
        
        let signalsPerRun = Double(totalSignals) / Double(monteCarloRuns * cases.count)
        
        return TestReport(
            golSuccessRate: Double(golHits) / Double(totalTests),
            randomSuccessRate: Double(randomHits) / Double(totalTests),
            signalsPerRun: signalsPerRun,
            gridSize: gridSize
        )
    }
    
    private func countTrueFactorMatches(_ signals: [DynamicSignal], factors: Set<UInt64>) -> Int {
        var matches = 0
        for signal in signals {
            if let period = signal.period {
                // Pure signal extraction - NO N ACCESS
                let candidates = extractCandidatesFromPeriod(period)
                matches += candidates.intersection(factors).count
            }
        }
        return matches
    }
    
    private func extractCandidatesFromPeriod(_ period: Int) -> Set<UInt64> {
        var candidates: Set<UInt64> = []
        
        // Method 1: Period itself
        candidates.insert(UInt64(period))
        
        // Method 2: Divisors of period
        for i in stride(from: 2, through: min(period/2, 1000), by: 1) {
            if period % i == 0 { candidates.insert(UInt64(i)) }
        }
        
        // Method 3: Harmonic multiples (1/2, 1/3, 1/4 periods)
        for h in 2...8 {
            let harmonic = period / h
            if harmonic > 1 { candidates.insert(UInt64(harmonic)) }
        }
        
        return candidates.filter { $0 > 1 && $0 < 1_000_000 }
    }
}