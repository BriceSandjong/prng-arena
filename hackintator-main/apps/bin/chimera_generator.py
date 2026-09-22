import hashlib
import sys

MOD32 = 2 ** 32
LCG_A = 1664525
LCG_C = 1013904223


def parse_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def xorshift32_next(value):
    value &= 0xFFFFFFFF
    value ^= (value << 13) & 0xFFFFFFFF
    value ^= (value >> 17) & 0xFFFFFFFF
    value ^= (value << 5) & 0xFFFFFFFF
    return value & 0xFFFFFFFF


def hash_step(value, step, seed):
    payload = f"{seed}:{step}:{value}".encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:4], byteorder="big", signed=False)


def rotate_mix(value, step):
    rot = (step % 31) + 1
    value &= 0xFFFFFFFF
    return ((value << rot) | (value >> (32 - rot))) & 0xFFFFFFFF


def next_chimera(state, step, seed):
    mode = (step + (state & 0x3)) % 4

    if mode == 0:
        # LCG branch
        return (LCG_A * state + LCG_C) % MOD32
    if mode == 1:
        # xorshift branch
        return xorshift32_next(state)
    if mode == 2:
        # hash branch
        return hash_step(state, step, seed)

    # rotation-xor branch
    mixed = rotate_mix(state ^ ((seed + step) & 0xFFFFFFFF), step)
    return xorshift32_next(mixed)


def main():
    # Args: [seed] [count]
    seed = parse_int(sys.argv[1], 42) if len(sys.argv) > 1 else 42
    count = parse_int(sys.argv[2], 1000) if len(sys.argv) > 2 else 1000

    state = seed & 0xFFFFFFFF
    for step in range(max(0, count)):
        state = next_chimera(state, step, seed)
        print(state)


if __name__ == "__main__":
    main()
