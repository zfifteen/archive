package unifiedframework;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.concurrent.atomic.AtomicReference;

/**
 * Java reference implementation of precision fixes from PR #206.
 * 
 * This class implements the high-precision curvature computation and fractional
 * comb formula that resolved the 3.92% error floor on RSA-2048 factorization.
 * 
 * Key formulas:
 * - Curvature: κ(n) = d(n) * ln(n+1) / e²
 * - Fractional Comb: log(p_m) = log(N)/2 - πm/k
 * 
 * Related to:
 * - Issue #221: Precision bottleneck fixes
 * - PR #206: Fix z5d_axioms import path and fractional comb precision issues
 * 
 * @see <a href="https://github.com/zfifteen/z-sandbox/pull/206">PR #206</a>
 */
public class PrecisionFixes {

    private static final Logger LOGGER = Logger.getLogger(PrecisionFixes.class.getName());
    
    // High-precision math context (512 decimal places for RSA-2048+ scale)
    private static final MathContext HIGH_PRECISION = new MathContext(512, RoundingMode.HALF_EVEN);
    
    // Standard precision for general calculations
    private static final MathContext STANDARD_PRECISION = new MathContext(100, RoundingMode.HALF_EVEN);
    
    // Constants
    private static final BigDecimal E_SQUARED;
    private static final BigDecimal PI;
    private static final BigDecimal PHI; // Golden ratio
    
    // Warning flag (thread-safe with volatile)
    private static volatile boolean fallbackWarningLogged = false;
    
    static {
        // Compute e² with high precision
        BigDecimal e = computeE(HIGH_PRECISION);
        E_SQUARED = e.multiply(e, HIGH_PRECISION);
        
        // Compute π with high precision (using Machin's formula)
        PI = computePi(HIGH_PRECISION);
        
        // Golden ratio: φ = (1 + √5) / 2
        // Reserved for future use in phase-bias correction mechanisms
        PHI = BigDecimal.ONE.add(sqrt(new BigDecimal("5"), HIGH_PRECISION))
              .divide(new BigDecimal("2"), HIGH_PRECISION);
    }
    
    /**
     * Configuration for refinement mechanisms.
     */
    public static class RefinementConfig {
        public boolean usePhaseCorrection = true;
        public boolean useDirichlet = true;
        public boolean useDualK = true;
        public boolean useKappaWeight = true;
        public boolean useAdaptiveK = true;
        
        // Fractional comb parameters (Issue #221 fix)
        public boolean useFractionalComb = false;
        public double combStep = 1.0;  // Step size for m (1.0 = integer, 0.001 = fractional)
        public double combRange = 100.0;  // Range for m scanning (absolute m range)
        
        // Precision settings
        public MathContext precision = HIGH_PRECISION;
        public boolean enablePrecisionWarnings = true;
    }
    
    /**
     * Result from fractional comb candidate generation.
     */
    public static class CombCandidate {
        public final BigInteger pCandidate;
        public final double mValue;
        public final BigDecimal amplitude;
        public final BigDecimal kappaWeight;
        public final BigDecimal score;
        
        public CombCandidate(BigInteger pCandidate, double mValue, 
                            BigDecimal amplitude, BigDecimal kappaWeight, BigDecimal score) {
            this.pCandidate = pCandidate;
            this.mValue = mValue;
            this.amplitude = amplitude;
            this.kappaWeight = kappaWeight;
            this.score = score;
        }
        
        @Override
        public String toString() {
            return String.format("CombCandidate{p=%s, m=%.6f, amplitude=%s, kappa=%.6f, score=%s}",
                pCandidate, mValue, amplitude.toPlainString(), kappaWeight.doubleValue(), 
                score.toPlainString());
        }
    }
    
