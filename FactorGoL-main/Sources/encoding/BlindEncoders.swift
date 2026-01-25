import Foundation

public struct BlindEncoder {
    public static func encode(_ n: UInt64, gridSize: Int) -> [UInt8] {
        let strategies = [
            binaryFractal(n: n, size: gridSize),
            residueWave(n: n, size: gridSize),
            dimensionalSeed(n: n, size: gridSize)
        ]
        return strategies.randomElement()!
    }
}

private extension BlindEncoder {
    static func mirror(_ s: String) -> String {
        return String(s.reversed())
    }
    
    // Strategy 1: Binary fractal - N's bits → spatial frequency
    static func binaryFractal(n: UInt64, size: Int) -> [UInt8] {
        var grid = [UInt8](repeating: 0, count: size * size)
        let bits = mirror(String(n, radix: 2))
        
        for i in 0..<size {
            for j in 0..<size {
                let bitIdx = (i * 37 + j * 73) % bits.count
                let r = hypot(Double(i - size/2), Double(j - size/2)) / Double(size)
                let bitChar = bits[bits.index(bits.startIndex, offsetBy: bitIdx)]
                grid[j * size + i] = (bitChar == "1" && sin(r * .pi * 8) > 0) ? 1 : 0
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
        
        // CHAOS FIX: Scale gliders inversely with area
        let maxGliders = max(3, 1200 / size)  // 101→12, 256→4, 512→3
        let primes: [UInt64] = [7, 11, 13, 17, 19, 23]
        
        for i in 0..<maxGliders {
            let _ = primes[i % primes.count]
            let x = Int((n % UInt64(size)) + UInt64(i * 17) % UInt64(size))
            let y = Int((n / UInt64(size)) % UInt64(size))
            
            // Place glider (updated pattern)
            let glider: [(Int, Int)] = [(0,0), (1,0), (2,0), (2,1), (1,2)]
            for (gx, gy) in glider {
                let nx = (x + gx) % size
                let ny = (y + gy) % size
                grid[ny * size + nx] = 1
            }
        }
        return grid
    }
}