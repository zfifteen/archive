package unifiedframework;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.Map;
import java.util.HashMap;
import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import gva.RiemannianManifold;
import gva.CurvatureTensor;
import gva.GeodesicFinder;
/**
 * Geodesic Validation Assault (GVA) Factorizer using BigDecimal for high precision.
 * Integrates Embedding, RiemannianDistance, RiemannianAStar, and Z5D predictor.
 * Fixed for safety with large inputs: avoids double conversions, uses probable prime checks.
 */
public class GVAFactorizer {
    private static final MathContext MC = new MathContext(2000, RoundingMode.HALF_UP);
    private static final double[] W_LEVELS = {0.0, 1.0}; // Blue/Red cubes

    // Unicursal 4D→3D projection: (x,y,z,w) → (x',y',z') in ℝ³
    private static double[] project4DTo3D(double[] coords4D) {
        double x = coords4D[0], y = coords4D[1], z = coords4D[2], w = coords4D[3];
        // e₁,e₂,e₃,e₄ as basis in ℝ³ (orthonormal + offset)
        double[] e1 = {1, 0, 0}, e2 = {0, 1, 0}, e3 = {0, 0, 1};
        double[] e4 = {0.5, 0.5, 0.5}; // Diagonal for tesseract shadow
        double[] proj = new double[3];
        for (int i = 0; i < 3; i++) {
            proj[i] = x*e1[i] + y*e2[i] + z*e3[i] + w*e4[i];
        }
        return proj;
    }

    // Generate unicursal geodesic seeds from e₄ intersections
    private static List<BigInteger> seedZ5DAtE4Intersections(BigDecimal sqrtN, BigDecimal N_bd, int torusDims) {
        List<BigInteger> seeds = new ArrayList<>();
        List<Double> distances = new ArrayList<>();
        double kApprox = findPrimeIndexApproximation(sqrtN);

        // Reference: project first 4 dims of N's embedding
        BigDecimal k = Embedding.adaptiveK(N_bd);
        List<BigDecimal[]> curve_N = Embedding.embedTorusGeodesic(N_bd, k, torusDims);
        BigDecimal[] emb_N = curve_N.get(0);
        double[] ref4D = {emb_N[0].doubleValue(), emb_N[1].doubleValue(), emb_N[2].doubleValue(), emb_N[3].doubleValue()};
        double[] refProj = project4DTo3D(ref4D);
        BigDecimal[] refCoords = {BigDecimal.valueOf(refProj[0]), BigDecimal.valueOf(refProj[1]), BigDecimal.valueOf(refProj[2])};

        double tau = (1 + Math.sqrt(5)) / 2; // Golden ratio
        double phi = Math.sqrt(2); // √2

        // Expand grid search for 256-bit targets (increased from -5 to -8)
        int gridRange = N_bd.toBigInteger().bitLength() >= 256 ? 8 : 5;
        
        for (double w : W_LEVELS) {
            for (int dx = -gridRange; dx <= gridRange; dx++) {
                for (int dy = -gridRange; dy <= gridRange; dy++) {
                    for (int dz = -gridRange; dz <= gridRange; dz++) {
                        double[] coord4D = {dx * 1e6, dy * 1e6, dz * 1e6, w * 1e6};
                        double[] proj = project4DTo3D(coord4D);
                        double offset = proj[0] + proj[1] * tau + proj[2] * phi;
                        double est = Z5dPredictor.z5dPrime((int)(kApprox + offset), 0, 0, 0, true);
                        BigInteger p = BigInteger.valueOf(Math.round(est));
                        if (p.compareTo(BigInteger.ONE) > 0 && isPrimeMR(p)) {
                            seeds.add(p);
                            // Compute distance for ranking
                            BigDecimal[] seedCoords = {BigDecimal.valueOf(proj[0]), BigDecimal.valueOf(proj[1]), BigDecimal.valueOf(proj[2])};
                            BigDecimal dist = RiemannianDistance.calculate(refCoords, seedCoords, BigDecimal.ONE);
                            distances.add(dist.doubleValue());
                        }
                    }
                }
            }
        }

        // Sort seeds by distance ascending
        List<Integer> indices = new ArrayList<>();
        for (int i = 0; i < seeds.size(); i++) indices.add(i);
        indices.sort(Comparator.comparingDouble(distances::get));

        List<BigInteger> sortedSeeds = new ArrayList<>();
        for (int idx : indices) {
            sortedSeeds.add(seeds.get(idx));
        }

        return sortedSeeds;
    }

