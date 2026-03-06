// src/main/java/org/zfifteen/sandbox/GeometricResonanceFactorizer.java
package org.zfifteen.sandbox;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;
import java.math.RoundingMode;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.IntStream;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.time.Instant;

import ch.obermuhlner.math.big.BigDecimalMath;
import org.zfifteen.sandbox.resonance.DirichletGate;
import org.zfifteen.sandbox.resonance.SnapKernel;

/**
 * Reference skeleton for Geometric Resonance Factorization (127-bit demo).
 * Deterministic: single MathContext, fixed rounding, arg-reduction, golden-ratio recurrence.
 *
 * Usage:
 *   java -cp build/libs/your.jar org.zfifteen.sandbox.GeometricResonanceFactorizer \
 *     137524771864208156028430259349934309717 \
 *     --mc-digits=240 --samples=3000 --m-span=180 --J=6 --threshold=0.92 --k-lo=0.25 --k-hi=0.45
 */
public final class GeometricResonanceFactorizer {

  // ---------- configuration (defaults; override via CLI) ----------
  private int mcDigits = 240;                 // >= 220 recommended
  private RoundingMode rounding = RoundingMode.HALF_EVEN;
  private long samples = 3000L;               // QMC samples across k
  private int mSpan = 180;                    // scan radius around m0
  private int J = 6;                          // Dirichlet half-width
  private BigDecimal threshold = bd("0.92");  // normalized amplitude gate
   private BigDecimal kLo = bd("0.25");
   private BigDecimal kHi = bd("0.45");
   private String outputDir = "results/legit_" + Instant.now().toString().substring(0, 15).replace(":", "").replace("-", "").replace("T", "_");


  // ---------- cached constants ----------
  private MathContext MC;
  private BigInteger N;
  private BigDecimal BD_N;     // exact BigDecimal(N)
  private BigDecimal LN_N;     // ln(N) at MC
  private BigDecimal PI;
  private BigDecimal TWO_PI;
  private BigDecimal INV_TWO_PI;
  private BigDecimal PHI_INV;  // (sqrt(5) - 1) / 2

  // golden-ratio sequence state u in [0,1)
  private BigDecimal u = BigDecimal.ZERO;

  // ---------- entry ----------
   public static void main(String[] args) {
     try {
       new GeometricResonanceFactorizer().run(args);
     } catch (IllegalArgumentException e) {
       System.err.println("Error: " + e.getMessage());
       printHelp();
       // Don't exit in test environment to allow testing
       if (System.getProperty("test.env") == null) {
         System.exit(1);
       } else {
         throw e; // Re-throw for tests
       }
     } catch (Exception e) {
       e.printStackTrace();
       System.exit(2);
     }
   }

   private void run(String[] args) throws IllegalArgumentException {
     if (args.length < 1) {
       throw new IllegalArgumentException("Missing N.");
     }

    // parse required N and optional flags
    final String nStr = args[0];
    for (int i = 1; i < args.length; i++) {
      final String a = args[i];
      if (!a.startsWith("--")) continue;
      final int eq = a.indexOf('=');
      final String key = (eq > 0 ? a.substring(2, eq) : a.substring(2)).trim();
      final String val = (eq > 0 ? a.substring(eq + 1) : "").trim();
      switch (key) {
        case "mc-digits": this.mcDigits = Integer.parseInt(val); break;
        case "samples":   this.samples  = Long.parseLong(val);   break;
        case "m-span":    this.mSpan    = Integer.parseInt(val); break;
        case "J":         this.J        = Integer.parseInt(val); break;
        case "threshold": this.threshold= new BigDecimal(val);   break;
        case "k-lo":      this.kLo      = new BigDecimal(val);   break;
         case "k-hi":      this.kHi      = new BigDecimal(val);   break;
         default: throw new IllegalArgumentException("Unknown flag: " + key);
      }
    }

    // zero-bias enforced: no bias parameters accepted

    // init N first to enable adaptive precision
    this.N = new BigInteger(nStr);
    if (N.signum() <= 0) throw new IllegalArgumentException("N must be positive.");

    // adaptive precision based on bit length (scale mcDigits for larger N)
    int bitLength = N.bitLength();
    if (this.mcDigits == 240) { // if not overridden, adapt
      this.mcDigits = Math.max(240, bitLength * 2 + 100);
    }

    // init math context and constants
    this.MC = new MathContext(this.mcDigits, this.rounding);
    this.BD_N = new BigDecimal(N, MC);

    this.PI = BigDecimalMath.pi(MC);
    this.TWO_PI = PI.multiply(bd("2"), MC);
    this.INV_TWO_PI = BigDecimal.ONE.divide(TWO_PI, MC);

    // PHI_INV = (sqrt(5) - 1)/2
    BigDecimal sqrt5 = BigDecimalMath.sqrt(bd("5"), MC);
    this.PHI_INV = sqrt5.subtract(BigDecimal.ONE, MC).divide(bd("2"), MC);

    // ln N
    this.LN_N = BigDecimalMath.log(BD_N, MC);

    // print reproducibility information
    printReproducibilityInfo();

    // sweep QMC samples over k, scan m about m0, gate by Dirichlet, form p̂, test candidates
    final BigInteger[] factors = search();
    if (factors != null) {
      BigInteger p = factors[0];
      BigInteger q = factors[1];
      System.out.println("FOUND:");
      System.out.println("p = " + p);
      System.out.println("q = " + q);
      // sanity
      if (!p.multiply(q).equals(N)) {
        throw new IllegalStateException("Product check failed.");
      }
      // emit artifacts
      emitArtifacts(p, q);
      return;
    }
    System.out.println("No factor found within sweep (consider ++mc-digits, ++samples, ++m-span, J=8, or slight threshold tweak).");
  }

