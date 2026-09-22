#!/usr/bin/env python3
import sys,re,json,urllib.request
def call_ollama(known_values):
  try:
    prompt=f'I have this sequence of numbers: {known_values}. What are the next 10 numbers in the sequence? Reply with only 10 numbers separated by commas or spaces, nothing else.'
    d=json.dumps({'model':'mistral','prompt':prompt,'stream':False}).encode()
    r=urllib.request.urlopen('http://localhost:11434/api/generate',d,timeout=30)
    response=json.loads(r.read())['response']
    nums=[int(x)for x in re.findall(r'-?\d+',response)][:10]
    return nums if len(nums)==10 else None
  except:
    return None
try:
 f=open(sys.argv[1])
 n=[int(x)for x in re.findall(r'-?\d+',f.read())]
 f.close()
 if not n:exit()
 output=list(n)
 known_idx=10
 while known_idx<len(n):
  known=output[:known_idx]
  preds=call_ollama(known)
  if preds:
   for j in range(min(10,len(n)-known_idx)):
    output[known_idx+j]=preds[j]
  known_idx+=10
 for x in output:print(x)
except:pass
