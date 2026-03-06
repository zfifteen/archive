package org.ede.experiment.pollard;

import java.time.Instant;

/**
 * Aggregates performance and algorithmic statistics for a single factorization attempt.
 *
 * Captures the complete execution profile: total iterations, GCD call count,
 * wall-clock time, restart frequency, and factor discovery moment. Enables
 * benchmarking, validation against Python reference implementation, and
 * identification of performance patterns across different semiprime sizes.
 *
 * These statistics are exported to CSV files for statistical analysis:
 * - Validates algorithm alignment between Python and Java implementations
 * - Identifies performance anomalies or pathological cases
 * - Measures overhead of state segmentation
 */
public class PollardRhoStatistics {
    private long totalIterations;              // Number of pseudorandom walk steps
    private int gcdCallCount;                  // Count of expensive gcd() operations
    private long wallClockTimeNanos;           // Total execution time in nanoseconds
    private int restartCount;                  // Number of complete cycle restarts (gcd = n)
    private long discoveredFactor;             // The factor successfully found
    private boolean succeeded;                 // Whether factorization completed successfully
    private long startTimeNanos;               // Timestamp when execution began
    private Instant executionTimestamp;        // When was this experiment run?

    /**
     * Constructs a statistics object for a new factorization attempt.
     *
     * Initializes all counters to zero and records the current timestamp
     * and start time for later duration calculation.
     */
    public PollardRhoStatistics() {
        this.totalIterations = 0;
        this.gcdCallCount = 0;
        this.wallClockTimeNanos = 0;
        this.restartCount = 0;
        this.discoveredFactor = 0;
        this.succeeded = false;
        this.startTimeNanos = System.nanoTime();
        this.executionTimestamp = Instant.now();
    }

    /**
     * Sets the total iterations executed.
     *
     * @param iterations the number of pseudorandom walk steps performed
     */
    public void setTotalIterations(long iterations) {
        this.totalIterations = iterations;
    }

    /**
     * Records a GCD computation.
     *
     * Typically called once per iteration, though batch GCD strategies
     * (future optimization) could reduce this count.
     */
    public void recordGcdCall() {
        this.gcdCallCount++;
    }

    /**
     * Finalizes the execution time measurement.
     *
     * Must be called at the end of execute() to capture total wall-clock time.
     */
    public void finalizeExecutionTime() {
        this.wallClockTimeNanos = System.nanoTime() - startTimeNanos;
    }

    /**
     * Records a restart attempt.
     *
     * Called when gcd(|x - y|, n) = n, indicating the walk cycle completed
     * without finding a non-trivial factor.
     */
    public void recordRestartAttempt() {
        this.restartCount++;
    }

    /**
     * Records the discovered factor.
     *
     * @param factor the value of p found (1 < p < n such that n % p == 0)
     * @param succeeded true if the factorization completed successfully
     */
    public void recordDiscoveredFactor(long factor, boolean succeeded) {
        this.discoveredFactor = factor;
        this.succeeded = succeeded;
    }

    /**
     * Returns the total iterations executed.
     *
     * @return the number of pseudorandom walk steps
     */
    public long getTotalIterations() {
        return totalIterations;
    }

    /**
     * Returns the count of GCD computations.
     *
     * @return the number of gcd() calls
     */
    public int getGcdCallCount() {
        return gcdCallCount;
    }

    /**
     * Returns the wall-clock execution time in milliseconds.
     *
     * Converts nanoseconds to milliseconds for readability.
     *
     * @return execution time in ms
     */
    public double getExecutionTimeMillis() {
        return wallClockTimeNanos / 1_000_000.0;
    }

    /**
     * Returns the wall-clock execution time in nanoseconds.
     *
     * @return execution time in ns
     */
    public long getExecutionTimeNanos() {
        return wallClockTimeNanos;
    }

    /**
     * Returns the restart attempt count.
     *
     * @return number of complete cycle restarts
     */
    public int getRestartCount() {
        return restartCount;
    }

    /**
     * Returns the discovered factor.
     *
     * @return the value p such that n = p * q
     */
    public long getDiscoveredFactor() {
        return discoveredFactor;
    }

    /**
     * Indicates whether factorization succeeded.
     *
     * @return true if a non-trivial factor was found, false if max iterations exceeded
     */
    public boolean isSucceeded() {
        return succeeded;
    }

    /**
     * Returns the execution timestamp.
     *
     * @return when this experiment was run
     */
    public Instant getExecutionTimestamp() {
        return executionTimestamp;
    }

    /**
     * Formats statistics as CSV row for export.
     *
     * @param testCaseName descriptive name of the test case
     * @return CSV-formatted statistics line
     */
    public String toCsvRow(String testCaseName) {
        return String.format("%s,%d,%d,%.4f,%d,%d,%s",
                testCaseName,
                totalIterations,
                gcdCallCount,
                getExecutionTimeMillis(),
                restartCount,
                discoveredFactor,
                succeeded ? "PASS" : "FAIL"
        );
    }

    /**
     * Provides a summary string representation.
     *
     * @return human-readable statistics summary
     */
    @Override
    public String toString() {
        return String.format(
                "PollardRhoStatistics{iterations=%d, gcdCalls=%d, timeMs=%.4f, restarts=%d, factor=%d, success=%s}",
                totalIterations,
                gcdCallCount,
                getExecutionTimeMillis(),
                restartCount,
                discoveredFactor,
                succeeded
        );
    }
}