    /**
     * Compute high-precision Z5D curvature: κ(n) = d(n) * ln(n+1) / e²
     * 
     * CRITICAL FIX (Issue #221): Uses ln(n+1) instead of ln(n) for consistency
     * with the Python implementation that achieved 0.077% error on RSA-2048.
     * 
     * @param n The integer value
     * @param useApproximation If true, use semiprime approximation (d=4)
     * @param mc Math context for precision
     * @return Curvature value κ(n)
     */
    public static BigDecimal computeCurvatureHighPrecision(BigInteger n, 
                                                           boolean useApproximation,
                                                           MathContext mc) {
        if (n.compareTo(BigInteger.ZERO) <= 0) {
            throw new IllegalArgumentException("n must be positive");
        }
        
        // Determine divisor count (d(n))
        int divisorCount;
        if (useApproximation) {
            // For semiprimes, d(n) ≈ 4
            divisorCount = 4;
        } else {
            // Exact divisor count (expensive for large n)
            divisorCount = computeDivisorCount(n);
        }
        
        // Convert to BigDecimal
        BigDecimal d = new BigDecimal(divisorCount);
        
        // Compute ln(n+1) with high precision
        BigDecimal nPlusOne = new BigDecimal(n.add(BigInteger.ONE));
        BigDecimal lnNPlusOne = ln(nPlusOne, mc);
        
        // κ(n) = d * ln(n+1) / e²
        BigDecimal kappa = d.multiply(lnNPlusOne, mc).divide(E_SQUARED, mc);
        
        return kappa;
    }
    
    /**
     * Compute prime density approximation: d(n) ≈ 1 / ln(n)
     */
    public static BigDecimal primeDensityApproximation(BigInteger n, MathContext mc) {
        if (n.compareTo(BigInteger.ONE) <= 0) {
            return BigDecimal.ZERO;
        }
        
        BigDecimal nDecimal = new BigDecimal(n);
        BigDecimal lnN = ln(nDecimal, mc);
        
        return BigDecimal.ONE.divide(lnN, mc);
    }
    
    /**
     * Generate candidates using fractional comb formula.
     * 
     * CRITICAL FIX (Issue #221): 
     * - combRange is interpreted as absolute m range (e.g., 1.0 means m ∈ [-1, +1])
     * - Always uses log_N/2 as center (NOT biased by sqrt corrections)
     * - Generates 2*combRange/combStep + 1 candidates
     * 
     * Formula: log(p_m) = log(N)/2 - πm/k
     * 
     * @param N The semiprime to factor
     * @param k Wave parameter
     * @param config Configuration
     * @return List of candidates with scoring
     */
    public static List<CombCandidate> generateFractionalCombCandidates(
            BigInteger N, double k, RefinementConfig config) {
        
        List<CombCandidate> candidates = new ArrayList<>();
        MathContext mc = config.precision;
        
        // CRITICAL: Always use log_N/2 as center (fractional comb formula requirement)
        BigDecimal nDecimal = new BigDecimal(N);
        BigDecimal logN = ln(nDecimal, mc);
        BigDecimal logCenter = logN.divide(new BigDecimal("2"), mc);
        
        // Calculate number of steps from range and step size
        // combRange is absolute m range (e.g., 1.0 means m ∈ [-1, +1])
        int numSteps = (int) (config.combRange / config.combStep);
        
        BigDecimal kBD = new BigDecimal(k, mc);
        
        // Generate candidates for m ∈ [-numSteps*combStep, +numSteps*combStep]
        for (int i = -numSteps; i <= numSteps; i++) {
            double m = i * config.combStep;
            BigDecimal mBD = new BigDecimal(m, mc);
            
            // Comb formula: log(p_m) = log(N)/2 - πm/k
            BigDecimal piMOverK = PI.multiply(mBD, mc).divide(kBD, mc);
            BigDecimal logP = logCenter.subtract(piMOverK, mc);
            
            // p_m = exp(logP)
            BigDecimal pDecimal = exp(logP, mc);
            
            // Convert to BigInteger (candidate factor)
            BigInteger pCandidate;
            try {
                pCandidate = pDecimal.toBigInteger();
            } catch (ArithmeticException e) {
                // Skip if conversion fails
                continue;
            }
            
            // Verify candidate is in valid range
            if (pCandidate.compareTo(BigInteger.ONE) <= 0 || 
                pCandidate.compareTo(N) >= 0) {
                continue;
            }
            
            // Compute Green's function amplitude: |cos(2πm)|
            // Note: This peaks at integer m, not fractional m where true factor lies
            double twoMPi = 2.0 * Math.PI * m;
            BigDecimal amplitude = new BigDecimal(Math.abs(Math.cos(twoMPi)), mc);
            
            // Compute κ-weight for this candidate
            BigDecimal kappaWeight = computeCurvatureHighPrecision(
                pCandidate, true, mc);
            
            // Combined score (amplitude × κ-weight)
            BigDecimal score = amplitude.multiply(kappaWeight, mc);
            
            candidates.add(new CombCandidate(pCandidate, m, amplitude, kappaWeight, score));
        }
        
        return candidates;
    }
    
