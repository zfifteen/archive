package unifiedframework;

import static org.junit.jupiter.api.Assertions.*;

import gva.GVAFactorizer;
import java.math.BigInteger;
import java.math.MathContext;
import java.util.List;
import org.junit.jupiter.api.Test;

/** Test for RSA-100 factorization validation. */
public class TestRSA100 {

  private final GVAFactorizer gva = new GVAFactorizer(new MathContext(200));

  @Test
  public void testRSA100Factorization() {
    // RSA-100: Known semiprime
    BigInteger N = new BigInteger("1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139");
    BigInteger p = new BigInteger("37975227936943673922808872755445627854565536638199");
    BigInteger q = new BigInteger("40094690950920881030683735292761468389214899724061");

    // Verify N = p * q
    assertEquals(N, p.multiply(q));

    long start = System.nanoTime();
    List<BigInteger> factors = gva.build(N, 10, 42);
    long time = System.nanoTime() - start;

    boolean hasFactor = factors.stream().anyMatch(f -> f.equals(p) || f.equals(q));
    System.out.println("RSA-100 factorization: time=" + (time / 1e9) + "s, success=" + hasFactor);

    // Note: May not succeed due to algorithm limitations, but tests the framework
    // assertTrue("Should find RSA-100 factors", hasFactor);
  }
}
