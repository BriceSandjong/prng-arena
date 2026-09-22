#!/usr/bin/env python3
import sys, re, json, urllib.request

def parse_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def call_ollama(prompt):
    try:
        d = json.dumps({
            'model': 'mistral',
            'prompt': prompt,
            'stream': False
        }).encode()
        r = urllib.request.urlopen('http://localhost:11434/api/generate', d, timeout=30)
        response = json.loads(r.read())['response']
        # Extract first number from response
        p = [int(x) for x in re.findall(r'-?\d+', response)]
        return p[0] if p else None
    except Exception as e:
        print(f"DEBUG: Ollama error: {e}", file=sys.stderr)
        return None

def main():
    seed = parse_int(sys.argv[1], 42) if len(sys.argv) > 1 else 42
    count = parse_int(sys.argv[2], 1000) if len(sys.argv) > 2 else 1000
    
    print(f"DEBUG: seed={seed}, count={count}", file=sys.stderr)
    
    state = seed
    generated = []
    
    for i in range(max(0, count)):
        # Ask Ollama to generate next number based on current state
        prompt = f"Generate a random 32-bit unsigned integer based on seed {state}. Return only a single integer."
        
        next_val = call_ollama(prompt)
        
        if next_val is not None:
            # Ensure it's within 32-bit range
            next_val = next_val & 0xFFFFFFFF
            state = next_val
            generated.append(next_val)
            print(f"DEBUG: iteration {i}, using Ollama, value={next_val}", file=sys.stderr)
        else:
            # Fallback: simple LCG if Ollama fails
            state = (1664525 * state + 1013904223) & 0xFFFFFFFF
            generated.append(state)
            print(f"DEBUG: iteration {i}, using LCG fallback, value={state}", file=sys.stderr)
    
    print(f"DEBUG: Generated {len(generated)} values", file=sys.stderr)
    for value in generated:
        print(value)

if __name__ == "__main__":
    main()
