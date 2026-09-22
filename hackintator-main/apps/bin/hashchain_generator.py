import hashlib
import sys


def parse_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def next_value(state: int, step: int) -> int:
    payload = f"{state}:{step}".encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:4], byteorder="big", signed=False)


def main():
    # Args: [seed] [count]
    seed = parse_int(sys.argv[1], 42) if len(sys.argv) > 1 else 42
    count = parse_int(sys.argv[2], 1000) if len(sys.argv) > 2 else 1000

    state = seed & 0xFFFFFFFF
    for step in range(max(0, count)):
        state = next_value(state, step)
        print(state)


if __name__ == "__main__":
    main()
