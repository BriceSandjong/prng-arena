import sys
import random

if len(sys.argv) != 3:
    sys.exit(1)

random.seed(int(sys.argv[1]))
for _ in range(int(sys.argv[2])):
    print(random.getrandbits(32))
