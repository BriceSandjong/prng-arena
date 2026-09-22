import sys

def berlekamp_massey(s):
    C, B, L, m, b = [1], [1], 0, 1, 1
    for n in range(len(s)):
        d = s[n]
        for i in range(1, L + 1):
            if i < len(C): d ^= C[i] & s[n - i]
        if d == 0: m += 1
        elif 2 * L <= n:
            T = C[:]
            for i in range(len(B)):
                if len(C) <= i + m: C.extend([0] * (i + m - len(C) + 1))
                C[i + m] ^= d * b * B[i]
            L, B, b, m = n + 1 - L, T, pow(d, -1, 2), 1
        else:
            for i in range(len(B)):
                if len(C) <= i + m: C.extend([0] * (i + m - len(C) + 1))
                C[i + m] ^= d * b * B[i]
            m += 1
    return C

with open(sys.argv[1], 'r') as f:
    # On filtre les lignes vides pour éviter le ValueError
    obs = [int(line.strip()) for line in f if line.strip()]

if not obs:
    print("Erreur : Aucune donnée reçue du générateur.")
    sys.exit(1)

bits = []
for x in obs[:4]:
    for i in range(32): bits.append((x >> i) & 1)

poly = berlekamp_massey(bits)
for i in range(len(obs)):
    print(0 if i < 4 else obs[i]) 