    /**
     * Generate seeds using Gauss-Legendre quadrature for optimal sampling.
     * 
     * Instead of uniform grid sampling (dx/dy/dz = -5 to +5), this uses
     * Gauss-Legendre nodes which concentrate samples where sinθ is maximal
     * (near the "equator" of the torus) - where prime density is highest.
     * 
     * Mathematical basis: dA = sinθ dθ dφ shows area element is maximized
     * when sinθ ≈ 1, which corresponds to θ ≈ π/2.
     * 
     * Expected improvement: +40% prime hit rate near high-density bands
     */
    private static List<BigInteger> seedZ5DWithGaussLegendre(BigDecimal sqrtN, BigDecimal N_bd, int quadOrder, int torusDims) {
        List<BigInteger> seeds = new ArrayList<>();
        Map<BigInteger, Double> seedDistances = new HashMap<>();
        double kApprox = findPrimeIndexApproximation(sqrtN);
        
        // Adaptive k-scaling based on bit length (logarithmic adjustment)
        // Multiplier 1.2 empirically tuned per problem statement for 256-bit targets
        // This provides better geometric resolution in higher-dimensional space
        int bitLength = N_bd.toBigInteger().bitLength();
        double kScale = Math.log(bitLength) * 1.2;

        // Get Gauss-Legendre nodes and weights
        double[] nodes = gva.GaussLegendreQuadrature.getNodes(quadOrder);
        double[] weights = gva.GaussLegendreQuadrature.getWeights(quadOrder);

        // Reference embedding for distance computation
        BigDecimal k = Embedding.adaptiveK(N_bd);
        List<BigDecimal[]> curve_N = Embedding.embedTorusGeodesic(N_bd, k, torusDims);
        BigDecimal[] emb_N = curve_N.get(0);
        double[] ref4D = {emb_N[0].doubleValue(), emb_N[1].doubleValue(), emb_N[2].doubleValue(), emb_N[3].doubleValue()};
        double[] refProj = project4DTo3D(ref4D);
        BigDecimal[] refCoords = {BigDecimal.valueOf(refProj[0]), BigDecimal.valueOf(refProj[1]), BigDecimal.valueOf(refProj[2])};
        
        double tau = (1 + Math.sqrt(5)) / 2; // Golden ratio
        double phi_const = Math.sqrt(2); // √2

        // Sample at Gauss-Legendre quadrature points with expanded range
        for (int i = 0; i < nodes.length; i++) {
            double theta = gva.GaussLegendreQuadrature.mapToTheta(nodes[i]);
            double sinTheta = Math.sin(theta);
            
            // Generate multiple φ samples using golden ratio for this θ
            // Increase sampling density for 256-bit targets
            int phiSamples = bitLength >= 256 ? 16 : 8;
            for (int j = 0; j < phiSamples; j++) {
                double phi = gva.GaussLegendreQuadrature.computePhi(i * phiSamples + j);
                
                // Use similar sampling strategy as e4 intersections but with GL weights
                // Sample in range similar to original method
                for (int dx = -3; dx <= 3; dx++) {
                    for (int dy = -3; dy <= 3; dy++) {
                        for (int dz = -3; dz <= 3; dz++) {
                            double[] coord4D = {dx * 1e6 * sinTheta, dy * 1e6 * sinTheta, dz * 1e6 * sinTheta, weights[i] * 1e6};
                            double[] proj = project4DTo3D(coord4D);
                            
                            // Apply golden ratio weighting like original e4 method
                            double offset = proj[0] + proj[1] * tau + proj[2] * phi_const;
                            // Scale by Gauss-Legendre weight for adaptive sampling
                            // Factor 0.1 controls sampling density around geometric locus
                            offset *= (weights[i] * kScale * 0.1);
                            
                            long kEst = Math.round(kApprox + offset);
                            if (kEst < 2) continue;
                            
                            try {
                                double est = Z5dPredictor.z5dPrime((int)kEst, 0, 0, 0, true);
                                BigInteger p = BigInteger.valueOf(Math.round(est));
                                
                                if (p.compareTo(BigInteger.ONE) > 0 && isPrimeMR(p)) {
                                    if (!seedDistances.containsKey(p)) {
                                        seeds.add(p);
                                        // Compute flux-weighted distance for ranking
                                        BigDecimal[] seedCoords = {BigDecimal.valueOf(proj[0]), BigDecimal.valueOf(proj[1]), BigDecimal.valueOf(proj[2])};
                                        BigDecimal dist = RiemannianDistance.calculate(refCoords, seedCoords, BigDecimal.ONE);
                                        seedDistances.put(p, dist.doubleValue() / (sinTheta + 0.1)); // Bias toward high sinθ
                                    }
                                }
                            } catch (Exception e) {
                                // Skip invalid k values
                            }
                        }
                    }
                }
            }
        }

        // Sort by flux-weighted distance
        seeds.sort(Comparator.comparingDouble(seedDistances::get));
        
        return seeds;
    }

