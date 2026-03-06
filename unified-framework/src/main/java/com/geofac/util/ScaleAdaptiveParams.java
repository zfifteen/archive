package com.geofac.util;

import java.math.BigInteger;

/**
 * Scale-adaptive parameters for geofac factorization.
 * Implements PR-123 curvature-threshold-k scaling laws.
 */
public class ScaleAdaptiveParams {
    
    private final int bitLength;
    private final double threshold;
    private final double kShift;
    private final int sampleCount;
    
    /**
     * Create scale-adaptive parameters for a given number.
     * 
     * @param N the number to factorize
     */
    public ScaleAdaptiveParams(BigInteger N) {
        this.bitLength = N.bitLength();
        this.threshold = calculateThreshold(bitLength);
        this.kShift = calculateKShift(bitLength);
        this.sampleCount = calculateSampleCount(bitLength);
    }
    
    /**
     * Calculate threshold using PR-123 formula:
     * T(N) = 0.92 - 0.10 * log2(bitLen/30)
     * 
     * @param bitLen bit length of the number
     * @return threshold value
     */
    private double calculateThreshold(int bitLen) {
        double ratio = (double) bitLen / 30.0;
        return 0.92 - 0.10 * (Math.log(ratio) / Math.log(2));
    }
    
    /**
     * Calculate k-shift using PR-123 formula:
     * k(N) = 0.35 + 0.0302 * ln(bitLen/30)
     * 
     * @param bitLen bit length of the number
     * @return k-shift value
     */
    private double calculateKShift(int bitLen) {
        double ratio = (double) bitLen / 30.0;
        return 0.35 + 0.0302 * Math.log(ratio);
    }
    
    /**
     * Calculate sample count using PR-123 formula:
     * samples(N) = round(30000 * (bitLen/60))
     * Clamped to minimum 5000.
     * 
     * @param bitLen bit length of the number
     * @return sample count
     */
    private int calculateSampleCount(int bitLen) {
        double ratio = (double) bitLen / 60.0;
        int samples = (int) Math.round(30000 * ratio);
        return Math.max(samples, 5000);
    }
    
    public int getBitLength() {
        return bitLength;
    }
    
    public double getThreshold() {
        return threshold;
    }
    
    public double getKShift() {
        return kShift;
    }
    
    public int getSampleCount() {
        return sampleCount;
    }
    
    @Override
    public String toString() {
        return String.format(
            "ScaleAdaptiveParams{bitLength=%d, threshold=%.4f, kShift=%.4f, sampleCount=%d}",
            bitLength, threshold, kShift, sampleCount
        );
    }
}
