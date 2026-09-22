#!/usr/bin/env python3
"""
Random guesser: output random numbers for each input to test the pipeline
"""
import sys
import re
import random

print("[RANDOM GUESSER] Started", file=sys.stderr)
print(f"[RANDOM GUESSER] Args: {sys.argv}", file=sys.stderr)

if len(sys.argv) < 2:
    print("[ERROR] No input file", file=sys.stderr)
    sys.exit(1)

input_file = sys.argv[1]
print(f"[RANDOM GUESSER] Reading from: {input_file}", file=sys.stderr)

try:
    with open(input_file, "r") as f:
        content = f.read()
    
    # Extract all numbers
    numbers = re.findall(r"-?\d+", content)
    print(f"[RANDOM GUESSER] Found {len(numbers)} numbers", file=sys.stderr)
    
    count = 0
    for num_str in numbers:
        try:
            num = int(num_str)
            predicted = random.randint(0, 2**32 - 1)  # Random number 0 to 2^32-1
            print(predicted)
            count += 1
        except Exception as e:
            print(f"[RANDOM GUESSER] Error processing {num_str}: {e}", file=sys.stderr)
            print(random.randint(0, 2**32 - 1))
    
    print(f"[RANDOM GUESSER] Output {count} predictions", file=sys.stderr)
                
except Exception as e:
    print(f"[ERROR] {e}", file=sys.stderr)
    sys.exit(1)
