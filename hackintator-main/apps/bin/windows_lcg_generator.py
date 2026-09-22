import sys


def parse_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def main():
    # Args: [seed] [count]
    seed = parse_int(sys.argv[1], 123456789) if len(sys.argv) > 1 else 123456789
    count = parse_int(sys.argv[2], 1000) if len(sys.argv) > 2 else 1000

    # Simple LCG constants (Numerical Recipes)
    a = 1664525
    c = 1013904223
    m = 2 ** 32

    x = seed
    for _ in range(max(0, count)):
        x = (a * x + c) % m
        print(x)


if __name__ == "__main__":
    main()
