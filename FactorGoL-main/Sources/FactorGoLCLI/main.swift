import Foundation
import FactorGoLCore

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
    
    static let resonantCases: [TestCase] = [
        TestCase(n: 101*103, trueFactors: [101, 103]),
        TestCase(n: 1009*1013, trueFactors: [1009, 1013]),
        TestCase(n: 997*1009, trueFactors: [997, 1009])
    ]
    
    static func main() {
        run()
    }
    
    static func run() {
        print("Emergent Factorization via Game of Life\n")
        print("Testing resonant cases with grid_size ≈ √N\n")
        
        guard let tester = StatisticalTester() else {
            print("Failed to initialize Metal compute engine")
            return
        }
        
        for testCase in resonantCases {
            let gridSize = Int(sqrt(Double(testCase.n)))
            let maxGens = max(2000, gridSize * 8)
            print("Testing N=\(testCase.n), gridSize=\(gridSize), maxGens=\(maxGens)")
            let report = tester.runBlindedTest([testCase], gridSize: gridSize, maxGens: maxGens)
            print(report.summary)
        }
    }
}