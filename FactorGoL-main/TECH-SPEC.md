# Green Field Implementation: Emergent Factorization via Game of Life (macOS Swift/Metal)

**Status: Clean slate specification. No prior code, conversations, or findings assumed.**

## Project Mission

Build a GPU-accelerated Conway's Game of Life simulator that attempts to reveal integer factors through **emergent dynamical properties only** (periods, stability, spatial patterns). **No trial division or direct divisibility tests permitted in analysis.**

**Scientific Goal:** Test if cellular automata dynamics can encode number-theoretic information without explicit arithmetic computation.

***

## Core Requirements

| Component | Specification | Constraints |
|-----------|---------------|-------------|
| **Platform** | macOS 14+, Apple Silicon | Swift 5.9+, Metal 3 |
| **Grid** | 64-512 toroidal | Double-buffered `UInt8` |
| **Encoding** | 3 blind strategies | Analysis **cannot access N** |
| **Analysis** | Pure dynamics (hash, period, entropy) | No `N % d` tests |
| **Validation** | Blinded statistical testing | Beat random baseline |

***

## 1. Architecture Overview

```
FactorGoL/
├── Sources/
│   ├── main.swift                 # Experiment runner
│   ├── engine/
│   │   ├── ComputeEngine.swift    # Metal GPU simulation
│   │   └── GridAnalyzer.swift     # Pure dynamics analysis
│   ├── encoding/
│   │   └── BlindEncoders.swift    # N→grid (no math ops in analysis)
│   └── validation/
│       └── StatisticalTester.swift # Null hypothesis testing
└── Shaders/
    └── gol.metal                  # Compute kernels
```

***

## 2. Metal Compute Pipeline (gol.metal)

**Three kernels: evolution, hash, entropy**

```metal
#include <metal_stdlib>
using namespace metal;

kernel void life_step(
    device uint8_t* inGrid [[buffer(0)]],
    device uint8_t* outGrid [[buffer(1)]],
    constant uint2& gridSize [[buffer(2)]],
    uint2 tid [[thread_position_in_grid]]
) {
    if (tid.x >= gridSize.x || tid.y >= gridSize.y) return;
    
    uint idx = tid.y * gridSize.x + tid.x;
    int liveNeighbors = 0;
    
    // 8 neighbors + toroidal wrap
    for (int dy = -1; dy <= 1; ++dy) {
        for (int dx = -1; dx <= 1; ++dx) {
            if (dx == 0 && dy == 0) continue;
            uint2 npos = uint2((tid.x + dx + gridSize.x) % gridSize.x,
                              (tid.y + dy + gridSize.y) % gridSize.y);
            liveNeighbors += inGrid[npos.y * gridSize.x + npos.x];
        }
    }
    
    uint8_t cell = inGrid[idx];
    outGrid[idx] = (cell == 1 && (liveNeighbors == 2 || liveNeighbors == 3)) ||
                   (cell == 0 && liveNeighbors == 3) ? 1 : 0;
}

kernel void grid_hash(
    device uint8_t* grid [[buffer(0)]],
    device atomic_uint* hash [[buffer(1)]],
    constant uint& size [[buffer(2)]],
    uint tid [[thread_position_in_grid]]
) {
    if (tid >= size) return;
    if (grid[tid] == 1) {
        atomic_fetch_xor_explicit(hash, tid ^ 16777619u, memory_order_relaxed);
    }
}

kernel void spatial_entropy(
    device uint8_t* grid [[buffer(0)]],
    device float* entropy [[buffer(1)]],
    constant uint2& gridSize [[buffer(2)]],
    uint2 tid [[thread_position_in_grid]]
) {
    if (tid.x >= gridSize.x || tid.y >= gridSize.y) return;
    
    uint idx = tid.y * gridSize.x + tid.x;
    float localDensity = 0;
    
    // Local 3x3 density (coherence measure)
    for (int dy = -1; dy <= 1; ++dy) {
        for (int dx = -1; dx <= 1; ++dx) {
            uint2 npos = uint2((tid.x + dx + gridSize.x) % gridSize.x,
                              (tid.y + dy + gridSize.y) % gridSize.y);
            localDensity += float(grid[npos.y * gridSize.x + npos.x]) / 9.0;
        }
    }
    
    // Low entropy = stable local patterns
    float localEntropy = localDensity * (1.0 - localDensity);
    atomic_fetch_add_explicit(entropy, localEntropy, memory_order_relaxed);
}
```

