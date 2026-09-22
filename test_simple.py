#!/usr/bin/env python3
import sys

def parse_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def main():
    seed = parse_int(sys.argv[1], 42) if len(sys.argv) > 1 else 42
    count = parse_int(sys.argv[2], 1000) if len(sys.argv) > 2 else 1000
    
    state = seed
    
    for _ in range(max(0, count)):
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        print(state)

if __name__ == "__main__":
    main()
