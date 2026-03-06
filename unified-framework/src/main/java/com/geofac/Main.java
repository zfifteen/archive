package com.geofac;

import java.math.BigInteger;
import java.util.logging.ConsoleHandler;
import java.util.logging.Handler;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.logging.SimpleFormatter;

/**
 * Main entry point for geofac factorization service.
 * Supports Gate-127 challenge with PR-123 scaling integration.
 */
public class Main {
    
    private static final Logger LOGGER = Logger.getLogger(Main.class.getName());
    
    // Gate-127 challenge number
    private static final String GATE_127 = "137524771864208156028430259349934309717";
    
    // Expected factors for validation
    private static final String EXPECTED_P = "10508623501177419659";
    private static final String EXPECTED_Q = "13086849276577416863";
    
    public static void main(String[] args) {
        setupLogging();
        
        String numberToFactor = null;
        
        // Parse command line arguments
        if (args.length >= 2 && "--factor".equals(args[0])) {
            numberToFactor = args[1];
        } else {
            LOGGER.info("No number specified, using Gate-127 challenge");
            numberToFactor = GATE_127;
        }
        
        LOGGER.info("========================================");
        LOGGER.info("  Geofac Gate-127 Factorization Tool");
        LOGGER.info("  PR-123 Scaling Integration");
        LOGGER.info("========================================");
        LOGGER.info("");
        
        try {
            BigInteger N = new BigInteger(numberToFactor);
            LOGGER.info(String.format("Target number: %s", N));
            LOGGER.info("");
            
            // Create factorizer service
            FactorizerService service = new FactorizerService();
            
            // Attempt factorization
            long startTime = System.currentTimeMillis();
            BigInteger[] factors = service.factor(N);
            long endTime = System.currentTimeMillis();
            
            LOGGER.info("");
            LOGGER.info(String.format("Factorization time: %d ms", endTime - startTime));
            LOGGER.info("");
            
            // Validate results
            if (factors != null) {
                boolean valid = service.validateFactors(N, factors);
                
                if (valid) {
                    LOGGER.info("");
                    LOGGER.info("========================================");
                    LOGGER.info("  ✓ GATE-127 FACTORIZATION SUCCESSFUL");
                    LOGGER.info("========================================");
                    
                    // Check against expected factors
                    BigInteger expectedP = new BigInteger(EXPECTED_P);
                    BigInteger expectedQ = new BigInteger(EXPECTED_Q);
                    
                    boolean matchesExpected = 
                        (factors[0].equals(expectedP) && factors[1].equals(expectedQ)) ||
                        (factors[0].equals(expectedQ) && factors[1].equals(expectedP));
                    
                    if (matchesExpected) {
                        LOGGER.info("✓ Factors match expected values!");
                    } else {
                        LOGGER.warning("⚠ Factors differ from expected values");
                        LOGGER.info(String.format("Expected: %s * %s", expectedP, expectedQ));
                    }
                    
                    System.exit(0);
                } else {
                    LOGGER.severe("✗ Factor validation failed");
                    System.exit(1);
                }
            } else {
                LOGGER.severe("✗ Factorization failed - no factors found");
                System.exit(1);
            }
            
        } catch (NumberFormatException e) {
            LOGGER.severe("Invalid number format: " + numberToFactor);
            System.exit(1);
        } catch (Exception e) {
            LOGGER.severe("Error during factorization: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
    
    /**
     * Setup logging configuration for verbose output.
     */
    private static void setupLogging() {
        Logger rootLogger = Logger.getLogger("");
        rootLogger.setLevel(Level.INFO);
        
        // Remove default handlers
        for (Handler handler : rootLogger.getHandlers()) {
            rootLogger.removeHandler(handler);
        }
        
        // Add console handler with simple formatting
        ConsoleHandler handler = new ConsoleHandler();
        handler.setLevel(Level.INFO);
        handler.setFormatter(new SimpleFormatter());
        rootLogger.addHandler(handler);
    }
}