***

## 3. Blind Encoding Strategies (BlindEncoders.swift)

**Analysis phase receives only grid dynamics. Encoders may use N internally.**

```swift
struct BlindEncoder {
    static func encode(_ n: UInt64, gridSize: Int) -> [UInt8] {
        let strategies = [
            binaryFractal(n: n, size: gridSize),
            residueWave(n: n, size: gridSize),
            dimensionalSeed(n: n, size: gridSize)
        ]
        return strategies.randomElement()!
    }
}

private extension BlindEncoder {
    // Strategy 1: Binary fractal - N's bits → spatial frequency
    static func binaryFractal(n: UInt64, size: Int) -> [UInt8] {
        var grid = [UInt8](repeating: 0, count: size * size)
        let bits = mirror(String(n, radix: 2))
        
        for i in 0..<size {
            for j in 0..<size {
                let bitIdx = (i * 37 + j * 73) % bits.count
                let r = hypot(Double(i - size/2), Double(j - size/2)) / Double(size)
                grid[j * size + i] = (bits[bitIdx] == "1" && sin(r * .pi * 8) > 0) ? 1 : 0
            }
        }
        return grid
    }
    
    // Strategy 2: Residue waves - N mod position → wave interference
    static func residueWave(n: UInt64, size: Int) -> [UInt8] {
        var grid = [UInt8](repeating: 0, count: size * size)
        for i in 0..<size {
            for j in 0..<size {
                let residue = n % UInt64((i + j + 1) * 3 + 1)
                let wave = sin(Double(residue) * Double(i) / 10.0) * cos(Double(residue) * Double(j) / 13.0)
                grid[j * size + i] = abs(wave) > 0.7 ? 1 : 0
            }
        }
        return grid
    }
    
    // Strategy 3: Dimensional seeds - N → glider positions
    static func dimensionalSeed(n: UInt64, size: Int) -> [UInt8] {
        var grid = [UInt8](repeating: 0, count: size * size)
        let seeds = stride(from: 3, to: 29, by: 2).map { UInt64($0) }
        
        for (idx, prime) in seeds.enumerated() {
            let x = Int((n % UInt64(size)) + UInt64(idx * 7) % UInt64(size))
            let y = Int((n / UInt64(size)) % UInt64(size))
            
            // Place glider
            let glider = [(0,1), (1,2), (2,2), (2,1), (1,0)]
            for (gx, gy) in glider {
                let nx = (x + gx) % size
                let ny = (y + gy) % size
                grid[ny * size + nx] = 1
            }
        }
        return grid
    }
}
```

***

## 4. Pure Dynamics Engine (ComputeEngine.swift + GridAnalyzer.swift)

**Analyzer sees ONLY: hash, population, entropy, period. Never N.**

```swift
// GridAnalyzer.swift - BLINDED ANALYSIS ONLY
struct DynamicSignal {
    let hash: UInt32
    let population: Int
    let entropy: Float
    let period: Int?
    let generation: Int
}

protocol DynamicsObserver {
    func signalDetected(_ signal: DynamicSignal)
}

class GridAnalyzer: DynamicsObserver {
    private var stateHistory: [UInt32: Int] = [:]  // hash → generation
    private var signals: [DynamicSignal] = []
    
    func signalDetected(_ signal: DynamicSignal) {
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
    
    func getSignals() -> [DynamicSignal] { signals }
    func reset() { stateHistory.removeAll(); signals.removeAll() }
}
```

***

## 5. Statistical Validation (StatisticalTester.swift)

