package org.ede.experiment.pollard;

/**
 * Tracks factorization progress and candidate factors discovered during execution.
 *
 * Pollard Rho does not directly compute factors; rather, it detects when
 * gcd(|x - y|, n) yields a value between 1 and n. This class records all
 * candidates discovered, their verification status, and the iteration at
 * which discovery occurred.
 *
 * This state is exposed to enable:
 * - Post-execution analysis of convergence patterns
 * - Detection of premature cycles (gcd = n) requiring restart
 * - Coordination in distributed settings (cells sharing discovered factors)
 * - Statistical validation against Python reference implementation
 */
public class FactorDiscoveryState {
    private long currentCandidateFactor;        // The last GCD result > 1
    private boolean isFactorVerified;           // true if n % currentCandidateFactor == 0
    private int iterationOfLastDiscovery;       // Which iteration found the current candidate
    private int discoveryCount;                 // Total candidate discoveries (including false cycles)
    private long targetModulus;                 // Reference to n for verification

    /**
     * Constructs a factor discovery state for tracking a factorization attempt.
     *
     * @param targetModulus the number n being factored
     */
    public FactorDiscoveryState(long targetModulus) {
        this.targetModulus = targetModulus;
        this.currentCandidateFactor = 1;
        this.isFactorVerified = false;
        this.iterationOfLastDiscovery = 0;
        this.discoveryCount = 0;
    }

    /**
     * Records the discovery of a new candidate factor.
     *
     * Validates the candidate is a true divisor of n (gcd result can be > 1 but
     * spurious if equal to n). The candidate is recorded regardless; the
     * verification flag indicates whether it is a true factor.
     *
     * @param candidate the gcd result to evaluate
     * @param iterationNumber the iteration at which this candidate was found
     */
    public void recordCandidateFactor(long candidate, int iterationNumber) {
        this.currentCandidateFactor = candidate;
        this.iterationOfLastDiscovery = iterationNumber;
        this.discoveryCount++;
        
        // Verify: a true factor divides n evenly
        this.isFactorVerified = (candidate > 1 && candidate < targetModulus && targetModulus % candidate == 0);
    }

    /**
     * Returns the most recent candidate factor discovered.
     *
     * @return the last gcd result that exceeded 1
     */
    public long getCurrentCandidateFactor() {
        return currentCandidateFactor;
    }

    /**
     * Indicates whether the current candidate is a verified factor of n.
     *
     * A result of false typically means gcd(x - y, n) = n, indicating
     * the walkers entered the same cycle modulo n (both modulo p and modulo q
     * for factors p, q of n). This triggers a restart.
     *
     * @return true if 1 < currentCandidateFactor < n and n % currentCandidateFactor == 0
     */
    public boolean isFactorVerified() {
        return isFactorVerified;
    }

    /**
     * Returns the iteration number at which the current candidate was discovered.
     *
     * Enables analysis of convergence speed: how many steps before the first
     * valid factor is found?
     *
     * @return the iteration number of last discovery
     */
    public int getIterationOfLastDiscovery() {
        return iterationOfLastDiscovery;
    }

    /**
     * Returns the total number of candidate discoveries (including false cycles).
     *
     * Each time gcd > 1, this counter increments. Includes cases where gcd = n
     * (requiring restart) and valid factors.
     *
     * @return the count of discovery events
     */
    public int getDiscoveryCount() {
        return discoveryCount;
    }

    /**
     * Returns the target modulus for reference.
     *
     * @return the number n
     */
    public long getTargetModulus() {
        return targetModulus;
    }
}
