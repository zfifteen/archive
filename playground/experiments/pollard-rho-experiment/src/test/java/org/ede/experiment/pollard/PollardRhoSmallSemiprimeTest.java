package org.ede.experiment.pollard;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Test suite for small semiprimes: factors in the 8-12 bit range.
 *
 * These tests validate Pollard Rho behavior on the smallest meaningful semiprimes.
 * Expected characteristics:
 * - Quick factor discovery (1-3 iterations average)
 * - Execution time under 1ms
 * - 100% success rate across multiple runs
 *
 * Aligned with Python experiments/pollard_rho/script.py test cases.
 */
@DisplayName("Pollard Rho: Small Semiprimes (8-12 bit factors)")
public class PollardRhoSmallSemiprimeTest {

    @Test
    @DisplayName("should factor product 11 × 13 = 143")
    public void shouldFactorProduct_11_13_ReturnsOneOf_11_Or_13() {
        // Arrange
        long semiprime = 11L * 13L; // 143
        PollardRhoDomainCell cell = new PollardRhoDomainCell(semiprime);

        // Act
        long discoveredFactor = cell.execute();

        // Assert
        assertTrue(discoveredFactor > 0, "Factor discovery failed");
        assertTrue(semiprime % discoveredFactor == 0, "Discovered value is not a factor of " + semiprime);
        assertTrue(discoveredFactor == 11 || discoveredFactor == 13,
                "Discovered factor should be 11 or 13, got " + discoveredFactor);
    }

    @Test
    @DisplayName("should factor product 17 × 19 = 323")
    public void shouldFactorProduct_17_19_ReturnsOneOf_17_Or_19() {
        // Arrange
        long semiprime = 17L * 19L; // 323
        PollardRhoDomainCell cell = new PollardRhoDomainCell(semiprime);

        // Act
        long discoveredFactor = cell.execute();

        // Assert
        assertTrue(discoveredFactor > 0, "Factor discovery failed");
        assertTrue(semiprime % discoveredFactor == 0, "Discovered value is not a factor of " + semiprime);
        assertTrue(discoveredFactor == 17 || discoveredFactor == 19,
                "Discovered factor should be 17 or 19, got " + discoveredFactor);
    }

    @Test
    @DisplayName("should factor product 29 × 31 = 899")
    public void shouldFactorProduct_29_31_ReturnsOneOf_29_Or_31() {
        // Arrange
        long semiprime = 29L * 31L; // 899
        PollardRhoDomainCell cell = new PollardRhoDomainCell(semiprime);

        // Act
        long discoveredFactor = cell.execute();

        // Assert
        assertTrue(discoveredFactor > 0, "Factor discovery failed");
        assertTrue(semiprime % discoveredFactor == 0, "Discovered value is not a factor of " + semiprime);
        assertTrue(discoveredFactor == 29 || discoveredFactor == 31,
                "Discovered factor should be 29 or 31, got " + discoveredFactor);
    }

    @Test
    @DisplayName("should factor product 41 × 47 = 1927")
    public void shouldFactorProduct_41_47_ReturnsOneOf_41_Or_47() {
        // Arrange
        long semiprime = 41L * 47L; // 1927
        PollardRhoDomainCell cell = new PollardRhoDomainCell(semiprime);

        // Act
        long discoveredFactor = cell.execute();

        // Assert
        assertTrue(discoveredFactor > 0, "Factor discovery failed");
        assertTrue(semiprime % discoveredFactor == 0, "Discovered value is not a factor of " + semiprime);
        assertTrue(discoveredFactor == 41 || discoveredFactor == 47,
                "Discovered factor should be 41 or 47, got " + discoveredFactor);
    }

    @Test
    @DisplayName("should factor product 53 × 59 = 3127")
    public void shouldFactorProduct_53_59_ReturnsOneOf_53_Or_59() {
        // Arrange
        long semiprime = 53L * 59L; // 3127
        PollardRhoDomainCell cell = new PollardRhoDomainCell(semiprime);

        // Act
        long discoveredFactor = cell.execute();

        // Assert
        assertTrue(discoveredFactor > 0, "Factor discovery failed");
        assertTrue(semiprime % discoveredFactor == 0, "Discovered value is not a factor of " + semiprime);
        assertTrue(discoveredFactor == 53 || discoveredFactor == 59,
                "Discovered factor should be 53 or 59, got " + discoveredFactor);
    }
}
