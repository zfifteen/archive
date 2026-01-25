import Metal
import Foundation

public class ComputeEngine {
    let device: MTLDevice
    let commandQueue: MTLCommandQueue
    let lifeStepPipeline: MTLComputePipelineState
    let hashPipeline: MTLComputePipelineState
    let entropyPipeline: MTLComputePipelineState
    let debrisPipeline: MTLComputePipelineState
    
    public init?() {
        guard let device = MTLCreateSystemDefaultDevice() else { return nil }
        self.device = device
        self.commandQueue = device.makeCommandQueue()!
        
        let shaderSource = """
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
    entropy[idx] = localEntropy;
}

// NEW: Debris suppression - kills clusters, preserves gliders
kernel void suppress_debris(
    device uint8_t* grid [[buffer(0)]],
    constant uint2& gridSize [[buffer(1)]],
    constant float& maxDensity [[buffer(2)]],  // 0.08 = 8% local threshold
    uint2 tid [[thread_position_in_grid]]
) {
    if (tid.x >= gridSize.x || tid.y >= gridSize.y) return;
    
    uint idx = tid.y * gridSize.x + tid.x;
    if (grid[idx] == 0) return;  // Dead cells skip
    
    // 5x5 local density (debris detector)
    float localRho = 0;
    for (int dy = -2; dy <= 2; dy++) {
        for (int dx = -2; dx <= 2; dx++) {
            uint2 npos = uint2(
                (tid.x + dx + gridSize.x) % gridSize.x,
                (tid.y + dy + gridSize.y) % gridSize.y
            );
            localRho += float(grid[npos.y * gridSize.x + npos.x]) / 25.0;
        }
    }
    
    // Kill debris: high density + clustered (not isolated glider)
    if (localRho > maxDensity) {
        int deadNeighbors = 0;
        for (int dy = -1; dy <= 1; dy++) {
            for (int dx = -1; dx <= 1; dx++) {
                if (dx == 0 && dy == 0) continue;
                uint2 npos = uint2(
                    (tid.x + dx + gridSize.x) % gridSize.x,
                    (tid.y + dy + gridSize.y) % gridSize.y
                );
                deadNeighbors += (grid[npos.y * gridSize.x + npos.x] == 0);
            }
        }
        // Gliders have ≥6 dead neighbors, debris <4
        if (deadNeighbors < 4) grid[idx] = 0;
    }
}
"""
        
        let library: MTLLibrary
        do {
            library = try device.makeLibrary(source: shaderSource, options: nil)
        } catch {
            print("Failed to create library: \(error)")
            return nil
        }
        
        let lifeStepFunction = library.makeFunction(name: "life_step")!
        let hashFunction = library.makeFunction(name: "grid_hash")!
        let entropyFunction = library.makeFunction(name: "spatial_entropy")!
        let debrisFunction = library.makeFunction(name: "suppress_debris")!
        
        do {
            lifeStepPipeline = try device.makeComputePipelineState(function: lifeStepFunction)
            hashPipeline = try device.makeComputePipelineState(function: hashFunction)
            entropyPipeline = try device.makeComputePipelineState(function: entropyFunction)
            debrisPipeline = try device.makeComputePipelineState(function: debrisFunction)
        } catch {
            print("Failed to create pipelines: \(error)")
            return nil
        }
    }
    
