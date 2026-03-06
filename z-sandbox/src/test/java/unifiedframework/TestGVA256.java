package unifiedframework;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.File;
import java.io.PrintWriter;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

import gva.GVAFactorizer;
import java.math.BigInteger;
import java.math.MathContext;

public class TestGVA256 {

  private final GVAFactorizer gva = new GVAFactorizer(new MathContext(200));
  private static PrintWriter pw;

  @ParameterizedTest
  @MethodSource("provideTargets")
  public void test256BitBatch(BigInteger p, BigInteger q) {
    BigInteger N = p.multiply(q);
    long start = System.nanoTime();
    List<BigInteger> factors = gva.build(N, 10, 42);
    long time = System.nanoTime() - start;
    boolean hasFactor = factors.stream().anyMatch(f -> f.equals(p) || f.equals(q));
    pw.println(N.bitLength() + "," + (time / 1e9) + "," + hasFactor);
  }

  public static Stream<Arguments> provideTargets() {
    try {
      pw = new PrintWriter("output/results/gva_results.csv");
      pw.println("N_bits,time_sec,success");
      ObjectMapper mapper = new ObjectMapper();
      Map<String, Object> data = mapper.readValue(new File("output/results/256bit_targets.json"), Map.class);
      List<Map<String, Object>> targets = (List<Map<String, Object>>) data.get("targets");
      return targets.stream().map(t -> Arguments.of(new BigInteger((String) t.get("p")), new BigInteger((String) t.get("q"))));
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  @AfterAll
  static void tearDown() {
    if (pw != null) pw.close();
  }
}
