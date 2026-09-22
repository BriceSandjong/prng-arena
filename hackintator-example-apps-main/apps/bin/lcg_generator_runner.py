import os
import sys

arg1 = sys.argv[1]
arg2 = sys.argv[2]
arg3 = sys.argv[3]
arg4 = sys.argv[4]
arg5 = int(sys.argv[5])

print(arg4)

for i in range(0, arg5):
  arg4 = os.popen(f"./apps/bin/lcg_generator/output/main {arg1} {arg2} {arg3} {arg4}").read()
  print(arg4, end='')