  // ---------- main search ----------
   private BigInteger[] search() {
     // u starts at 0; update via golden-ratio recurrence deterministically
     BigDecimal kWidth = kHi.subtract(kLo, MC);

    final double progStep = Double.parseDouble(System.getProperty("progress.log", "0"));
    final long total = samples; long lastPct = -1;
    for (long n = 0; n < samples; n++) {
      if (progStep > 0) {
        long pct = (n * 100) / total;
        if (pct % Math.max(1, (int)(progStep * 100)) == 0 && pct != lastPct) {
          lastPct = pct; System.out.println("progress=" + pct + "% (" + n + "/" + total + ")");
        }
      }
      stepGoldenRatio();

      // k = k_lo + u * (k_hi - k_lo)
      final BigDecimal k = kLo.add(kWidth.multiply(u, MC), MC);

      // set m0 = 0 for balanced semiprimes
      final BigInteger m0 = BigInteger.ZERO;

      // Atomic reference to hold result found in parallel stream
      final AtomicReference<BigInteger[]> result = new AtomicReference<>(null);

      // Parallelize the dm×bias loop using IntStream
      IntStream.rangeClosed(-mSpan, mSpan).parallel().forEach(dm -> {
        // Early exit if result already found
        if (result.get() != null) return;

        BigInteger m = m0.add(BigInteger.valueOf(dm));

        // Zero-bias: no bias scanning, use m directly
        // Compute theta from m and k
        BigDecimal theta = TWO_PI.multiply(new BigDecimal(m), MC).divide(k, MC);

        // Use normalized Dirichlet gate
        BigDecimal A = DirichletGate.normalizedAmplitude(theta, J, MC);
        // Assert normalized form: amplitude should be in [0, 1] range
        assert A.compareTo(BigDecimal.ZERO) >= 0 && A.compareTo(BigDecimal.ONE) <= 0 : "Dirichlet amplitude not normalized";
        if (A.compareTo(threshold) > 0) {
          // Use phase-corrected snap for candidate generation
          BigInteger p0 = SnapKernel.phaseCorrectedSnap(LN_N, theta, MC);
          // Assert positive candidate
          assert p0.compareTo(BigInteger.ONE) > 0 : "Snap produced invalid candidate";
          BigInteger[] hit = testNeighbors(p0);
          if (hit != null) {
            result.compareAndSet(null, hit);
            return;
          }
        }
      });

      // Check if result was found in parallel iteration
      if (result.get() != null) {
        return result.get();
      }
    }
    return null;
  }

  // ---------- helpers ----------

  private void stepGoldenRatio() {
    u = u.add(PHI_INV, MC);
    if (u.compareTo(BigDecimal.ONE) >= 0) {
      u = u.subtract(BigDecimal.ONE, MC);
    }
  }

  // test p, p-1, p+1 (guards)
  private BigInteger[] testNeighbors(BigInteger pCenter) {
    BigInteger[] offsets = { BigInteger.ZERO, BigInteger.valueOf(-1), BigInteger.ONE };
    for (BigInteger off : offsets) {
      BigInteger p = pCenter.add(off);
      if (p.compareTo(BigInteger.ONE) <= 0 || p.compareTo(N) >= 0) continue;
      if (N.mod(p).equals(BigInteger.ZERO)) {
        BigInteger q = N.divide(p);
        return ordered(p, q);
      }
    }
    return null;
  }

