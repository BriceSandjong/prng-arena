#!/usr/bin/env python3
"""
DEBUG VERSION: Mistral Ollama-based PRNG Guesser
With extensive logging to understand what's failing
"""

import sys
import re
import requests
import json
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"
TIMEOUT = 300  # 5 minutes - Ollama can be slow on first load

# Debug output - write immediately
print("[DEBUG START]", file=sys.stderr)

def main():
    print(f"[DEBUG] Script started with args: {sys.argv}", file=sys.stderr)
    
    if len(sys.argv) < 2:
        print("ERROR: No input file provided", file=sys.stderr)
        return

    input_file = sys.argv[1]
    print(f"[DEBUG] Input file: {input_file}", file=sys.stderr)

    try:
        # Read the file
        if not Path(input_file).exists():
            print(f"[ERROR] File not found: {input_file}", file=sys.stderr)
            raise FileNotFoundError(input_file)
            
        with open(input_file, "r") as f:
            content = f.read()
        print(f"[DEBUG] Read {len(content)} bytes from file", file=sys.stderr)
        print(f"[DEBUG] Content preview: {content[:100]}", file=sys.stderr)
        
        lines = content.strip().split("\n")
        print(f"[DEBUG] Parsed {len(lines)} lines", file=sys.stderr)
        
        # Extract numbers
        numbers = re.findall(r"-?\d+", "\n".join(lines))
        numbers = [int(n) for n in numbers[:20]]
        print(f"[DEBUG] Extracted {len(numbers)} numbers: {numbers}", file=sys.stderr)

        if len(numbers) < 3:
            print(f"[ERROR] Not enough data: {len(numbers)} numbers", file=sys.stderr)
            print("0")
            print("0")
            print("0")
            return

        # Prepare prompt
        recent = numbers[-10:]
        prompt = (
            f"Given this PRNG sequence: {recent}\n"
            f"Predict the next 3 numbers.\n"
            f"Answer with only the numbers, one per line.\n"
        )
        print(f"[DEBUG] Prompt ready, querying Ollama...", file=sys.stderr)

        # Query Ollama
        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.1,
                },
                timeout=TIMEOUT,
            )
            response.raise_for_status()
            response_text = response.json().get("response", "")
            print(f"[DEBUG] Ollama response ({len(response_text)} chars): {response_text[:100]}", file=sys.stderr)
        except requests.exceptions.ConnectionError:
            print(f"[ERROR] Cannot connect to Ollama at {OLLAMA_URL}", file=sys.stderr)
            print("0")
            print("0")
            print("0")
            return
        except Exception as e:
            print(f"[ERROR] Ollama query failed: {e}", file=sys.stderr)
            print("0")
            print("0")
            print("0")
            return
        
        predictions = re.findall(r"-?\d+", response_text)
        predictions = [int(p) for p in predictions[:3]]
        print(f"[DEBUG] Extracted {len(predictions)} predictions: {predictions}", file=sys.stderr)

        # Print predictions
        for pred in predictions:
            print(pred)
            
        if len(predictions) < 3:
            for _ in range(3 - len(predictions)):
                print("0")

    except Exception as e:
        print(f"[EXCEPTION] {e}", file=sys.stderr)
        print("0")
        print("0")
        print("0")


if __name__ == "__main__":
    main()
    print("[DEBUG END]", file=sys.stderr)