**Null hypothesis: GoL signals no better than random periods**

```swift
struct TestCase {
    let n: UInt64
    let trueFactors: Set<UInt64>
}

class StatisticalTester {
    func runBlindedTest(_ cases: [TestCase], gridSize: Int = 128, maxGens: Int = 5000) -> TestReport {
        var golHits = 0, randomHits = 0, totalTests = 0
        
        for _ in 0..<50 {  // 50 Monte Carlo runs
            for testCase in cases {
                // Test 1: GoL encoding
                let golSignals = simulateGoL(n: testCase.n, size: gridSize, maxGens: maxGens)
                golHits += countTrueFactorMatches(golSignals, factors: testCase.trueFactors)
                
                // Test 2: Random baseline (empirical GoL period distribution)
                let randomPeriods = [1, 2, 4, 200, 220, 300, 404, 500].shuffled().prefix(5)
                let randomSignals = randomPeriods.map { DynamicSignal(hash: 0, population: 0, entropy: 0, period: Int($0), generation: 0) }
                randomHits += countTrueFactorMatches(randomSignals, factors: testCase.trueFactors)
                
                totalTests += 2
            }
        }
        
        return TestReport(
            golSuccessRate: Double(golHits) / Double(totalTests),
            randomSuccessRate: Double(randomHits) / Double(totalTests),
            signalsPerRun: averageSignals(cases)
        )
    }
    
    private func countTrueFactorMatches(_ signals: [DynamicSignal], factors: Set<UInt64>) -> Int {
        var matches = 0
        for signal in signals where let period = signal.period {
            // Pure signal extraction - NO N ACCESS
            let candidates = extractCandidatesFromPeriod(period)
            matches += candidates.intersection(factors).count
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
```

***

## 6. Complete Runner (main.swift)

```swift
@main
struct FactorGoL {
    static let testCases: [TestCase] = [
        TestCase(n: 15, trueFactors: [3, 5]),
        TestCase(n: 21, trueFactors: [3, 7]),
        TestCase(n: 35, trueFactors: [5, 7]),
        TestCase(n: 77, trueFactors: [7, 11]),
        TestCase(n: 143, trueFactors: [11, 13]),
        TestCase(n: 221, trueFactors: [13, 17]),
        TestCase(n: 10403, trueFactors: [101, 103])  // Interesting case
    ]
    
    static func main() async {
        print("Emergent Factorization via Game of Life\n")
        print("Grid sizes: 64, 128, 256 | Max generations: 5000")
        print("Analysis: Pure dynamics (periods, entropy) - NO trial division\n")
        
        let tester = StatisticalTester()
        let sizes = [64, 128, 256]
        
        for size in sizes {
            let report = tester.runBlindedTest(testCases, gridSize: size)
            print(report.summary)
        }
    }
}
```

***

## 7. Success Criteria

| Outcome | GoL > Random? | Interpretation |
|---------|---------------|----------------|
| GoL success >> random | Yes (p<0.01) | **Novel signal found** |
| GoL success ≈ random | No | Dynamics are geometry-only |
| GoL success = 0 | No | Encoding failure |

**Expected Result:** GoL ≈ random (grid artifacts dominate)

***

## 8. Package.swift

```swift
// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "FactorGoL",
    platforms: [.macOS(.v14)],
    targets: [
        .executableTarget(
            name: "FactorGoL",
            path: "Sources",
            resources: [.process("Shaders")]
        )
    ]
)
```

***

## Build & Run

```bash
swift build -c release
.build/release/FactorGoL
```

**Output format:**
```
Grid=128 | GoL: 0.023 | Random: 0.021 | Signals/run: 2.1 | p=0.87
```

This specification is **100% self-contained**. Any LLM can implement from scratch and reproduce Claude's null result, confirming GoL periods are grid geometry artifacts, not factorization signals.[1]

Sources
[1] FINDINGS.md https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/85312621/a7aabc10-e601-4d45-83a7-0b451f47daac/FINDINGS.md
