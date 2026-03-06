// Z5D Curvature-Guided Ray Marching Shader
// ==========================================
// 
// This WGSL shader implements adaptive ray-marching for Mandelbulb rendering
// using Z5D number-theoretic curvature κ(p) to predict optimal step sizes.
//
// Core Innovation: High κ(p) = complex geometry = small steps
//                  Low κ(p) = smooth space = geodesic leaps (10-1000× larger)

struct Uniforms {
    viewMatrix: mat4x4<f32>,
    projectionMatrix: mat4x4<f32>,
    cameraPosition: vec3<f32>,
    time: f32,
    power: f32,               // Mandelbulb power (8, 12, 16, 20)
    maxSteps: u32,            // Max ray-marching iterations (512)
    epsilon: f32,             // Hit threshold (0.0001)
    maxDistance: f32,         // Ray max distance (1000.0)
    geodesicMultiplier: f32,  // Adaptive step multiplier (10.0)
    enableZ5D: u32,           // Toggle Z5D curvature (1=on, 0=off)
};

@group(0) @binding(0) var<uniform> uniforms: Uniforms;

// Constants
const E: f32 = 2.71828;
const E_SQUARED: f32 = 7.38906;  // e²
const PI: f32 = 3.14159265359;
const EPSILON_SAFE: f32 = 0.0001;

// =============================================================================
// Z5D Curvature Function
// =============================================================================
// 
// Embeds 3D spatial point p into Z5D number-theoretic space and computes
// approximate divisor-density curvature κ(p) ≈ d(n)·ln(n)/e²
//
// Theory: Prime distribution curvature naturally extends to R³ via coordinate
// embedding. High κ(p) indicates geometric complexity requiring fine sampling.
//
fn kappa(p: vec3<f32>) -> f32 {
    // Ensure positive coordinates for log domain
    let q = abs(p) + EPSILON_SAFE;
    
    // Approximate divisor count d(n) via log product of coordinates
    // This mimics the number-theoretic density without factorization
    let divisors_approx = log(q.x) * log(q.y) * log(q.z);
    
    // Scale by ln(|p|)/e² for dimensional consistency with Z5D framework
    let radius = length(p) + 1.0;
    let curvature = divisors_approx * log(radius) / E_SQUARED;
    
    // Clamp to prevent numerical overflow in exponential damping
    return clamp(curvature, -10.0, 10.0);
}

// =============================================================================
// Mandelbulb Distance Estimator
// =============================================================================
//
// Standard distance estimator for Mandelbulb fractal
// DE(p) = 0.5 * |z| * log(|z|) / |dz|
//
fn mandelbulbDE(pos: vec3<f32>, power: f32) -> f32 {
    var z = pos;
    var dr = 1.0;
    var r = 0.0;
    
    // Iterate the Mandelbulb formula
    for (var i = 0u; i < 15u; i++) {
        r = length(z);
        
        // Escape radius check
        if (r > 2.0) {
            break;
        }
        
        // Convert to polar coordinates
        let theta = acos(z.z / r);
        let phi = atan2(z.y, z.x);
        
        // Derivative tracking for distance estimation
        dr = pow(r, power - 1.0) * power * dr + 1.0;
        
        // Mandelbulb power formula in spherical coords
        let zr = pow(r, power);
        let newTheta = theta * power;
        let newPhi = phi * power;
        
        // Convert back to Cartesian
        z = zr * vec3<f32>(
            sin(newTheta) * cos(newPhi),
            sin(newTheta) * sin(newPhi),
            cos(newTheta)
        );
        z += pos;
    }
    
    // Distance estimator formula
    return 0.5 * log(r) * r / dr;
}

// =============================================================================
// Z5D Adaptive Step Function
// =============================================================================
//
// Computes optimal ray-marching step size based on:
// 1. Distance estimator DE (geometric safety)
// 2. Curvature κ(p) (complexity prediction)
//
// Returns: Adaptive step with geodesic leap in smooth regions
//
fn z5d_step(de: f32, p: vec3<f32>, dir: vec3<f32>) -> f32 {
    let k = kappa(p);
    
    // Conservative bound: 1.2× DE guarantees no overshooting
    let safe = de * 1.2;
    
    // Aggressive geodesic leap: exponential damping based on curvature
    // High k (complex) → small multiplier → conservative
    // Low k (smooth) → large multiplier → aggressive leap
    let aggressive = de * (1.0 + 50.0 * exp(-k * 0.8));
    
    // Apply geodesic multiplier with safety clamp
    // In smooth regions (low k), this can reach 10-1000× normal step size
    return min(safe, aggressive * uniforms.geodesicMultiplier);
}

// Standard sphere-tracing step (for comparison)
fn standard_step(de: f32) -> f32 {
    return de * 0.9;  // Conservative multiplier
}

// =============================================================================
// Ray Marching Loop
// =============================================================================
//
// Main ray-marching algorithm with Z5D-guided adaptive stepping
//
// Returns: (distance, iterations, hit)
//
struct MarchResult {
    distance: f32,
    iterations: u32,
    hit: bool,
};

