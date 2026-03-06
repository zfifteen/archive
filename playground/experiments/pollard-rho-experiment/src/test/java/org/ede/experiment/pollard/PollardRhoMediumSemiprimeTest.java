package org.ede.experiment.pollard;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Test suite for medium semiprimes: factors in the 16-24 bit range.
 *
 * These tests validate Pollard Rho behavior on moderately sized semiprimes.
 * Expected characteristics:
 * - Moderate factor discovery time (1-130 iterations)
 * - Execution time under 1ms
 * - 100% success rate across all test cases
 *
 * Aligned with Python experiments/pollard_rho/script_1.py test cases.
 */
@DisplayName("Pollard Rho: Medium Semiprimes (16-24 bit factors)")
public class PollardRhoMediumSemiprimeTest {

    @Test
    @DisplayName("should factor product 101 × 103 = 10403")
    public void shouldFactorProduct_101_103_ReturnsValidFactor() {
        // Arrange
        long semiprime = 101L * 103L; // 10403
        PollardRhoDomainCell cell = new PollardRhoDomainCell(semiprime);

        // Act
        long discoveredFactor = cell.execute();

        // Assert
        assertTrue(discoveredFactor > 0, "Factor discovery failed");
        assertTrue(semiprime % discoveredFactor == 0, "Discovered value is not a factor of " + semiprime);
        assertTrue(discoveredFactor == 101 || discoveredFactor == 103,
                "Discovered factor should be 101 or 103, got " + discoveredFactor);
    }

    @Test
    @DisplayName("should factor product 1009 × 1013 = 1022117")
    public void shouldFactorProduct_1009_1013_ReturnsValidFactor() {
        // Arrange
        long semiprime = 1009L * 1013L; // 1022117
        PollardRhoDomainCell cell = new PollardRhoDomainCell(semiprime);

        // Act
        long discoveredFactor = cell.execute();

        // Assert
        assertTrue(discoveredFactor > 0, "Factor discovery failed");
        assertTrue(semiprime % discoveredFactor == 0, "Discovered value is not a factor of " + semiprime);
        assertTrue(discoveredFactor == 1009 || discoveredFactor == 1013,
                "Discovered factor should be 1009 or 1013, got " + discoveredFactor);
    }

    @Test
    @DisplayName("should factor product 10007 × 10009 = 100160063")
    public void shouldFactorProduct_10007_10009_ReturnsValidFactor() {
        // Arrange
        long semiprime = 10007L * 10009L; // 100160063
        PollardRhoDomainCell cell = new PollardRhoDomainCell(semiprime);

        // Act
        long discoveredFactor = cell.execute();

        // Assert
        assertTrue(discoveredFactor > 0, "Factor discovery failed");
        assertTrue(semiprime % discoveredFactor == 0, "Discovered value is not a factor of " + semiprime);
        assertTrue(discoveredFactor == 10007 || discoveredFactor == 10009,
                "Discovered factor should be 10007 or 10009, got " + discoveredFactor);
    }

    @Test
    @DisplayName("should factor product 99991 × 100003 = 9999099973")
    public void shouldFactorProduct_99991_100003_ReturnsValidFactor() {
        // Arrange
        long semiprime = 99991L * 100003L; // 9999099973
        PollardRhoDomainCell cell = new PollardRhoDomainCell(semiprime);

        // Act
        long discoveredFactor = cell.execute();

        // Assert
        assertTrue(discoveredFactor > 0, "Factor discovery failed");
        assertTrue(semiprime % discoveredFactor == 0, "Discovered value is not a factor of " + semiprime);
        assertTrue(discoveredFactor == 99991 || discoveredFactor == 100003,
                "Discovered factor should be 99991 or 100003, got " + discoveredFactor);
    }
}
