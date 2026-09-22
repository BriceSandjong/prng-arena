import sys

MOD = 2 ** 32
GAMMA = 0x9E3779B9


def parse_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def mix32(z):
    z &= 0xFFFFFFFF
    z = (z ^ (z >> 16)) * 0x85EBCA6B & 0xFFFFFFFF
    z = (z ^ (z >> 13)) * 0xC2B2AE35 & 0xFFFFFFFF
    z ^= z >> 16
    return z & 0xFFFFFFFF


def main():
    seed = parse_int(sys.argv[1], 123456789) if len(sys.argv) > 1 else 123456789
    count = parse_int(sys.argv[2], 1000) if len(sys.argv) > 2 else 1000

    state = seed & 0xFFFFFFFF
    for _ in range(max(0, count)):
        state = (state + GAMMA) & 0xFFFFFFFF
        print(mix32(state))


if __name__ == "__main__":
    main()
