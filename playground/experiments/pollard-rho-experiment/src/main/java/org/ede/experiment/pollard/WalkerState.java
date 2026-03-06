package org.ede.experiment.pollard;

/**
 * Represents the position and motion state of both Pollard Rho walkers.
 *
 * The pseudorandom walk in Pollard Rho maintains two concurrent traversals:
 * the "slow walker" advances one step per iteration (x = f(x)), while the
 * "fast walker" advances two steps per iteration (y = f(f(y))).
 *
 * This asymmetry enables cycle detection via Floyd's algorithm: when both
 * walkers are in the same cycle modulo n, their positions will eventually
 * converge. More importantly, they converge modulo any prime factor p of n
 * much faster than modulo n itself, because cycles are shorter modulo p.
 *
 * The walker separation (|x - y|) becomes a primary signal:
 * - Small separation → walkers converging → cycle imminent
 * - Large separation → walkers still exploring → different cycle paths
 *
 * This state is exposed to enable future distributed coordination where cells
 * compare walker convergence rates to organize into affinity groups.
 */
public class WalkerState {
    private long slowWalkerPosition;      // x: advances 1 step per iteration
    private long fastWalkerPosition;      // y: advances 2 steps per iteration
    private long polynomialOffset;        // c: random parameter for f(x) = x² + c (mod n)
    private long walkerSeparation;        // |x - y| mod n
    private long targetModulus;           // n: the number being factored

    /**
     * Constructs a walker state initialized to the given modulus.
     *
     * @param targetModulus the number n being factored
     */
    public WalkerState(long targetModulus) {
        this.targetModulus = targetModulus;
        this.slowWalkerPosition = 0;
        this.fastWalkerPosition = 0;
        this.polynomialOffset = 0;
        this.walkerSeparation = 0;
    }

    /**
     * Returns the current position of the slow walker in the pseudorandom walk.
     *
     * @return the slow walker position x
     */
    public long getSlowWalkerPosition() {
        return slowWalkerPosition;
    }

    /**
     * Sets the slow walker to a new position.
     *
     * @param position the new position for the slow walker
     */
    public void setSlowWalkerPosition(long position) {
        this.slowWalkerPosition = position;
    }

    /**
     * Returns the current position of the fast walker in the pseudorandom walk.
     *
     * @return the fast walker position y
     */
    public long getFastWalkerPosition() {
        return fastWalkerPosition;
    }

    /**
     * Sets the fast walker to a new position.
     *
     * @param position the new position for the fast walker
     */
    public void setFastWalkerPosition(long position) {
        this.fastWalkerPosition = position;
    }

    /**
     * Returns the polynomial offset parameter c used in f(x) = x² + c (mod n).
     *
     * Different values of c produce different pseudorandom sequences,
     * enabling exploration of multiple walk paths.
     *
     * @return the polynomial offset c
     */
    public long getPolynomialOffset() {
        return polynomialOffset;
    }

    /**
     * Sets the polynomial offset parameter.
     *
     * @param offset the new polynomial offset c
     */
    public void setPolynomialOffset(long offset) {
        this.polynomialOffset = offset;
    }

    /**
     * Returns the absolute difference between walker positions: |x - y| mod n.
     *
     * This separation is the key signal for factor discovery. When
     * gcd(walkerSeparation, n) > 1, a factor is at hand.
     *
     * @return the walker separation
     */
    public long getWalkerSeparation() {
        return walkerSeparation;
    }

    /**
     * Sets the walker separation to a new value.
     *
     * @param separation the new separation |x - y|
     */
    public void setWalkerSeparation(long separation) {
        this.walkerSeparation = separation;
    }

    /**
     * Returns the target modulus n being factored.
     *
     * @return the modulus n
     */
    public long getTargetModulus() {
        return targetModulus;
    }
}
