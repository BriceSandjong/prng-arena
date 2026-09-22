import sys
import re
import os


def find_period(values):
    """Cherche la plus petite période p sur un buffer de taille fixe."""
    size = len(values)
    if size < 2:
        return size
    for p in range(1, size // 2 + 1):
        if all(values[j] == values[j + p] for j in range(size - p)):
            return p
    return size


def main():
    # 1. Récupération des données
    arg = " ".join(sys.argv[1:]).replace('"', '').strip()
    if arg and os.path.isfile(arg):
        with open(arg, 'r', encoding='utf-8-sig') as f:
            raw = f.read()
    else:
        raw = sys.stdin.read()

    nombres = [n for n in re.findall(r'\d+', raw)]

    # Phase 1 : détection sur un buffer borné (pas toute la séquence en RAM)
    # LEARNING_WINDOW doit être >= 2 * période_max_attendue
    LEARNING_WINDOW = 1000

    learning_buf = []
    known_period = None
    cycle = None      # tableau de longueur `known_period` seulement
    position = 0      # curseur dans le cycle

    for val in nombres:

        if known_period is None:
            # APPRENTISSAGE : on accumule jusqu'à détecter la période
            learning_buf.append(val)

            if len(learning_buf) >= 4:
                p = find_period(learning_buf)
                if p < len(learning_buf) and len(learning_buf) >= 2 * p:
                    known_period = p
                    cycle = learning_buf[:p]  # on ne garde que p valeurs !
                    # Calcul de la position courante dans le cycle
                    position = len(learning_buf) % known_period
                    learning_buf = None       # libère le buffer d'apprentissage

            sys.stdout.write("0\n")

        else:
            # PRÉDICTION : O(1) par valeur, O(p) mémoire totale
            prediction = cycle[position % known_period]
            sys.stdout.write(f"{prediction}\n")
            position += 1

        sys.stdout.flush()


if __name__ == "__main__":
    main()