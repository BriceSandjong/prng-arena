import sys
import re
import os

MOD = 2 ** 32
GAMMA = 0x9E3779B9
C1 = 0x85EBCA6B
C2 = 0xC2B2AE35


# --- Modular inverse (extended Euclidean) ---

def _ext_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x, y = _ext_gcd(b % a, a)
    return g, y - (b // a) * x, x


INV_C1 = _ext_gcd(C1, MOD)[1] % MOD
INV_C2 = _ext_gcd(C2, MOD)[1] % MOD


# --- Forward mix32 (identical to generator) ---

def _mix32(z):
    z &= 0xFFFFFFFF
    z = (z ^ (z >> 16)) * C1 & 0xFFFFFFFF   # step 1
    z = (z ^ (z >> 13)) * C2 & 0xFFFFFFFF   # step 2
    z ^= z >> 16                              # step 3
    return z


# --- Inverse mix32 ---
# Each step is a bijection, so the whole function is invertible.
#
# inv(step 3):  z ^ (z>>16)  =>  just apply again (self-inverse for shift>=16)
# inv(step 2):  (y ^ (y>>13)) * C2  =>  multiply by INV_C2, then inv-xorshift-13
# inv(step 1):  (y ^ (y>>16)) * C1  =>  multiply by INV_C1, then inv-xorshift-16
#
# inv_xorshift_k(z): recover y from z = y ^ (y >> k)
#   For k=16 (shift >= half width): one XOR pass suffices.
#   For k=13: two passes needed (13*2=26 > 16, 13*3=39 > 32 so two suffice).

def inv_mix32(z):
    # Undo step 3: z ^= z >> 16
    z = (z ^ (z >> 16)) & 0xFFFFFFFF
    # Undo step 2: z = (z ^ (z>>13)) * C2
    z = (z * INV_C2) & 0xFFFFFFFF
    z ^= z >> 13
    z ^= z >> 26
    z &= 0xFFFFFFFF
    # Undo step 1: z = (z ^ (z>>16)) * C1
    z = (z * INV_C1) & 0xFFFFFFFF
    z = (z ^ (z >> 16)) & 0xFFFFFFFF
    return z


# --- Main ---

def main():
    # Read input: file path passed as argument (launcher convention), or stdin
    arg = " ".join(sys.argv[1:]).replace('"', '').strip()
    if arg and os.path.isfile(arg):
        with open(arg, 'r', encoding='utf-8-sig') as f:
            raw = f.read()
    else:
        raw = sys.stdin.read()

    nombres = [int(n) for n in re.findall(r'\d+', raw)]

    # splitmix32 only needs ONE observed output to fully recover the internal state,
    # because inv_mix32 is a bijection:
    #   state[i]  = inv_mix32(output[i])
    #   state[i+k] = state[i] + k * GAMMA  (mod 2^32)
    #   output[i+k] = mix32(state[i+k])

    recovered_state = None

    for val in nombres:
        if recovered_state is None:
            recovered_state = inv_mix32(val)
            sys.stdout.write("0\n")       # learning phase output (ignored by launcher)
        else:
            recovered_state = (recovered_state + GAMMA) & 0xFFFFFFFF
            sys.stdout.write(f"{_mix32(recovered_state)}\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()