    /**
     * Compute exact divisor count (expensive for large n).
     */
    private static int computeDivisorCount(BigInteger n) {
        int count = 0;
        BigInteger i = BigInteger.ONE;
        BigInteger sqrt = sqrt(n);
        
        while (i.compareTo(sqrt) <= 0) {
            if (n.mod(i).equals(BigInteger.ZERO)) {
                count++;
                BigInteger quotient = n.divide(i);
                if (!i.equals(quotient)) {
                    count++;
                }
            }
            i = i.add(BigInteger.ONE);
        }
        
        return count;
    }
    
    /**
     * Compute integer square root.
     */
    private static BigInteger sqrt(BigInteger n) {
        if (n.compareTo(BigInteger.ZERO) < 0) {
            throw new IllegalArgumentException("Cannot compute square root of negative number");
        }
        if (n.compareTo(BigInteger.ONE) <= 0) {
            return n;
        }
        
        // Newton's method for integer square root
        BigInteger x = n.divide(BigInteger.TWO);
        BigInteger lastX = x.add(BigInteger.ONE);
        
        while (x.compareTo(lastX) < 0) {
            lastX = x;
            x = x.add(n.divide(x)).divide(BigInteger.TWO);
        }
        
        return lastX;
    }
    
    // ========== High-Precision Mathematical Functions ==========
    
    /**
     * Compute natural logarithm with high precision.
     * Uses ln(x) = 2 * artanh((x-1)/(x+1)) for better convergence.
     */
    private static BigDecimal ln(BigDecimal x, MathContext mc) {
        if (x.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("ln(x) undefined for x <= 0");
        }
        
        if (x.compareTo(BigDecimal.ONE) == 0) {
            return BigDecimal.ZERO;
        }
        
        // Scale to [0.5, 2) for better convergence
        int scale = 0;
        BigDecimal scaled = x;
        BigDecimal two = new BigDecimal("2");
        BigDecimal half = new BigDecimal("0.5");
        
        while (scaled.compareTo(two) >= 0) {
            scaled = scaled.divide(two, mc);
            scale++;
        }
        
        while (scaled.compareTo(half) < 0) {
            scaled = scaled.multiply(two, mc);
            scale--;
        }
        
        // Use the identity: ln(x) = 2 * artanh((x-1)/(x+1))
        // This converges faster than the Taylor series
        BigDecimal numerator = scaled.subtract(BigDecimal.ONE);
        BigDecimal denominator = scaled.add(BigDecimal.ONE);
        BigDecimal z = numerator.divide(denominator, mc);
        
        BigDecimal artanhZ = artanh(z, mc);
        BigDecimal lnScaled = two.multiply(artanhZ, mc);
        
        // Add back the scaling: ln(x) = ln(scaled) + scale*ln(2)
        if (scale != 0) {
            BigDecimal ln2 = ln2(mc);
            lnScaled = lnScaled.add(ln2.multiply(new BigDecimal(scale), mc), mc);
        }
        
        return lnScaled;
    }
    