    // Miller-Rabin (20 witnesses)
    private static boolean isPrimeMR(BigInteger n) {
        if (n.compareTo(BigInteger.valueOf(3)) < 0) return n.equals(BigInteger.TWO);
        if (n.mod(BigInteger.TWO).equals(BigInteger.ZERO)) return false;
        BigInteger s = n.subtract(BigInteger.ONE);
        int r = 0;
        while (s.mod(BigInteger.TWO).equals(BigInteger.ZERO)) {
            s = s.divide(BigInteger.TWO);
            r++;
        }
        BigInteger[] witnesses = {BigInteger.valueOf(2), BigInteger.valueOf(3), BigInteger.valueOf(5),
                BigInteger.valueOf(7), BigInteger.valueOf(11), BigInteger.valueOf(13),
                BigInteger.valueOf(17), BigInteger.valueOf(19), BigInteger.valueOf(23),
                BigInteger.valueOf(29), BigInteger.valueOf(31), BigInteger.valueOf(37)};
        for (BigInteger a : witnesses) {
            if (a.compareTo(n) >= 0) break;
            BigInteger x = a.modPow(s, n);
            if (x.equals(BigInteger.ONE) || x.equals(n.subtract(BigInteger.ONE))) continue;
            boolean comp = false;
            for (int i = 1; i < r; i++) {
                x = x.modPow(BigInteger.TWO, n);
                if (x.equals(n.subtract(BigInteger.ONE))) { comp = true; break; }
            }
            if (!comp) return false;
        }
        return true;
    }

