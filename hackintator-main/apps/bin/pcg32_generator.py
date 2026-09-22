import sys

MOD = 2 ** 32
MULTIPLIER = 6364136223846793005
INCREMENT = 1442695040888963407


def parse_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def rotr32(value, rot):
    value &= 0xFFFFFFFF
    rot &= 31
    return ((value >> rot) | (value << ((-rot) & 31))) & 0xFFFFFFFF


def next_pcg32(state):
    oldstate = state
    state = (oldstate * MULTIPLIER + INCREMENT) & 0xFFFFFFFFFFFFFFFF
    xorshifted = (((oldstate >> 18) ^ oldstate) >> 27) & 0xFFFFFFFF
    rot = (oldstate >> 59) & 31
    output = rotr32(xorshifted, rot)
    return state, output


def main():
    seed = parse_int(sys.argv[1], 42) if len(sys.argv) > 1 else 42
    count = parse_int(sys.argv[2], 1000) if len(sys.argv) > 2 else 1000

    state = (seed + INCREMENT) & 0xFFFFFFFFFFFFFFFF
    for _ in range(max(0, count)):
        state, value = next_pcg32(state)
        print(value)


if __name__ == "__main__":
    main()
