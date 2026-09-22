import sys

MOD = 2 ** 32


def parse_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def next_xorshift32(value):
    value &= 0xFFFFFFFF
    value ^= (value << 13) & 0xFFFFFFFF
    value ^= (value >> 17) & 0xFFFFFFFF
    value ^= (value << 5) & 0xFFFFFFFF
    return value & 0xFFFFFFFF


def main():
    seed = parse_int(sys.argv[1], 2463534242) if len(sys.argv) > 1 else 2463534242
    count = parse_int(sys.argv[2], 1000) if len(sys.argv) > 2 else 1000

    value = seed & 0xFFFFFFFF
    if value == 0:
        value = 2463534242

    for _ in range(max(0, count)):
        value = next_xorshift32(value)
        print(value)


if __name__ == "__main__":
    main()