    /**
     * Compute artanh(x) = 0.5 * ln((1+x)/(1-x)) using series expansion.
     * artanh(x) = x + x³/3 + x⁵/5 + x⁷/7 + ...
     */
    private static BigDecimal artanh(BigDecimal x, MathContext mc) {
        if (x.abs().compareTo(BigDecimal.ONE) >= 0) {
            throw new IllegalArgumentException("artanh(x) undefined for |x| >= 1");
        }
        
        BigDecimal sum = BigDecimal.ZERO;
        BigDecimal xSquared = x.multiply(x, mc);
        BigDecimal term = x;
        int n = 1;
        
        int maxIterations = mc.getPrecision() * 2;
        for (int i = 0; i < maxIterations; i++) {
            BigDecimal termValue = term.divide(new BigDecimal(n), mc);
            sum = sum.add(termValue, mc);
            
            // Check convergence
            if (termValue.abs().compareTo(
                BigDecimal.ONE.movePointLeft(mc.getPrecision())) < 0) {
                break;
            }
            
            term = term.multiply(xSquared, mc);
            n += 2;
        }
        
        return sum;
    }
    
    /**
     * Compute e^x with high precision using Taylor series.
     */
    private static BigDecimal exp(BigDecimal x, MathContext mc) {
        // exp(x) = 1 + x + x²/2! + x³/3! + ...
        
        BigDecimal sum = BigDecimal.ONE;
        BigDecimal term = BigDecimal.ONE;
        int n = 1;
        
        int maxIterations = mc.getPrecision() * 2;
        for (int i = 0; i < maxIterations; i++) {
            term = term.multiply(x, mc).divide(new BigDecimal(n), mc);
            sum = sum.add(term, mc);
            
            // Check convergence
            if (term.abs().compareTo(
                BigDecimal.ONE.movePointLeft(mc.getPrecision())) < 0) {
                break;
            }
            
            n++;
        }
        
        return sum;
    }
    
    /**
     * Compute square root with high precision using Newton's method.
     */
    private static BigDecimal sqrt(BigDecimal x, MathContext mc) {
        if (x.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("Cannot compute square root of negative number");
        }
        if (x.compareTo(BigDecimal.ZERO) == 0) {
            return BigDecimal.ZERO;
        }
        
        // Newton's method: x_{n+1} = (x_n + a/x_n) / 2
        BigDecimal guess = x.divide(new BigDecimal("2"), mc);
        BigDecimal lastGuess;
        BigDecimal two = new BigDecimal("2");
        
        int maxIterations = mc.getPrecision();
        for (int i = 0; i < maxIterations; i++) {
            lastGuess = guess;
            guess = x.divide(guess, mc).add(guess, mc).divide(two, mc);
            
            // Check convergence
            if (guess.subtract(lastGuess).abs().compareTo(
                BigDecimal.ONE.movePointLeft(mc.getPrecision())) < 0) {
                break;
            }
        }
        
        return guess;
    }
    
    /**
     * Compute e with high precision.
     */
    private static BigDecimal computeE(MathContext mc) {
        // e = 1 + 1/1! + 1/2! + 1/3! + ...
        BigDecimal sum = BigDecimal.ONE;
        BigDecimal term = BigDecimal.ONE;
        int n = 1;
        
        int maxIterations = mc.getPrecision();
        for (int i = 0; i < maxIterations; i++) {
            term = term.divide(new BigDecimal(n), mc);
            sum = sum.add(term, mc);
            
            if (term.compareTo(BigDecimal.ONE.movePointLeft(mc.getPrecision())) < 0) {
                break;
            }
            
            n++;
        }
        
        return sum;
    }
    
    /**
     * Compute π with high precision using Machin's formula.
     * π/4 = 4*arctan(1/5) - arctan(1/239)
     */
    private static BigDecimal computePi(MathContext mc) {
        BigDecimal four = new BigDecimal("4");
        BigDecimal arctan5 = arctan(BigDecimal.ONE.divide(new BigDecimal("5"), mc), mc);
        BigDecimal arctan239 = arctan(BigDecimal.ONE.divide(new BigDecimal("239"), mc), mc);
        
        BigDecimal piOver4 = four.multiply(arctan5, mc).subtract(arctan239, mc);
        
        return piOver4.multiply(four, mc);
    }
    
