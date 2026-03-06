import random

def bootstrap_ci(data, n_boot=1000, alpha=0.05):
    boots = []
    for _ in range(n_boot):
        sample = [random.choice(data) for _ in data]
        boots.append(sum(sample) / len(sample))
    boots.sort()
    lower = boots[int(n_boot * alpha / 2)]
    upper = boots[int(n_boot * (1 - alpha / 2))]
    return lower, upper