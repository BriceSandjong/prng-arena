import sys
import random
import re
import os
from z3 import Solver, BitVec, LShR, sat


def untemper_z3(value):
    y = BitVec('y', 32)
    y1 = y ^ LShR(y, 11)
    y2 = y1 ^ ((y1 << 7) & 0x9d2c5680)
    y3 = y2 ^ ((y2 << 15) & 0xefc60000)
    y4 = y3 ^ LShR(y3, 18)
    s = Solver()
    s.add(y4 == value)
    return s.model()[y].as_long() if s.check() == sat else 0


def main():
    state = []

    # 1. On récupère les données (soit du fichier argument, soit du flux)
    arg = " ".join(sys.argv[1:]).replace('"', '').strip()
    if arg and os.path.isfile(arg):
        with open(arg, 'r', encoding='utf-8-sig') as f:  # utf-8-sig gère les symboles bizarres 'ÿþ'
            raw = f.read()
    else:
        raw = sys.stdin.read()

    # 2. On extrait tous les nombres (nettoie les ;; et les espaces)
    nombres = [int(n) for n in re.findall(r'\d+', raw)]

    # 3. On répond au Launcher nombre par nombre
    for val in nombres:
        if len(state) < 624:
            # Phase d'apprentissage
            state.append(untemper_z3(val))
            sys.stdout.write("0\n")  # On répond 0 pour dire qu'on apprend
        else:
            if len(state) == 624:
                # Synchronisation du moteur Python (ton astuce !)
                random.setstate((3, tuple(state + [624]), None))
                state.append("SYNC_DONE")

            # Phase de prédiction réelle
            prediction = random.getrandbits(32)
            sys.stdout.write(f"{prediction}\n")

        # On force l'envoi pour que le Launcher ne bloque pas
        sys.stdout.flush()


if __name__ == "__main__":
    main()