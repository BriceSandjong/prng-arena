import sys
import math
import random


def is_prime(n):
    if n < 2: return False
    if n % 2 == 0: return n == 2
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0: return False
    return True


def gen_prime_3mod4(rng, low, high):
    """Génère un premier ≡ 3 mod 4 dans [low, high]."""
    while True:
        c = rng.randint(low, high)
        c = (c & ~3) | 3   # force les 2 derniers bits à 11 → c ≡ 3 mod 4
        if is_prime(c):
            return c


if len(sys.argv) != 3:
    sys.exit(1)

seed     = int(sys.argv[1])
n_output = int(sys.argv[2])

rng = random.Random(seed)

# p, q dans [46000, 59999] → n = p*q < 2^32 garanti (59999² ≈ 3.6e9 < 4.29e9)
# Condition BBS : p ≡ 3 mod 4, q ≡ 3 mod 4, p ≠ q, p et q premiers
p = gen_prime_3mod4(rng, 46000, 59999)
q = gen_prime_3mod4(rng, 46000, 59999)
while q == p:
    q = gen_prime_3mod4(rng, 46000, 59999)

n = p * q   # module de Blum, < 2^32

# Seed BBS : coprime avec n (≠ 0, ≠ 1, ≠ p, ≠ q)
x = rng.randint(2, n - 2)
while math.gcd(x, n) != 1:
    x = rng.randint(2, n - 2)

for _ in range(n_output):
    x = (x * x) % n        # x < n < 2^32 : pas besoin de masque
    sys.stdout.write(f"{x}\n")
    sys.stdout.flush()