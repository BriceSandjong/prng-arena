#!/usr/bin/env python3
import sys, re, json, urllib.request, threading

LCG_A = 1664525
LCG_C = 1013904223
MOD32 = 0xFFFFFFFF

def parse_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def call_ollama_batch(seed, result_list):
    """Try to get 10 numbers from Ollama based on seed, but don't block if it fails"""
    try:
        prompt = f"Generate 10 random 32-bit unsigned integers as a sequence starting from seed {seed}. Return only the 10 integers separated by spaces or commas, no other text."
        d = json.dumps({
            'model': 'qwen',
            'prompt': prompt,
            'stream': False
        }).encode()
        r = urllib.request.urlopen('http://localhost:11434/api/generate', d, timeout=5)
        response = json.loads(r.read())['response']
        # Extract numbers from response
        numbers = [int(x) & MOD32 for x in re.findall(r'-?\d+', response)]
        if len(numbers) >= 10:
            result_list.extend(numbers[:10])
        elif len(numbers) > 0:
            result_list.extend(numbers)
    except:
        pass

def generate_lcg_batch(seed, count):
    """Generate batch of numbers using LCG"""
    numbers = []
    state = seed
    for _ in range(count):
        state = (LCG_A * state + LCG_C) & MOD32
        numbers.append(state)
    return numbers

def main():
    seed = parse_int(sys.argv[1], 42) if len(sys.argv) > 1 else 42
    count = parse_int(sys.argv[2], 1000) if len(sys.argv) > 2 else 1000
    
    state = seed
    generated = 0
    
    while generated < count:
        batch_size = min(10, count - generated)
        
        # Try to get batch from Ollama (non-blocking)
        result = []
        thread = threading.Thread(target=call_ollama_batch, args=(state, result), daemon=True)
        thread.start()
        thread.join(timeout=3)  # Wait max 3s for Ollama batch response
        
        # Use Ollama result if available, otherwise use LCG
        if result:
            batch = result[:batch_size]
        else:
            batch = generate_lcg_batch(state, batch_size)
        
        # Output batch
        for num in batch:
            print(num)
            generated += 1
        
        # Update state for next batch
        if batch:
            state = batch[-1]

if __name__ == "__main__":
    main()