    public func simulateGoL(n: UInt64, size: Int, maxGens: Int, debrisThreshold: Float = 0.08) -> ([DynamicSignal], [UInt8]) {
        let initialGrid = BlindEncoder.encode(n, gridSize: size)
        let analyzer = GridAnalyzer()
        
        guard let gridA = device.makeBuffer(bytes: initialGrid, length: size * size, options: []),
              let gridB = device.makeBuffer(length: size * size, options: []) else {
            return ([], [])
        }
        
        var bufferA = gridA
        var bufferB = gridB
        
        for gen in 0..<maxGens {
            // Life step
            let commandBuffer = commandQueue.makeCommandBuffer()!
            let lifeEncoder = commandBuffer.makeComputeCommandEncoder()!
            lifeEncoder.setComputePipelineState(lifeStepPipeline)
            lifeEncoder.setBuffer(bufferA, offset: 0, index: 0)
            lifeEncoder.setBuffer(bufferB, offset: 0, index: 1)
            var gridSizeVec = SIMD2<UInt32>(UInt32(size), UInt32(size))
            lifeEncoder.setBytes(&gridSizeVec, length: MemoryLayout<SIMD2<UInt32>>.size, index: 2)
            let threadgroups = MTLSize(width: (size + 15)/16, height: (size + 15)/16, depth: 1)
            let threadsPerGroup = MTLSize(width: 16, height: 16, depth: 1)
            lifeEncoder.dispatchThreadgroups(threadgroups, threadsPerThreadgroup: threadsPerGroup)
            lifeEncoder.endEncoding()
            commandBuffer.commit()
            commandBuffer.waitUntilCompleted()
            
            // Debris suppression disabled for factorization signals
            // if gen > 0 && gen % 40 == 0 {
            //     ...
            // }
            
            // Compute hash
            let hashBuffer = device.makeBuffer(length: 4, options: [])!
            // Reset hash buffer to 0
            memset(hashBuffer.contents(), 0, 4)
            let hashCommandBuffer = commandQueue.makeCommandBuffer()!
            let hashEncoder = hashCommandBuffer.makeComputeCommandEncoder()!
            hashEncoder.setComputePipelineState(hashPipeline)
            hashEncoder.setBuffer(bufferB, offset: 0, index: 0)
            hashEncoder.setBuffer(hashBuffer, offset: 0, index: 1)
            var totalSize = UInt32(size * size)
            hashEncoder.setBytes(&totalSize, length: 4, index: 2)
            let tg = MTLSize(width: (size * size + 255) / 256, height: 1, depth: 1)
            let tptg = MTLSize(width: 256, height: 1, depth: 1)
            hashEncoder.dispatchThreadgroups(tg, threadsPerThreadgroup: tptg)
            hashEncoder.endEncoding()
            hashCommandBuffer.commit()
            hashCommandBuffer.waitUntilCompleted()
            let hash = hashBuffer.contents().load(as: UInt32.self)
            
            // Population
            let gridPtr = bufferB.contents().bindMemory(to: UInt8.self, capacity: size * size)
            let population = (0..<size * size).reduce(0) { $0 + Int(gridPtr[$1]) }

            // Entropy
            let entropyBuffer = device.makeBuffer(length: size * size * 4, options: [])!
            let entropyCommandBuffer = commandQueue.makeCommandBuffer()!
            let entropyEncoder = entropyCommandBuffer.makeComputeCommandEncoder()!
            entropyEncoder.setComputePipelineState(entropyPipeline)
            entropyEncoder.setBuffer(bufferB, offset: 0, index: 0)
            entropyEncoder.setBuffer(entropyBuffer, offset: 0, index: 1)
            entropyEncoder.setBytes(&gridSizeVec, length: 8, index: 2)
            entropyEncoder.dispatchThreadgroups(threadgroups, threadsPerThreadgroup: threadsPerGroup)
            entropyEncoder.endEncoding()
            entropyCommandBuffer.commit()
            entropyCommandBuffer.waitUntilCompleted()
            let entropyPtr = entropyBuffer.contents().bindMemory(to: Float.self, capacity: size * size)
            let entropy = (0..<size * size).reduce(0.0) { $0 + entropyPtr[$1] }
            
            let signal = DynamicSignal(hash: hash, population: population, entropy: entropy, period: nil, generation: gen)
            analyzer.signalDetected(signal)
            
            // Swap buffers
            swap(&bufferA, &bufferB)
        }

        // Get final grid
        let gridPtr = bufferB.contents().bindMemory(to: UInt8.self, capacity: size * size)
        let finalGrid = Array(UnsafeBufferPointer(start: gridPtr, count: size * size))

        return (analyzer.getSignals(), finalGrid)
    }
}
