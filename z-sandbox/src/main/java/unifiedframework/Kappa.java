package unifiedframework;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;
import java.util.Arrays;
import java.util.Random;

/**
 * Kappa curvature signal implementation for RSA challenge analysis.
 */
public class Kappa {

    private static final double E_SQ = Math.exp(2.0);
    private static final BigInteger AUTO_APPROX_THRESHOLD = BigInteger.valueOf(10).pow(20);

    /**
     * Compute κ(n) = d(n) * ln(n) / e^2.
     */
    public static double kappa(BigInteger n, Boolean useApproximation, boolean highPrecision, MathContext mc) {
        if (n.compareTo(BigInteger.ZERO) <= 0) {
            throw new IllegalArgumentException("n must be positive");
        }
        boolean approx = useApproximation == null ? n.compareTo(AUTO_APPROX_THRESHOLD) > 0 : useApproximation;
        int d = approx ? 4 : divisorCount(n).intValue();
        double lnN = Math.log(n.doubleValue());
        double result = d * lnN / E_SQ;
        if (highPrecision) {
            BigDecimal bigD = BigDecimal.valueOf(d);
            BigDecimal bigLnN = BigDecimal.valueOf(lnN);
            BigDecimal bigESq = BigDecimal.valueOf(E_SQ);
            BigDecimal bigResult = bigD.multiply(bigLnN, mc).divide(bigESq, mc);
            return bigResult.doubleValue();
        }
        return result;
    }

    private static BigInteger divisorCount(BigInteger n) {
        BigInteger count = BigInteger.ZERO;
        BigInteger i = BigInteger.ONE;
        while (i.multiply(i).compareTo(n) <= 0) {
            if (n.mod(i).equals(BigInteger.ZERO)) {
                count = count.add(BigInteger.ONE);
                BigInteger div = n.divide(i);
                if (!i.equals(div)) {
                    count = count.add(BigInteger.ONE);
                }
            }
            i = i.add(BigInteger.ONE);
        }
        return count;
    }

    /**
     * Batch computation of κ(n).
     */
    public static double[] batchKappa(BigInteger[] ns, Boolean useApproximation, boolean highPrecision, MathContext mc) {
        double[] results = new double[ns.length];
        for (int i = 0; i < ns.length; i++) {
            results[i] = kappa(ns[i], useApproximation, highPrecision, mc);
        }
        return results;
    }

    /**
     * Bootstrap confidence interval.
     */
    public static double[] bootstrapCi(double[] data, int nResamples, long seed, double alpha) {
        if (data.length < 10) {
            System.out.println("Warning: Bootstrap on small sample size is unreliable");
        }
        Random rand = new Random(seed);
        double[] stats = new double[nResamples];
        for (int i = 0; i < nResamples; i++) {
            double sum = 0;
            for (int j = 0; j < data.length; j++) {
                sum += data[rand.nextInt(data.length)];
            }
            stats[i] = sum / data.length;
        }
        Arrays.sort(stats);
        int lowerIdx = (int) Math.floor(nResamples * (alpha / 2));
        int upperIdx = (int) Math.ceil(nResamples * (1 - alpha / 2)) - 1;
        return new double[]{stats[lowerIdx], stats[upperIdx]};
    }

    /**
     * Fit linear model κ ~ a * ln(n) + b.
     */
    public static double[] fitLinearLnVsKappa(BigInteger[] ns, double[] kappas) {
        int n = ns.length;
        double[] x = new double[n];
        for (int i = 0; i < n; i++) {
            x[i] = Math.log(ns[i].doubleValue());
        }
        double sumX = 0, sumY = 0, sumXY = 0, sumXX = 0;
        for (int i = 0; i < n; i++) {
            sumX += x[i];
            sumY += kappas[i];
            sumXY += x[i] * kappas[i];
            sumXX += x[i] * x[i];
        }
        double slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
        double intercept = (sumY - slope * sumX) / n;
        double ssRes = 0, ssTot = 0;
        double meanY = sumY / n;
        for (int i = 0; i < n; i++) {
            double pred = slope * x[i] + intercept;
            ssRes += (kappas[i] - pred) * (kappas[i] - pred);
            ssTot += (kappas[i] - meanY) * (kappas[i] - meanY);
        }
        double r2 = 1 - ssRes / ssTot;
        return new double[]{slope, intercept, r2};
    }
}