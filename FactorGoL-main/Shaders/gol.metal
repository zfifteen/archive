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
    
    