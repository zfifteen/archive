package com.geofac.util;

import java.math.BigInteger;
import java.math.MathContext;
import java.math.RoundingMode;

/**
 * Utility class for precision calculations in geofac factorization.
 * Implements PR-123 precision scaling for 127-bit challenge.
 */
public class PrecisionUtil {
    
    /**
     * Calculate precision required for a given bit length.
     * For 127-bit: precision = 4 * bitLen + 200
     * 
     * @param N the number to factorize
     * @return the precision value
     */
    public static int calculatePrecision(BigInteger N) {
        int bitLen = N.bitLength();
        return 4 * bitLen + 200;
    }
    
    /**
     * Create a MathContext with calculated precision.
     * 
     * @param N the number to factorize
     * @return MathContext with appropriate precision
     */
    public static MathContext createMathContext(BigInteger N) {
        int precision = calculatePrecision(N);
        return new MathContext(precision, RoundingMode.HALF_UP);
    }
    
    /**
     * Get bit length of a number.
     * 
     * @param N the number
     * @return bit length
     */
    public static int getBitLength(BigInteger N) {
        return N.bitLength();
    }
}
