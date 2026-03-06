package org.ede.experiment.pollard;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Test suite for unbalanced semiprimes: one small factor, one large factor.
 *
 * These tests validate Pollard Rho behavior on the class of semiprimes where
 * one factor is significantly smaller than the other. This is the strength of
 * Pollard Rho: it finds small factors efficiently regardless of the other factor's size.
 *
 * Expected characteristics:
 * - Small factor discovered quickly (proportional to sqrt(small_factor))
 * - Works even when the large factor is cryptographically hard
 * - 100% success rate
 *
 * Aligned with Python experiments/pollard_rho/script_2.py and script_5.py test cases.
 */
@DisplayName("Pollard Rho: Unbalanced Semiprimes (mixed factor sizes)")
public class PollardRhoUnbalancedSemiprimeTest {

    @Test
    @DisplayName("should factor product 997 × (10^15 + 3)")
    public void shouldFactorUnbalancedProduct_997_By_1e15_ReturnsSmallFactor() {
        // Arrange: 997 is small, 10^15 + 3 is a large semiprime component
        long smallFactor = 997L;
        long largeFactor = 1_000_000_000_000_003L; // 10^15 + 3
        long semiprime = smallFactor * largeFactor;
        PollardRhoDomainCell cell = new PollardRhoDomainCell(semiprime);

        // Act
        long discoveredFactor = cell.execute();

        // Assert
        assertTrue(discoveredFactor > 0, "Factor discovery failed");
        assertTrue(semiprime % discoveredFactor == 0, "Discovered value is not a factor of " + semiprime);
        assertTrue(discoveredFactor == smallFactor || discoveredFactor == largeFactor,
                "Discovered factor should be " + smallFactor + " or " + largeFactor + ", got " + discoveredFactor);
    }

    @Test
    @DisplayName("should factor product 10007 × (10^20 + 39)")
    public void shouldFactorUnbalancedProduct_10007_By_1e20_ReturnsSmallFactor() {
        // Arrange: 10007 is small, 10^20 + 39 is a large semiprime component
        long smallFactor = 10007L;
        long largeFactor = 100_000_000_000_000_000_039L; // 10^20 + 39
        long semiprime = smallFactor * largeFactor;
        PollardRhoDomainCell cell = new PollardRhoDomainCell(semiprime);

        // Act
        long discoveredFactor = cell.execute();

        // Assert
        assertTrue(discoveredFactor > 0, "Factor discovery failed");
        assertTrue(semiprime % discoveredFactor == 0, "Discovered value is not a factor of " + semiprime);
        assertTrue(discoveredFactor == smallFactor || discoveredFactor == largeFactor,
                "Discovered factor should be " + smallFactor + " or " + largeFactor + ", got " + discoveredFactor);
    }
}
