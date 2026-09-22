import sys
import random

# Arguments : seed, n_outputs
# La période est fixée à 50 par défaut (modifiable)
PERIOD = 50

if len(sys.argv) < 3:
    sys.exit(1)

seed = int(sys.argv[1])
n = int(sys.argv[2])

# On génère une séquence de base de longueur PERIOD
random.seed(seed)
base = [random.randint(0, 2**32 - 1) for _ in range(PERIOD)]

# On la répète cycliquement
for i in range(n):
    print(base[i % PERIOD])