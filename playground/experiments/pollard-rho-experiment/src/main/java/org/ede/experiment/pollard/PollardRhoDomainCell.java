package org.ede.experiment.pollard;

import java.util.Random;

/**
 * Pollard Rho factorization cell implementing a distributed factorization protocol.
 *
 * This cell encapsulates a single Pollard Rho factorization attempt with rich
 * state exposure. The algorithm uses a pseudorandom walk modulo n to detect
 * factors via cycle-finding: when the fast walker catches the slow walker
 * modulo a hidden prime factor p (but not modulo n), gcd(|x-y|, n) reveals p.
 *
 * State is segmented into three logical domains:
 * - Walker state: positions in the pseudorandom walk
 * - Factor discovery: candidate factors and verification
 * - Health metrics: convergence status and stagnation signals
 *
 * This design enables future distributed implementations where cells coordinate
 * via state comparison, sharing discovered factors, and adaptive restart strategies.
 *
 * Algorithm reference: Pollard, J.M. (1975) "A Monte Carlo Method for Factorization"
 * Cycle detection: Floyd, R.W. (1967) "Nondeterministic Algorithms"
 */
public class PollardRhoDomainCell {
    private final long targetModulus;
    private final WalkerState walkerState;
    private final FactorDiscoveryState factorDiscovery;
    private final HealthMetrics healthMetrics;
    private final PollardRhoStatistics statistics;

    private static final int DEFAULT_MAX_ITERATIONS = 10_000_000;
    private static final int RESTART_THRESHOLD = 100_000;

    private Random random;

    /**
     * Constructs a Pollard Rho cell for factoring the given semiprime.
     *
     * Validates that the target is odd (even numbers are trivially factorable
     * via division by 2). Initializes all state objects for tracking walk
     * position, factor discovery, health metrics, and execution statistics.
     *
     * @param targetModulus the number to factor (must be >= 2 and odd)
     * @throws IllegalArgumentException if targetModulus < 2 or is even
     */
    public PollardRhoDomainCell(long targetModulus) {
        if (targetModulus < 2) {
            throw new IllegalArgumentException("Target modulus must be >= 2, got " + targetModulus);
        }
        if (targetModulus % 2 == 0) {
            throw new IllegalArgumentException("Target modulus must be odd, got " + targetModulus);
        }

        this.targetModulus = targetModulus;
        this.walkerState = new WalkerState(targetModulus);
        this.factorDiscovery = new FactorDiscoveryState(targetModulus);
        this.healthMetrics = new HealthMetrics();
        this.statistics = new PollardRhoStatistics();
        this.random = new Random();
    }

    /**
     * Executes Pollard Rho factorization with full state instrumentation.
     *
     * The algorithm performs pseudorandom walk steps, checking for factors via GCD
     * at each iteration. When both walkers appear to enter the same cycle (GCD = n),
     * the cell restarts with new random parameters.
     *
     * The walk uses the polynomial f(x) = x^2 + c (mod n) where c is randomly chosen.
     * Both walkers start at the same position but advance at different rates:
     * - slow walker: x = f(x) (1 step per iteration)
     * - fast walker: y = f(f(y)) (2 steps per iteration)
     *
     * @return the discovered factor, or 0 if max iterations exceeded without success
     */
    public long execute() {
        initializeWalkers();

        long iterations = 0;
        while (iterations < DEFAULT_MAX_ITERATIONS) {
            // Advance walkers and check for factor
            if (stepWalkersAndCheckForFactor()) {
                // Found a valid factor
                statistics.setTotalIterations(iterations);
                statistics.recordDiscoveredFactor(factorDiscovery.getCurrentCandidateFactor(), true);
                statistics.finalizeExecutionTime();
                return factorDiscovery.getCurrentCandidateFactor();
            }

            // If gcd returned n, the walk has cycled completely without finding a factor
            // Restart with new random parameters
            if (!factorDiscovery.isFactorVerified() && factorDiscovery.getCurrentCandidateFactor() == targetModulus) {
                healthMetrics.recordRestartAttempt();
                statistics.recordRestartAttempt();
                restartWithNewParameters();
            }

            healthMetrics.incrementIterationsSinceDiscovery();
            iterations++;
        }

        // Exceeded max iterations without finding a factor
        statistics.setTotalIterations(iterations);
        statistics.recordDiscoveredFactor(0, false);
        statistics.finalizeExecutionTime();
        return 0;
    }