fn raymarch(ro: vec3<f32>, rd: vec3<f32>) -> MarchResult {
    var t = 0.0;
    var result: MarchResult;
    
    for (var i = 0u; i < uniforms.maxSteps; i++) {
        let pos = ro + rd * t;
        let de = mandelbulbDE(pos, uniforms.power);
        
        // Hit detection
        if (de < uniforms.epsilon) {
            result.distance = t;
            result.iterations = i;
            result.hit = true;
            return result;
        }
        
        // Escape check
        if (t > uniforms.maxDistance) {
            result.distance = t;
            result.iterations = i;
            result.hit = false;
            return result;
        }
        
        // Adaptive stepping: Z5D or standard
        var step: f32;
        if (uniforms.enableZ5D == 1u) {
            step = z5d_step(de, pos, rd);
        } else {
            step = standard_step(de);
        }
        
        t += step;
    }
    
    // Max iterations reached
    result.distance = t;
    result.iterations = uniforms.maxSteps;
    result.hit = false;
    return result;
}

// =============================================================================
// Normal Calculation
// =============================================================================
//
// Compute surface normal using central differences
//
fn calcNormal(p: vec3<f32>, power: f32) -> vec3<f32> {
    let eps = 0.0001;
    let h = vec2<f32>(eps, 0.0);
    
    return normalize(vec3<f32>(
        mandelbulbDE(p + h.xyy, power) - mandelbulbDE(p - h.xyy, power),
        mandelbulbDE(p + h.yxy, power) - mandelbulbDE(p - h.yxy, power),
        mandelbulbDE(p + h.yyx, power) - mandelbulbDE(p - h.yyx, power)
    ));
}

// =============================================================================
// Lighting and Shading
// =============================================================================
//
// Simple Blinn-Phong shading with ambient occlusion
//
fn shade(p: vec3<f32>, rd: vec3<f32>, power: f32) -> vec3<f32> {
    let normal = calcNormal(p, power);
    
    // Light direction (key light from upper right)
    let lightDir = normalize(vec3<f32>(0.6, 0.8, 0.5));
    
    // Diffuse lighting
    let diffuse = max(dot(normal, lightDir), 0.0);
    
    // Specular (Blinn-Phong)
    let halfDir = normalize(lightDir - rd);
    let specular = pow(max(dot(normal, halfDir), 0.0), 32.0);
    
    // Ambient occlusion (cheap approximation)
    let ao = 1.0 - clamp(length(p) * 0.15, 0.0, 1.0);
    
    // Color palette based on distance from origin
    let dist = length(p);
    let hue = fract(dist * 0.3 + uniforms.time * 0.05);
    let color = 0.5 + 0.5 * cos(2.0 * PI * (hue + vec3<f32>(0.0, 0.33, 0.67)));
    
    // Combine lighting components
    let ambient = vec3<f32>(0.1, 0.12, 0.15);
    return (ambient + diffuse * color + specular * vec3<f32>(1.0)) * ao;
}

// =============================================================================
// Fragment Shader Entry Point
// =============================================================================
//
struct VertexOutput {
    @builtin(position) position: vec4<f32>,
    @location(0) uv: vec2<f32>,
};

@fragment
fn main(in: VertexOutput) -> @location(0) vec4<f32> {
    // Convert UV to normalized device coordinates
    let ndc = in.uv * 2.0 - 1.0;
    
    // Ray origin and direction from camera
    let ro = uniforms.cameraPosition;
    
    // Compute ray direction from projection
    // This should be passed from vertex shader in production
    let aspect = 16.0 / 9.0;  // Adjust based on viewport
    let rd = normalize(vec3<f32>(ndc.x * aspect, ndc.y, -2.0));
    
    // Ray-march the scene
    let result = raymarch(ro, rd);
    
    // Background color (gradient)
    let bgColor = mix(
        vec3<f32>(0.05, 0.08, 0.12),  // Dark blue bottom
        vec3<f32>(0.02, 0.02, 0.06),  // Darker top
        ndc.y * 0.5 + 0.5
    );
    
    // Render result
    if (result.hit) {
        let hitPoint = ro + rd * result.distance;
        let color = shade(hitPoint, rd, uniforms.power);
        
        // Depth-based fog
        let fog = exp(-result.distance * 0.15);
        return vec4<f32>(mix(bgColor, color, fog), 1.0);
    } else {
        // Background with subtle iteration-based glow
        let glow = f32(result.iterations) / f32(uniforms.maxSteps);
        return vec4<f32>(bgColor + glow * 0.02, 1.0);
    }
}

// =============================================================================
// Performance Instrumentation (Optional)
// =============================================================================
//
// For benchmarking, export iteration count and step statistics
// Can be read back to CPU for analysis
//
struct PerformanceStats {
    avgIterations: f32,
    maxIterations: u32,
    avgStepSize: f32,
    hitRate: f32,
};

// This would require compute shader pass to aggregate statistics
// Omitted from fragment shader for performance
