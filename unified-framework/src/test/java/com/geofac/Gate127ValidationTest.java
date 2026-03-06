package com.geofac;

import org.junit.Test;
import java.math.BigInteger;
import static org.junit.Assert.*;

/**
 * Validation test for Gate-127 challenge factorization.
 * 
 * This test verifies that:
 * 1. The factorizer can factor N = 137524771864208156028430259349934309717
 * 2. The factors match the expected values p and q
 * 3. The product p * q equals N
 */
public class Gate127ValidationTest {
    
    // Gate-127 challenge number
    private static final String GATE_127_N = "137524771864208156028430259349934309717";
    
    // Expected factors
    private static final String EXPECTED_P = "10508623501177419659";
    private static final String EXPECTED_Q = "13086849276577416863";
    
    @Test
    public void testGate127Factorization() {
        System.out.println("=== Gate-127 Validation Test ===");
        
        // Parse input
        BigInteger N = new BigInteger(GATE_127_N);
        BigInteger expectedP = new BigInteger(EXPECTED_P);
        BigInteger expectedQ = new BigInteger(EXPECTED_Q);
        
        System.out.println("Target N: " + N);
        System.out.println("Expected p: " + expectedP);
        System.out.println("Expected q: " + expectedQ);
        
        // Create factorizer and attempt factorization
        FactorizerService service = new FactorizerService();
        BigInteger[] factors = service.factor(N);
        
        // Assert factors were found
        assertNotNull("Factors should not be null", factors);
        assertEquals("Should return exactly 2 factors", 2, factors.length);
        
        BigInteger p = factors[0];
        BigInteger q = factors[1];
        
        System.out.println("Found p: " + p);
        System.out.println("Found q: " + q);
        
        // Verify factors multiply to N
        BigInteger product = p.multiply(q);
        assertEquals("Product of factors should equal N", N, product);
        
        // Verify factors match expected values (order independent)
        boolean matchesExpected = 
            (p.equals(expectedP) && q.equals(expectedQ)) ||
            (p.equals(expectedQ) && q.equals(expectedP));
        
        assertTrue("Factors should match expected values", matchesExpected);
        
        // Validate factors are proper (not 1 or N)
        assertNotEquals("p should not be 1", BigInteger.ONE, p);
        assertNotEquals("p should not be N", N, p);
        assertNotEquals("q should not be 1", BigInteger.ONE, q);
        assertNotEquals("q should not be N", N, q);
        
        System.out.println("=== ✓ All validations passed ===");
    }
    
    @Test
    public void testFactorValidation() {
        System.out.println("=== Factor Validation Test ===");
        
        BigInteger N = new BigInteger(GATE_127_N);
        BigInteger p = new BigInteger(EXPECTED_P);
        BigInteger q = new BigInteger(EXPECTED_Q);
        
        // Test the validation method directly
        FactorizerService service = new FactorizerService();
        BigInteger[] factors = new BigInteger[]{p, q};
        
        boolean isValid = service.validateFactors(N, factors);
        assertTrue("Factors should validate correctly", isValid);
        
        System.out.println("=== ✓ Validation method works correctly ===");
    }
}