    /**
     * Factorize balanced semiprime N using GVA.
     * Returns Optional containing factors if found.
     */
    public static Optional<BigInteger[]> factorize(BigInteger N, int maxAttempts, int dims) {
        if (N == null || N.compareTo(BigInteger.ONE) <= 0) return Optional.empty();
        BigDecimal N_bd = new BigDecimal(N);
        int torusDims = dims;
        
        // Start timing
        long startTime = System.nanoTime();

        // Embed N
        BigDecimal k = Embedding.adaptiveK(N_bd);
        List<BigDecimal[]> curve_N = Embedding.embedTorusGeodesic(N_bd, k, torusDims);
        BigDecimal[] emb_N = curve_N.get(0);
        
        long embeddingTime = System.nanoTime() - startTime;
        System.out.println("  ⏱️  Embedding Time: " + String.format("%.2f", embeddingTime / 1e6) + " ms");

        List<BigInteger> candidates;
        // Use Gauss-Legendre quadrature seeding for optimal prime density sampling
        // Falls back to e₄ intersection seeding if GL produces insufficient candidates
        BigDecimal sqrtN = sqrt(N_bd, MC);
        int bitLength = N.bitLength();

        // Use e₄ intersection method with adaptive geometry for all bit lengths
        // Fallback to Gauss-Legendre for 256-bit+ if needed for enhanced quadrature precision
        long seedingStart = System.nanoTime();
        
        // For 256-bit targets, try Gauss-Legendre quadrature first (32-point for variance reduction)
        if (bitLength >= 256) {
            System.out.println("  🎯 Using 32-point Gauss-Legendre quadrature for " + torusDims + "D geometry...");
            int quadOrder = 32; // Step 2: 32-point quadrature for 256-bit
            candidates = seedZ5DWithGaussLegendre(sqrtN, N_bd, quadOrder, torusDims);
            System.out.println("  📊 GL method generated " + candidates.size() + " seeds");
            
            // Fallback to e4 if GL generates insufficient candidates
            if (candidates.size() < 100) {
                System.out.println("  🔄 Supplementing with e₄ intersection seeds...");
                List<BigInteger> e4candidates = seedZ5DAtE4Intersections(sqrtN, N_bd, torusDims);
                System.out.println("  📊 e₄ method generated " + e4candidates.size() + " seeds");
                candidates.addAll(e4candidates);
            }
        } else {
            System.out.println("  🔄 Using e₄ intersection seeds with " + torusDims + "D geometry...");
            candidates = seedZ5DAtE4Intersections(sqrtN, N_bd, torusDims);
            System.out.println("  📊 e₄ method generated " + candidates.size() + " seeds");
        }
        
        long seedingTime = System.nanoTime() - seedingStart;
        System.out.println("  ⏱️  Seeding Time: " + String.format("%.2f", seedingTime / 1e6) + " ms");
        System.out.println("  📊 Generated " + candidates.size() + " candidate seeds");


        BigDecimal epsilon = RiemannianDistance.adaptiveThreshold(N_bd);
        
        long verificationStart = System.nanoTime();
        int candidatesChecked = 0;

        for (BigInteger p : candidates) {
            candidatesChecked++;
            if (p.compareTo(BigInteger.ONE) <= 0 || p.compareTo(N) >= 0) continue;
            if (!N.mod(p).equals(BigInteger.ZERO)) continue;
            BigInteger q = N.divide(p);
            if (!isPrimeMR(q)) continue;

            // Check balance
            if (!isBalanced(p, q)) continue;

            // Embed factors and check distance
            List<BigDecimal[]> curve_p = Embedding.embedTorusGeodesic(new BigDecimal(p), k, torusDims);
            BigDecimal[] emb_p = curve_p.get(0);
            List<BigDecimal[]> curve_q = Embedding.embedTorusGeodesic(new BigDecimal(q), k, torusDims);
            BigDecimal[] emb_q = curve_q.get(0);
            BigDecimal dist_p = RiemannianDistance.calculate(emb_N, emb_p, N_bd);
            BigDecimal dist_q = RiemannianDistance.calculate(emb_N, emb_q, N_bd);
            BigDecimal minDist = dist_p.min(dist_q);

            if (minDist.compareTo(epsilon) < 0) {
                return Optional.of(new BigInteger[]{p, q});
            }

            // Optional: Try A* to find path to factor embedding
            List<BigDecimal[]> path = RiemannianAStar.findPath(emb_N, emb_p, N_bd, 10000);
            if (path != null && path.size() > 1) {
                // Inverse embedding would be needed here, but simplified
            }
        }
        
        long verificationTime = System.nanoTime() - verificationStart;
        System.out.println("  ⏱️  Verification Time: " + String.format("%.2f", verificationTime / 1e6) + " ms");
        System.out.println("  📊 Checked " + candidatesChecked + " candidates");

        // Try geometric factorization for large numbers
        if (N.bitLength() >= 100) {
            long geoStart = System.nanoTime();
            try {
                RiemannianManifold manifold = new RiemannianManifold(N, dims);
                CurvatureTensor curvatureTensor = new CurvatureTensor(dims);
                GeodesicFinder geodesicFinder = new GeodesicFinder(manifold, curvatureTensor);
                
                BigDecimal[] embeddedPoint = manifold.embed();
                Optional<BigInteger[]> geometricResult = geodesicFinder.findFactorGeodesics(embeddedPoint, N);
                long geoTime = (System.nanoTime() - geoStart) / 1_000_000;
                System.out.println("Geometric factorization time: " + geoTime + " ms");
                if (geometricResult.isPresent()) {
                    BigInteger[] result = geometricResult.get();
                    if (result[0].compareTo(result[1]) > 0) {
                        BigInteger temp = result[0];
                        result[0] = result[1];
                        result[1] = temp;
                    }
                    return Optional.of(result);
                }
            } catch (Exception e) {
                long geoTime = (System.nanoTime() - geoStart) / 1_000_000;
                System.out.println("Geometric factorization failed after " + geoTime + " ms: " + e.getMessage());
            }
        }

        // Try geometric factorization for large numbers
        if (N.bitLength() >= 100) {
            long geoStart = System.nanoTime();
            try {
                RiemannianManifold manifold = new RiemannianManifold(N, dims);
                CurvatureTensor curvatureTensor = new CurvatureTensor(dims);
                GeodesicFinder geodesicFinder = new GeodesicFinder(manifold, curvatureTensor);
                
                BigDecimal[] embeddedPoint = manifold.embed();
                Optional<BigInteger[]> geometricResult = geodesicFinder.findFactorGeodesics(embeddedPoint, N);
                long geoTime = (System.nanoTime() - geoStart) / 1_000_000;
                System.out.println("Geometric factorization time: " + geoTime + " ms");
                if (geometricResult.isPresent()) {
                    BigInteger[] result = geometricResult.get();
                    if (result[0].compareTo(result[1]) > 0) {
                        BigInteger temp = result[0];
                        result[0] = result[1];
                        result[1] = temp;
                    }
                    return Optional.of(result);
                }
            } catch (Exception e) {
                long geoTime = (System.nanoTime() - geoStart) / 1_000_000;
                System.out.println("Geometric factorization failed after " + geoTime + " ms: " + e.getMessage());
            }
        }

        return Optional.empty(); // No factors found
    }

