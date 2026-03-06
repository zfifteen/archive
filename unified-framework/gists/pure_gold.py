import sympy as sp
import numpy as np

def beatty_mr_test(n, num_streams=3):
    if n < 2: return False
    if n == 2 or n == 3: return True
    if n % 2 == 0 or n % 3 == 0: return False

    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1

    # Deterministic witnesses from φ-streams (floor(φ^k) mod n for k=1,2,3)
    phi = (1 + 5**0.5) / 2
    witnesses = []
    current = 1.0
    for k in range(1, num_streams + 1):
        current *= phi
        a = int(current) % n
        if a == 0 or a == n: a = 2  # Avoid trivial
        witnesses.append(a)

    for a in witnesses:
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        cont = False
        for _ in range(1, r):
            x = pow(x, 2, n)
            if x == n - 1:
                cont = True
                break
        if not cont: return False
    return True

# Test set: Balanced primes/composites up to 10^5
N = 100000
primes = list(sp.primerange(2, N))
# Balanced composites: Mix evens and odds
composites = list(range(4, N, 2))[:len(primes)//2] + [9,15,21,25,27,33,35,39,45,49,51,55,57,63,65,69,75,77,81,85,87,91,93,95,99] * (len(primes)//2 // 25)
composites = composites[:len(primes)]  # Balance
all_nums = primes + composites
true_labels = [True] * len(primes) + [False] * len(composites)

# Accuracy
acc_beatty = np.mean([beatty_mr_test(num, 3) == label for num, label in zip(all_nums, true_labels)])
fp_beatty = sum(beatty_mr_test(num, 3) for num in composites) / len(composites) * 100 if composites else 0

print(f'GBMR Accuracy: {acc_beatty * 100:.2f}%')
print(f'GBMR FP Rate: {fp_beatty:.2f}%')

# Bootstrap CI
np.random.seed(42)
boot_acc = []
for _ in range(1000):
    res_sample = np.random.choice(len(all_nums), len(all_nums), replace=True)
    res_acc = np.mean([beatty_mr_test(all_nums[idx], 3) == true_labels[idx] for idx in res_sample])
    boot_acc.append(res_acc * 100)
ci_low, ci_high = np.percentile(boot_acc, [2.5, 97.5])
print(f'Accuracy CI: [{ci_low:.1f}%, {ci_high:.1f}%]')