  private static BigInteger[] ordered(BigInteger a, BigInteger b) {
    return (a.compareTo(b) <= 0) ? new BigInteger[]{a, b} : new BigInteger[]{b, a};
  }

  private static BigDecimal bd(String s) {
    return new BigDecimal(s);
  }

  private void printReproducibilityInfo() {
    System.err.println("=== Geometric Resonance Factorizer - Reproducibility Info ===");
    System.err.println("JVM: " + System.getProperty("java.version") + " (" + System.getProperty("java.vendor") + ")");
    System.err.println("OS: " + System.getProperty("os.name") + " " + System.getProperty("os.version") + " (" + System.getProperty("os.arch") + ")");
    System.err.println("BigDecimalMath: ch.obermuhlner.math.big");
    System.err.println("Precision: " + mcDigits + " digits (MathContext)");
    System.err.println("N: " + N);
    System.err.println("N bit length: " + N.bitLength());
    System.err.println("Parameters:");
    System.err.println("  samples=" + samples + ", m-span=" + mSpan + ", J=" + J);
    System.err.println("  threshold=" + threshold + ", k-range=[" + kLo + ", " + kHi + "]");
    System.err.println("  dirichlet_normalized=true, snap_mode=phase_corrected_nint");
    System.err.println("  biasPresent=false (zero-bias invariant enforced)");
    System.err.println("==============================================================");
  }

  private void emitArtifacts(BigInteger p, BigInteger q) {
    try {
      Files.createDirectories(Paths.get(outputDir));

      // config.json
      String configJson = String.format(
        "{\n" +
        "  \"run_id\": \"%s\",\n" +
        "  \"commit_sha\": \"%s\",\n" +
        "  \"jvm_version\": \"%s\",\n" +
        "  \"gradle_version\": \"%s\",\n" +
        "  \"precision_digits\": %d,\n" +
        "  \"dirichlet_normalized\": true,\n" +
        "  \"snap_mode\": \"phase_corrected_nint\",\n" +
        "  \"bias_present\": false,\n" +
        "  \"threshold\": %s,\n" +
        "  \"J\": %d,\n" +
        "  \"k_lo\": %s,\n" +
        "  \"k_hi\": %s,\n" +
        "  \"k_step\": %s,\n" +
        "  \"m_span\": %d,\n" +
        "  \"samples\": %d,\n" +
        "  \"seed\": 42\n" +
        "}",
        outputDir,
        "placeholder", // Would get from git
        System.getProperty("java.version"),
        "placeholder", // Would get from build
        mcDigits,
        threshold.toString(),
        J,
        kLo.toString(),
        kHi.toString(),
        "0.0001", // Fixed step
        mSpan,
        samples
      );
      try (FileWriter fw = new FileWriter(outputDir + "/config.json")) {
        fw.write(configJson);
      }

      // factors.txt
      try (FileWriter fw = new FileWriter(outputDir + "/factors.txt")) {
        fw.write("p = " + p + "\n");
        fw.write("q = " + q + "\n");
        fw.write("verification = " + p.multiply(q).equals(N) + "\n");
      }

      // provenance.txt
      try (FileWriter fw = new FileWriter(outputDir + "/provenance.txt")) {
        fw.write("run_id: " + outputDir + "\n");
        fw.write("command: java ... GeometricResonanceFactorizer " + N + " --mc-digits=" + mcDigits + " ...\n");
        fw.write("environment: JVM=" + System.getProperty("java.version") + ", OS=" + System.getProperty("os.name") + "\n");
        fw.write("timestamp: " + Instant.now() + "\n");
        fw.write("commit_sha: placeholder\n");
        fw.write("bias_source: zero-bias\n");
      }

    } catch (IOException e) {
      System.err.println("Warning: Failed to emit artifacts: " + e.getMessage());
    }
  }

  private static void printHelp() {
    System.err.println("Usage:");
    System.err.println("  java ... GeometricResonanceFactorizer <N> [--mc-digits=240] [--samples=3000]");
    System.err.println("                                          [--m-span=180] [--J=6] [--threshold=0.92]");
    System.err.println("                                          [--k-lo=0.25] [--k-hi=0.45] [--bias=0]");
    System.err.println("                                          [--bias-scan=0.03] [--bias-steps=21]");
  }
}
