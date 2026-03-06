package org.ede.experiment.pollard;

/**
 * Measures factorization cell health and convergence status.
 *
 * Health signals include iteration stagnation (how many steps since last discovery),
 * successful factor discovery frequency, and GCD computation count. These metrics
 * enable monitoring of algorithm behavior and detection of pathological cases.
 *
 * In distributed implementations, health metrics enable emergent coordination:
 * - Cells with similar convergence rates attract (synchronization)
 * - Stagnant cells repel healthy ones (specialization)
 * - Restart frequency indicates parameter diversity exploration
 *
 * This segmentation allows a grid of cells to self-organize based on
 * local health comparisons rather than explicit role assignment.
 */
public class HealthMetrics {
    private int iterationsSinceLastDiscovery;     // Steps since last factor candidate
    private int restartAttemptCount;              // Number of failed cycles (gcd = n)
    private int gcdComputationCount;              // Total GCD calls (expensive operation)
    private boolean isStagnant;                   // true if exceeding stagnation threshold
    private double convergenceVelocity;           // (walkerSeparation decrease) / iteration
    private long lastWalkerSeparation;            // Previous separation for velocity calculation
    private int stagnationThreshold;              // Iterations without discovery to flag stagnation

    /**
     * Constructs health metrics with default stagnation threshold.
     *
     * The threshold is set to 1,000 iterations: if no factor candidate is discovered
     * within this window, the cell is flagged as stagnant. Cells can then restart
     * with new parameters or coordinate with neighbors.
     */
    public HealthMetrics() {
        this.iterationsSinceLastDiscovery = 0;
        this.restartAttemptCount = 0;
        this.gcdComputationCount = 0;
        this.isStagnant = false;
        this.convergenceVelocity = 0.0;
        this.lastWalkerSeparation = 0;
        this.stagnationThreshold = 1000;
    }

    /**
     * Increments the iteration counter since last discovery.
     *
     * Called each iteration to track how long the cell has searched without
     * finding a candidate factor.
     */
    public void incrementIterationsSinceDiscovery() {
        iterationsSinceLastDiscovery++;
        updateStagnationStatus();
    }

    /**
     * Resets the iterations-since-discovery counter.
     *
     * Called when a new candidate factor is discovered (regardless of validity).
     * This restarts the stagnation timer.
     */
    public void resetIterationsSinceDiscovery() {
        iterationsSinceLastDiscovery = 0;
        updateStagnationStatus();
    }

    /**
     * Records a GCD computation event.
     *
     * GCD is expensive: O(log n). Tracking its frequency enables benchmarking
     * and optimization of batch GCD strategies for future distributed versions.
     */
    public void recordGcdComputation() {
        gcdComputationCount++;
    }

    /**
     * Records a restart event (cycle completed without factor discovery).
     *
     * When gcd(|x - y|, n) = n, both walkers have entered the complete cycle
     * modulo n. Restarting with new random parameters explores different
     * pseudorandom sequences.
     */
    public void recordRestartAttempt() {
        restartAttemptCount++;
    }

    /**
     * Updates convergence velocity based on walker separation change.
     *
     * Measures how quickly walker positions are converging. A decreasing separation
     * indicates progress toward cycle detection. Small positive velocity suggests
     * the walk is converging; zero or negative velocity suggests divergence or cycling.
     *
     * @param currentWalkerSeparation the current |x - y| mod n
     */
    public void updateConvergenceVelocity(long currentWalkerSeparation) {
        if (lastWalkerSeparation > 0) {
            // Velocity: how much did separation decrease?
            long separationDelta = lastWalkerSeparation - currentWalkerSeparation;
            this.convergenceVelocity = (double) separationDelta / lastWalkerSeparation;
        }
        this.lastWalkerSeparation = currentWalkerSeparation;
    }

    /**
     * Returns iterations without discovery.
     *
     * @return count of iterations since last factor candidate
     */
    public int getIterationsSinceLastDiscovery() {
        return iterationsSinceLastDiscovery;
    }

    /**
     * Returns the restart attempt count.
     *
     * @return number of complete cycles completed (gcd = n events)
     */
    public int getRestartAttemptCount() {
        return restartAttemptCount;
    }

    /**
     * Returns the total GCD computations performed.
     *
     * @return count of gcd() calls
     */
    public int getGcdComputationCount() {
        return gcdComputationCount;
    }

    /**
     * Indicates whether the cell is flagged as stagnant.
     *
     * A stagnant cell has completed many iterations without discovering a
     * factor candidate. This may indicate:
     * - Poor random seed for polynomial offset c
     * - Pathological walk behavior for this particular n
     * - Very large factors (expected: very long walks)
     *
     * @return true if iterationsSinceLastDiscovery > stagnationThreshold
     */
    public boolean isStagnant() {
        return isStagnant;
    }

    /**
     * Returns the convergence velocity: the fractional decrease in separation per iteration.
     *
     * A value near 0.0 indicates the separation is not changing.
     * Positive values indicate decreasing separation (converging).
     * Negative values indicate increasing separation (diverging).
     *
     * @return the convergence velocity
     */
    public double getConvergenceVelocity() {
        return convergenceVelocity;
    }

    /**
     * Internally updates stagnation status based on current iteration count.
     */
    private void updateStagnationStatus() {
        this.isStagnant = (iterationsSinceLastDiscovery > stagnationThreshold);
    }
}
