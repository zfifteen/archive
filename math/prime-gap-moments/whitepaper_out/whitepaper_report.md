==========================================================================================
PRIME GAP MOMENT DEVIATIONS — REVERSAL, CANCELLATION, AND SHAPE METRICS
==========================================================================================

Data: Cohen (2024) Table moment values for the first n prime gaps (μ1..μ4).
Goal: Diagnose what the apparent 'reversed convergence hierarchy' in |A_k| is really measuring.

Definitions
------------------------------------------------------------------------------------------
A_k(n) = μ_k / (k! (log n)^k) - 1            (Cohen normalization; mixes mean + shape)
B_k(n) = μ_k / (k! μ_1^k) - 1               (shape-only deviation at fixed empirical mean)

Identity (exact):  1 + A_k = (1 + A_1)^k · (1 + B_k)
Interpretation:
  • A_1 captures how μ_1 compares to log n (mean mismatch).
  • B_k captures whether standardized moments are exponential-like once the mean is matched.
  • Small |A_k| for k>=2 can be cancellation between (1+A_1)^k (>1) and (1+B_k) (<1).

Cohen table-derived metrics (signed)
------------------------------------------------------------------------------------------
idx            n  loglog n         A1         A2         A3         A4         B2         B3         B4
-------------------------------------------------------------------------------------------------------
  0    3.510e+03    2.0997   0.142824   0.021912  -0.147752  -0.302968  -0.217554  -0.429011  -0.591366
  1    2.300e+04    2.3069   0.134921   0.044511  -0.094114  -0.240449  -0.189073  -0.380308  -0.542181
  2    1.556e+05    2.4812   0.127301   0.063892  -0.035179  -0.133048  -0.162822  -0.326517  -0.463172
  3    1.078e+06    2.6312   0.120565   0.069695  -0.018947  -0.117345  -0.148105  -0.302761  -0.440187
  4    7.604e+06    2.7628   0.114104   0.074444   0.000850  -0.083349  -0.134369  -0.276244  -0.405021
  5    5.440e+07    2.8799   0.108132   0.076768   0.015240  -0.055941  -0.123121  -0.253904  -0.373914
  6    3.936e+08    2.9852   0.102684   0.077575   0.024939  -0.037454  -0.113773  -0.235558  -0.348946
  7    2.874e+09    3.0810   0.097722   0.077521   0.032092  -0.022673  -0.105787  -0.219736  -0.326913
  8    2.115e+10    3.1686   0.093199   0.076779   0.037268  -0.011254  -0.098993  -0.206049  -0.307710
  9    1.567e+11    3.2495   0.089080   0.075742   0.041064  -0.002127  -0.093040  -0.194069  -0.290691
 10    1.167e+12    3.3245   0.085326   0.074458   0.043869   0.005085  -0.087844  -0.183483  -0.275627
 11    8.731e+12    3.3944   0.081884   0.073074   0.045869   0.010861  -0.083213  -0.174086  -0.262149

Absolute-value 'hierarchies' and why |·| can mislead
------------------------------------------------------------------------------------------
Rows with reversed hierarchy in |A_k| (|A4|<|A3|<|A2|<|A1|): 5/12
Rows with normal hierarchy in |B_k| (|B4|>|B3|>|B2|):         12/12

Important: |A_k| can look 'small' due to a zero crossing. Always inspect signed A_k.

Largest scale decomposition (cancellation check)
------------------------------------------------------------------------------------------
n = 8.7312e+12
A1 = 0.081884  => mean factor (1+A1) = 1.081884
k=2: 1+A2=1.073074  (1+A1)^k=1.170473  (1+B2)=0.916787  product=1.073074
k=3: 1+A3=1.045869  (1+A1)^k=1.266316  (1+B3)=0.825914  product=1.045869
k=4: 1+A4=1.010861  (1+A1)^k=1.370008  (1+B4)=0.737851  product=1.010861

Takeaway: if A1>0 and Bk<0, higher k can have *more* cancellation, yielding smaller |A_k|.
          That is a normalization artifact, not necessarily 'faster convergence' of tails.

A1 vs a simple next-order correction
------------------------------------------------------------------------------------------
If μ1 ≈ log n + log log n - 1, then
  A1(n) ≈ (log log n - 1)/log n

           n  A1 observed     (loglog n - 1)/log n         diff
-----------------------------------------------------------------
   3.510e+03     0.142824                 0.134706     0.008118
   2.300e+04     0.134921                 0.130128     0.004794
   1.556e+05     0.127301                 0.123893     0.003408
   1.078e+06     0.120565                 0.117433     0.003132
   7.604e+06     0.114104                 0.111259     0.002845
   5.440e+07     0.108132                 0.105540     0.002591
   3.936e+08     0.102684                 0.100310     0.002374
   2.874e+09     0.097722                 0.095548     0.002174
   2.115e+10     0.093199                 0.091215     0.001984
   1.567e+11     0.089080                 0.087266     0.001814
   1.167e+12     0.085326                 0.083660     0.001666
   8.731e+12     0.081884                 0.080356     0.001528

