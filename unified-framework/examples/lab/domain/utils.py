import math
import csv
from abc import ABC

class UniversalZetaShift(ABC):
    def __init__(self, a, b, c):
        if c == 0:
            raise ValueError("Universal invariant C cannot be zero.")
        self.a = a
        self.b = b
        self.c = c

    def compute_z(self):
        return self.a * (self.b / self.c)

    def getD(self):
        if self.a == 0:
            raise ValueError("Division by zero: 'a' cannot be zero in getD().")
        return self.c / self.a

    def getE(self):
        if self.b == 0:
            raise ValueError("Division by zero: 'b' cannot be zero in getE().")
        return self.c / self.b

    def getF(self):
        return self.getD() / self.getE()

    def getG(self):
        f = self.getF()
        if f == 0:
            raise ValueError("Division by zero: 'F' cannot be zero in getG().")
        return self.getE() / f

    def getH(self):
        g = self.getG()
        if g == 0:
            raise ValueError("Division by zero: 'G' cannot be zero in getH().")
        return self.getF() / g

    def getI(self):
        h = self.getH()
        if h == 0:
            raise ValueError("Division by zero: 'H' cannot be zero in getI().")
        return self.getG() / h

    def getJ(self):
        i = self.getI()
        if i == 0:
            raise ValueError("Division by zero: 'I' cannot be zero in getJ().")
        return self.getH() / i

    def getK(self):
        j = self.getJ()
        if j == 0:
            raise ValueError("Division by zero: 'J' cannot be zero in getK().")
        return self.getI() / j

    def getL(self):
        k = self.getK()
        if k == 0:
            raise ValueError("Division by zero: 'K' cannot be zero in getL().")
        return self.getJ() / k

    def getM(self):
        l = self.getL()
        if l == 0:
            raise ValueError("Division by zero: 'L' cannot be zero in getM().")
        return self.getK() / l

    def getN(self):
        m = self.getM()
        if m == 0:
            raise ValueError("Division by zero: 'M' cannot be zero in getN().")
        return self.getL() / m

    def getO(self):
        n = self.getN()
        if n == 0:
            raise ValueError("Division by zero: 'N' cannot be zero in getO().")
        return self.getM() / n

# Parameters
MAX_N = 100000
UNIVERSAL_C = math.e  # Invariant anchor

# Generate data
data = []
headers = ['n', 'a', 'b', 'c', 'z', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']

for n in range(1, MAX_N + 1):
    a = float(n)
    b = math.log(n + 1)  # Frame shift rate proxy
    try:
        shift = UniversalZetaShift(a, b, UNIVERSAL_C)
        row = [
            n,
            a,
            b,
            UNIVERSAL_C,
            shift.compute_z(),
            shift.getD(),
            shift.getE(),
            shift.getF(),
            shift.getG(),
            shift.getH(),
            shift.getI(),
            shift.getJ(),
            shift.getK(),
            shift.getL(),
            shift.getM(),
            shift.getN(),
            shift.getO()
        ]
    except ValueError as e:
        # Handle any division errors gracefully with inf or nan
        row = [n, a, b, UNIVERSAL_C] + [float('nan')] * 13
    data.append(row)

# Write to CSV
with open('zeta_shifts_1_to_6000.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(headers)
    writer.writerows(data)

print(f"CSV file 'zeta_shifts_1_to_6000.csv' generated with {MAX_N} ZetaShift records.")