# Detailed Command Log for All Runs

## Run 01: Phase 1 Baseline
```bash
./gradlew run --args="137524771864208156028430259349934309717 \
  --mc-digits=220 --samples=1500 --m-span=40 --J=6 \
  --threshold=0.98 --k-lo=0.28 --k-hi=0.32 --bias=0"
```
**Runtime:** 3m 12s  
**Result:** No factor found within sweep

---

## Run 02: Phase 2 (faster, pinned parallelism)
```bash
./gradlew run -Djava.util.concurrent.ForkJoinPool.common.parallelism=8 --args="137524771864208156028430259349934309717 \
  --mc-digits=260 --samples=1500 --m-span=60 --J=4 \
  --threshold=0.992 --k-lo=0.295 --k-hi=0.305 --bias=0"
```
**Runtime:** >6m (timeout)  
**Result:** Incomplete - exceeded timeout

---

## Run 03: Reduced Parameters
```bash
./gradlew run -Djava.util.concurrent.ForkJoinPool.common.parallelism=8 --args="137524771864208156028430259349934309717 \
  --mc-digits=260 --samples=1000 --m-span=40 --J=4 \
  --threshold=0.98 --k-lo=0.29 --k-hi=0.31 --bias=0"
```
**Runtime:** 2m 48s  
**Result:** No factor found within sweep

---

## Run 04: k-range widen with bias
```bash
./gradlew run -Djava.util.concurrent.ForkJoinPool.common.parallelism=8 --args="137524771864208156028430259349934309717 \
  --mc-digits=260 --samples=2000 --m-span=60 --J=4 \
  --threshold=0.98 --k-lo=0.29 --k-hi=0.31 --bias=0.1"
```
**Runtime:** >6m (timeout)  
**Result:** Incomplete - exceeded timeout

---

## Run 05: J=6 with bias
```bash
./gradlew run -Djava.util.concurrent.ForkJoinPool.common.parallelism=8 --args="137524771864208156028430259349934309717 \
  --mc-digits=260 --samples=1500 --m-span=40 --J=6 \
  --threshold=0.98 --k-lo=0.29 --k-hi=0.31 --bias=0.1"
```
**Runtime:** >5m (timeout)  
**Result:** Incomplete - exceeded timeout

---

## Run 06: Small Parameters
```bash
./gradlew run -Djava.util.concurrent.ForkJoinPool.common.parallelism=8 --args="137524771864208156028430259349934309717 \
  --mc-digits=260 --samples=1000 --m-span=30 --J=6 \
  --threshold=0.98 --k-lo=0.29 --k-hi=0.31 --bias=0"
```
**Runtime:** 2m 6s  
**Result:** No factor found within sweep

---

## Run 07: Higher Precision
```bash
./gradlew run -Djava.util.concurrent.ForkJoinPool.common.parallelism=8 --args="137524771864208156028430259349934309717 \
  --mc-digits=300 --samples=1000 --m-span=40 --J=4 \
  --threshold=0.98 --k-lo=0.29 --k-hi=0.31 --bias=0"
```
**Runtime:** 4m 21s  
**Result:** No factor found within sweep

---

## Run 08: Lower Threshold
```bash
./gradlew run -Djava.util.concurrent.ForkJoinPool.common.parallelism=8 --args="137524771864208156028430259349934309717 \
  --mc-digits=260 --samples=1500 --m-span=50 --J=4 \
  --threshold=0.95 --k-lo=0.29 --k-hi=0.31 --bias=0.05"
```
**Runtime:** >5m (timeout)  
**Result:** Incomplete - exceeded timeout

---

## Run 09: Balanced Parameters
```bash
./gradlew run -Djava.util.concurrent.ForkJoinPool.common.parallelism=8 --args="137524771864208156028430259349934309717 \
  --mc-digits=260 --samples=1200 --m-span=30 --J=4 \
  --threshold=0.98 --k-lo=0.29 --k-hi=0.31 --bias=0.05"
```
**Runtime:** 2m 51s  
**Result:** No factor found within sweep

---

## Run 10: Fractional Bias Scan (Recommended)
```bash
./gradlew run --args="137524771864208156028430259349934309717 \
  --samples=1 --m-span=0 --J=6 --threshold=0.98 \
  --k-lo=0.3 --k-hi=0.3 --bias=0 --bias-scan=0.02 --bias-steps=21"
```
**Runtime:** ~5s (fast smoke test)  
**Result:** Tests bias scan functionality with minimal parameters  
**Purpose:** Validates that the bias scan feature can discover fractional bias values automatically instead of requiring hard-coded bias parameters.

---

## Run 11: Expanded Bias Scan
```bash
./gradlew run --args="137524771864208156028430259349934309717 \
  --samples=1000 --m-span=30 --J=6 --threshold=0.98 \
  --k-lo=0.29 --k-hi=0.31 --bias=0 --bias-scan=0.03 --bias-steps=21"
```
**Runtime:** ~5-10m  
**Result:** Full parameter sweep with bias scan enabled  
**Purpose:** Automatically discovers the optimal fractional bias in the range [-0.03, +0.03] around bias=0, which previous runs missed by using fixed bias values.

---

## Success Check (for reference)
If factors are found, output must exactly show:
```
p = 10508623501177419659
q = 13086849276577416863
```
And verify: p * q == 137524771864208156028430259349934309717

---

## Understanding Bias Scan Parameters

**--bias-scan=X**: Sets the half-span for fractional bias scanning. The scan will explore bias values in the range [bias - X, bias + X].

**--bias-steps=N**: Sets the number of bias values to test (must be odd to include the center point). For example:
- `--bias-steps=1`: No scan, uses only the specified `--bias` value
- `--bias-steps=21`: Tests 21 evenly-spaced bias values across the scan range

**Example**: With `--bias=0 --bias-scan=0.02 --bias-steps=21`, the factorizer will test 21 bias values: -0.02, -0.018, -0.016, ..., 0, ..., 0.018, 0.02

This automatic scanning is critical for discovering resonance points that fixed bias values would miss.
