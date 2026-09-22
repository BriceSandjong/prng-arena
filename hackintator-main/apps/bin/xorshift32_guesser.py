import sys
import re
import os

# --- L'algorithme exact du générateur ---
def next_xorshift32(value):
    value &= 0xFFFFFFFF
    value ^= (value << 13) & 0xFFFFFFFF
    value ^= (value >> 17) & 0xFFFFFFFF
    value ^= (value << 5) & 0xFFFFFFFF
    return value & 0xFFFFFFFF

def main():
    # 1. Récupération des données (via fichier ou stdin, comme tes autres guessers)
    arg = " ".join(sys.argv[1:]).replace('"', '').strip()
    if arg and os.path.isfile(arg):
        with open(arg, 'r', encoding='utf-8-sig') as f:
            raw = f.read()
    else:
        raw = sys.stdin.read()

    nombres = [int(n) for n in re.findall(r'\d+', raw)]

    # 2. Xorshift32 ne nécessite qu'un seul nombre pour cloner l'état
    # puisque la sortie EST l'état interne.
    current_state = None

    for val in nombres:
        if current_state is None:
            # Phase d'apprentissage
            current_state = val
            sys.stdout.write("0\n")  # Réponse 0 exigée par ton Launcher
        else:
            # Phase de prédiction : on simule l'étape suivante à partir de notre état
            current_state = next_xorshift32(current_state)
            sys.stdout.write(f"{current_state}\n")
            
        sys.stdout.flush()

if __name__ == "__main__":
    main()