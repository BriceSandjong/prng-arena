#!/usr/bin/env python3
import urllib.request, json, re, time

# Test 1: Simple request
print('Test 1: Simple prompt')
start = time.time()
try:
  d = json.dumps({'model':'qwen','prompt':'What is 2+2?','stream':False}).encode()
  r = urllib.request.urlopen('http://localhost:11434/api/generate', d, timeout=10)
  response = json.loads(r.read())
  elapsed = time.time() - start
  print(f'  SUCCESS in {elapsed:.2f}s')
  print(f'  Response: {response["response"][:100]}...')
except Exception as e:
  print(f'  FAILED: {e}')

print()
print('Test 2: Number sequence prediction')
start = time.time()
try:
  context = [1083814273, 378494188, 2479403867, 955863294, 1613448261, 110225632, 1921058495, 508781842, 3753001289, 4271921684]
  prompt = f'Given this sequence of numbers: {context}, what are the next 3 numbers? Return only 3 numbers'
  d = json.dumps({'model':'qwen','prompt':prompt,'stream':False}).encode()
  r = urllib.request.urlopen('http://localhost:11434/api/generate', d, timeout=15)
  txt = json.loads(r.read())['response']
  elapsed = time.time() - start
  nums = [int(x) for x in re.findall(r'-?\d+', txt)][:3]
  print(f'  SUCCESS in {elapsed:.2f}s')
  print(f'  Predicted numbers: {nums}')
  print(f'  Full response: {txt[:200]}...')
except Exception as e:
  print(f'  FAILED: {e}')

print()
print('Test 3: Check model status')
try:
  r = urllib.request.urlopen('http://localhost:11434/api/tags', timeout=2)
  models = json.loads(r.read())
  print('  Available models:')
  for model in models.get('models', []):
    print(f'    - {model["name"]}')
except Exception as e:
  print(f'  FAILED: {e}')