This explains why A1 is 'stubborn': it's dominated by the next-order mean correction,
not by tail effects.

Alternative mean proxy normalization: L(n) = log n + log log n - 1
------------------------------------------------------------------------------------------
Define Ã_k(n) = μ_k/(k! L(n)^k) - 1. This removes most of A1.
Observe that Ã_k for k>=2 aligns closely with B_k (shape-only deviation).

           n        Ã1        Ã2        Ã3        Ã4
-------------------------------------------------------
   3.510e+03   0.007154  -0.206318  -0.416668  -0.579546
   2.300e+04   0.004242  -0.182179  -0.372388  -0.534363
   1.556e+05   0.003032  -0.157738  -0.320372  -0.456631
   1.078e+06   0.002802  -0.143323  -0.296883  -0.433885
   7.604e+06   0.002560  -0.129931  -0.270671  -0.398905
   5.440e+07   0.002344  -0.119005  -0.248645  -0.368023
   3.936e+08   0.002158  -0.109944  -0.230598  -0.343308
   2.874e+09   0.001984  -0.102235  -0.215082  -0.321555
   2.115e+10   0.001818  -0.095714  -0.201711  -0.302662
   1.567e+11   0.001668  -0.090011  -0.190029  -0.285945
   1.167e+12   0.001538  -0.085037  -0.179711  -0.271162
   8.731e+12   0.001415  -0.080618  -0.170576  -0.257965

Interpretation: once you normalize by a better mean proxy, the 'reversal' disappears;
you see sub-exponential standardized moments (negative deviations) instead.

Sign-change diagnostics (where |·| plots are most misleading)
------------------------------------------------------------------------------------------
A1 sign changes / zero touches: none in the Cohen table scales.
A2 sign changes / zero touches: none in the Cohen table scales.
A3 sign changes / zero touches in loglog(n) intervals: [(2.6312049013924135, 2.7627988280351716)]
A4 sign changes / zero touches in loglog(n) intervals: [(3.2494959545329984, 3.3245035180348816)]

If A_k crosses zero, |A_k| can appear to 'converge rapidly' even when A_k itself
is not monotonically shrinking.

Control-model sanity checks (conceptual)
------------------------------------------------------------------------------------------
Mean drift alone (a mixture of exponentials with varying means) implies B_k >= 0 for k>=2
by Jensen (x^k convex). Therefore, the observed B_k < 0 cannot be explained by mean drift alone.

A simple way to get B_k < 0 is a sub-exponential shape (e.g., Gamma with shape r>1),
which has smaller standardized moments than Exp at the same mean. Combined with A1>0,
this can produce small |A_k| via cancellation.

Numerical sanity: identity residuals (reconstructed A_k - direct A_k)
------------------------------------------------------------------------------------------
           n   resid A1   resid A2   resid A3   resid A4
------------------------------------------------------------
   3.510e+03          0  2.220e-16  1.110e-16  2.220e-16
   2.300e+04          0  2.220e-16  2.220e-16  1.110e-16
   1.556e+05          0 -2.220e-16 -2.220e-16 -2.220e-16
   1.078e+06          0 -2.220e-16  1.110e-16 -1.110e-16
   7.604e+06          0          0          0  2.220e-16
   5.440e+07          0 -2.220e-16 -4.441e-16 -7.772e-16
   3.936e+08          0          0          0 -2.220e-16
   2.874e+09          0  2.220e-16 -2.220e-16 -1.110e-16
   2.115e+10          0          0          0  1.110e-16
   1.567e+11          0  2.220e-16  2.220e-16  3.331e-16
   1.167e+12          0  2.220e-16          0  2.220e-16
   8.731e+12          0 -2.220e-16          0 -2.220e-16

Residuals should be ~0 up to floating error; this confirms the algebraic decomposition.

Actionable recommendations for future empirical work
------------------------------------------------------------------------------------------
1) Always report A_k *and* B_k. A_k mixes mean mismatch and shape; B_k isolates shape.
2) Plot signed A_k (not only |A_k|). Zero crossings can fake 'fast convergence'.
3) Use windowed moments (e.g., last 10%, last 1%) to reduce history mixing.
4) For tail claims, add tail diagnostics: exceedance rates and conditional tail moments.
5) Test control models: drift-only mixtures cannot produce B_k<0; if primes show B_k<0 robustly,
   that is evidence of additional arithmetic regularity beyond nonstationary means.

==========================================================================================
END OF WHITE PAPER SCRIPT OUTPUT
==========================================================================================