    /**
     * Initializes walker positions and polynomial offset to random values.
     *
     * Both slow and fast walkers start at the same position x in [2, n-1].
     * The polynomial offset c is randomly chosen in [1, n-1] to provide
     * diversity in the pseudorandom sequence across multiple cells.
     */
    private void initializeWalkers() {
        long initialPosition = 2 + random.nextLong(targetModulus - 2);
        long polynomialOffset = 1 + random.nextLong(targetModulus - 1);

        walkerState.setSlowWalkerPosition(initialPosition);
        walkerState.setFastWalkerPosition(initialPosition);
        walkerState.setPolynomialOffset(polynomialOffset);
    }

    /**
     * Performs one pseudorandom walk step via polynomial f(x) = x^2 + c (mod n).
     *
     * Advances:
     * - Slow walker: x = f(x) (1 step)
     * - Fast walker: y = f(f(y)) (2 steps)
     *
     * Computes their separation and performs GCD to check for factor discovery.
     *
     * @return true if a valid factor was discovered (1 < gcd < n)
     */
    private boolean stepWalkersAndCheckForFactor() {
        long c = walkerState.getPolynomialOffset();
        long x = walkerState.getSlowWalkerPosition();
        long y = walkerState.getFastWalkerPosition();

        // Advance slow walker 1 step
        x = (x * x + c) % targetModulus;

        // Advance fast walker 2 steps
        y = (y * y + c) % targetModulus;
        y = (y * y + c) % targetModulus;

        // Update walker positions
        walkerState.setSlowWalkerPosition(x);
        walkerState.setFastWalkerPosition(y);

        // Compute separation and check for factor
        long separation = Math.abs(x - y) % targetModulus;
        walkerState.setWalkerSeparation(separation);
        healthMetrics.updateConvergenceVelocity(separation);

        // Compute GCD of separation with target modulus
        long gcdResult = gcd(separation, targetModulus);
        healthMetrics.recordGcdComputation();
        statistics.recordGcdCall();

        // Record the candidate (regardless of validity)
        factorDiscovery.recordCandidateFactor(gcdResult, statistics.getTotalIterations());

        // Check if we found a valid factor
        if (gcdResult > 1 && gcdResult < targetModulus) {
            healthMetrics.resetIterationsSinceDiscovery();
            return true;
        }

        return false;
    }

    /**
     * Resets walker positions and polynomial offset for next attempt.
     *
     * Called when current walk enters a complete cycle (GCD = n).
     * Uses fresh random values to explore different pseudo-random sequences.
     * This provides parameter diversity across restart attempts.
     */
    private void restartWithNewParameters() {
        initializeWalkers();
        factorDiscovery.recordCandidateFactor(1, (int) statistics.getTotalIterations());
    }

    /**
     * Computes the greatest common divisor of a and b using Euclidean algorithm.
     *
     * @param a first operand
     * @param b second operand
     * @return gcd(a, b)
     */
    private long gcd(long a, long b) {
        a = Math.abs(a);
        b = Math.abs(b);
        while (b != 0) {
            long temp = b;
            b = a % b;
            a = temp;
        }
        return a;
    }

    // State accessors for distributed coordination

    /**
     * Exposes walker state for external coordination (future distributed use).
     *
     * @return snapshot of current walker positions and separation
     */
    public WalkerState getWalkerState() {
        return walkerState;
    }

    /**
     * Exposes factorization progress for external analysis.
     *
     * @return snapshot of discovered factors and verification status
     */
    public FactorDiscoveryState getFactorDiscoveryState() {
        return factorDiscovery;
    }

    /**
     * Exposes health signals for adaptive cell behavior (future distributed use).
     *
     * @return current health assessment including stagnation detection
     */
    public HealthMetrics getHealthMetrics() {
        return healthMetrics;
    }

    /**
     * Provides complete execution statistics for benchmarking and analysis.
     *
     * @return aggregated statistics including iterations, timing, and GCD calls
     */
    public PollardRhoStatistics getStatistics() {
        return statistics;
    }
}