    /**
     * Compute arctan with high precision using Taylor series.
     */
    private static BigDecimal arctan(BigDecimal x, MathContext mc) {
        // arctan(x) = x - x³/3 + x⁵/5 - x⁷/7 + ...
        BigDecimal sum = BigDecimal.ZERO;
        BigDecimal xSquared = x.multiply(x, mc);
        BigDecimal term = x;
        int n = 1;
        
        int maxIterations = mc.getPrecision() * 2;
        for (int i = 0; i < maxIterations; i++) {
            BigDecimal termValue = term.divide(new BigDecimal(n), mc);
            if (i % 2 == 0) {
                sum = sum.add(termValue, mc);
            } else {
                sum = sum.subtract(termValue, mc);
            }
            
            // Check convergence
            if (termValue.abs().compareTo(
                BigDecimal.ONE.movePointLeft(mc.getPrecision())) < 0) {
                break;
            }
            
            term = term.multiply(xSquared, mc);
            n += 2;
        }
        
        return sum;
    }
    
    /**
     * Cached ln(2) and ln(10) for efficiency.
     * Uses AtomicReference for thread-safe, context-aware caching.
     */
    private static final AtomicReference<Pair<MathContext, BigDecimal>> ln2Cache = new AtomicReference<>();
    private static final AtomicReference<Pair<MathContext, BigDecimal>> ln10Cache = new AtomicReference<>();

    private static BigDecimal ln2(MathContext mc) {
        Pair<MathContext, BigDecimal> cached = ln2Cache.get();
        if (cached != null && cached.key.equals(mc)) {
            return cached.value;
        }
        // Compute ln(2) using series: ln(2) = 2 * artanh(1/3)
        BigDecimal third = BigDecimal.ONE.divide(new BigDecimal("3"), mc);
        BigDecimal newLn2 = new BigDecimal("2").multiply(artanh(third, mc), mc);
        ln2Cache.set(new Pair<>(mc, newLn2));
        return newLn2;
    }

    /**
     * Compute ln(10) with caching.
     * Reserved for potential future use in scaling operations.
     */
    private static BigDecimal ln10(MathContext mc) {
        Pair<MathContext, BigDecimal> cached = ln10Cache.get();
        if (cached != null && cached.key.equals(mc)) {
            return cached.value;
        }
        // ln(10) = ln(2*5) = ln(2) + ln(5)
        BigDecimal ln2 = ln2(mc);
        BigDecimal ln5 = ln(new BigDecimal("5"), mc);
        BigDecimal newLn10 = ln2.add(ln5, mc);
        ln10Cache.set(new Pair<>(mc, newLn10));
        return newLn10;
    }

    /**
     * Log precision warning if fallback to low-precision methods.
     */
    private static void logPrecisionWarning(String message) {
        if (!fallbackWarningLogged) {
            synchronized (PrecisionFixes.class) {
                if (!fallbackWarningLogged) {
                    LOGGER.log(Level.WARNING,
                        "⚠️  PRECISION DEGRADATION: " + message +
                        " This may cause ~3.92% error floor on RSA-2048. " +
                        "Use high-precision methods for cryptographic-scale work.");
                    fallbackWarningLogged = true;
                }
            }
        }
    }

    /**
     * Validate that sufficient precision is being used for a given bit size.
     */
    public static void validatePrecision(int bitSize, MathContext mc) {
        // Correct conversion: decimal digits ≈ bitSize * log10(2) ≈ bitSize * 0.30103
        int requiredPrecision = (int) Math.ceil(bitSize * 0.30103);

        if (mc.getPrecision() < requiredPrecision) {
            String message = String.format(
                "Precision %d may be insufficient for %d-bit numbers (recommended: >=%d)",
                mc.getPrecision(), bitSize, requiredPrecision);
            logPrecisionWarning(message);
        }
    }

    private static class Pair<K, V> {
        final K key;
        final V value;

        Pair(K key, V value) {
            this.key = key;
            this.value = value;
        }
    }
}