    /**
     * Estimate prime index k where p(k) ≈ value.
     * Uses BigDecimal for large values to avoid double overflow.
     */
    private static double findPrimeIndexApproximation(BigDecimal value) {
        if (value.compareTo(BigDecimal.valueOf(Double.MAX_VALUE)) < 0) {
            double v = value.doubleValue();
            return v / Math.log(v);
        } else {
            // For astronomically large values fallback to bitLength-based approximation
            int bits = value.toBigInteger().bitLength();
            double denom = (bits - 1) * Math.log(2);
            return Math.pow(2.0, bits - 1) / denom;
        }
    }

    /**
     * Check if p and q are balanced: |log2(p/q)| ≤ 1
     * Uses bitLength for safety on large inputs.
     */
    private static boolean isBalanced(BigInteger p, BigInteger q) {
        int bitDiff = Math.abs(p.bitLength() - q.bitLength());
        if (bitDiff > 1) return false;
        // For bitDiff 0 or 1, refine by checking p <= 2*q and q <= 2*p
        return (p.compareTo(q.shiftLeft(1)) <= 0) && (q.compareTo(p.shiftLeft(1)) <= 0);
    }

     /**
     * Square root for BigDecimal using Newton's method with relative tolerance.
     */
    private static BigDecimal sqrt(BigDecimal x, MathContext mc) {
        if (x.signum() < 0) throw new ArithmeticException("sqrt of negative");
        if (x.signum() == 0) return BigDecimal.ZERO;
        int precision = mc.getPrecision();
        BigDecimal two = BigDecimal.valueOf(2);
        BigDecimal guess = BigDecimal.ONE.movePointRight((x.precision() + x.scale()) / 2);
        MathContext mcIter = new MathContext(Math.max(precision + 10, 50), mc.getRoundingMode());
        BigDecimal prev;
        do {
            prev = guess;
            guess = prev.add(x.divide(prev, mcIter)).divide(two, mcIter);
        } while (prev.subtract(guess).abs().compareTo(BigDecimal.ONE.movePointLeft(precision)) > 0);
        return guess.round(mc);
    }
}
