package unifiedframework;

import java.math.BigInteger;
import java.util.Optional;

/**
 * Test 256-bit factorization using enhanced GVA with Gauss-Prime Law improvements.
 */
public class Test256BitFactorization {

    // Hardcoded 256-bit unbiased target (from generation)
    private static final String N_STR = "98370022278116778484828004030285751271924127783874933995276494485359510298647";
    private static final String P_STR = "305670890164289826090221391421870275737";
    private static final String Q_STR = "321816782177869653560766416864591888431";

    public static void main(String[] args) {
        System.out.println("=".repeat(80));
        System.out.println("256-Bit GVA Factorization Test with Gauss-Prime Law Enhancements");
        System.out.println("=".repeat(80));
        System.out.println();

        try {
            BigInteger N = new BigInteger(N_STR);
            BigInteger trueP = new BigInteger(P_STR);
            BigInteger trueQ = new BigInteger(Q_STR);

            System.out.println("Target Information:");
            System.out.println("N = " + N);
            System.out.println("N bits: " + N.bitLength());
            System.out.println("True p = " + trueP);
            System.out.println("True q = " + trueQ);
            System.out.println();

            // Test factorization
            long startTime = System.currentTimeMillis();

            System.out.println("🔍 Starting GVA factorization with Gauss-Legendre seeding...");
            Optional<BigInteger[]> result = GVAFactorizer.factorize(N, 10000000, 11);

            long endTime = System.currentTimeMillis();
            double elapsedSeconds = (endTime - startTime) / 1000.0;

            System.out.println();
            System.out.println("Results:");
            System.out.println("Time elapsed: " + String.format("%.2f", elapsedSeconds) + " seconds");

            if (result.isPresent()) {
                BigInteger[] factors = result.get();
                BigInteger foundP = factors[0];
                BigInteger foundQ = factors[1];

                // Sort to match true factors
                if (foundP.compareTo(foundQ) > 0) {
                    BigInteger temp = foundP;
                    foundP = foundQ;
                    foundQ = temp;
                }

                boolean success = (foundP.equals(trueP) && foundQ.equals(trueQ)) ||
                                (foundP.equals(trueQ) && foundQ.equals(trueP));

                System.out.println("Found p = " + foundP);
                System.out.println("Found q = " + foundQ);
                System.out.println(success ? "✅ SUCCESS: Factors verified!" : "❌ FAILURE: Incorrect factors");

                if (success) {
                    System.out.println();
                    System.out.println("🎉 256-bit factorization breakthrough achieved!");
                    System.out.println("First successful 256-bit GVA factorization with Gauss-Prime Law");
                }
            } else {
                System.out.println("❌ No factors found within timeout");
            }

        } catch (Exception e) {
            System.out.println("❌ Error during test: " + e.getMessage());
            e.printStackTrace();
        }
    }
}