import sys
import re
import os
import math
import sympy


def recover_n(values):
    """
    Retrouve n = p*q depuis les outputs sans connaître le générateur.

    Principe :
      x_{i+1} = x_i² mod n  →  x_i² - x_{i+1} ≡ 0 mod n
      Donc n | gcd(x1²-x2, x2²-x3).

    Le gcd peut retourner un multiple de n : on factorise le candidat
    et on vérifie quel produit de deux facteurs premiers est cohérent
    avec la séquence observée.
    """
    candidates = set()
    for i in range(min(10, len(values) - 3)):
        x0, x1, x2, x3 = values[i], values[i+1], values[i+2], values[i+3]
        a = x1*x1 - x2
        b = x2*x2 - x3
        if a == 0 or b == 0:
            continue
        g = math.gcd(abs(a), abs(b))
        if g > 1:
            candidates.add(g)

    for c in sorted(candidates):
        factors = list(sympy.factorint(c).keys())
        for i in range(len(factors)):
            for j in range(i, len(factors)):
                n_cand = factors[i] * factors[j]
                if n_cand > 1 and (values[0] * values[0]) % n_cand == values[1]:
                    return n_cand
    return None


def main():
    # 1. Récupération des données
    arg = " ".join(sys.argv[1:]).replace('"', '').strip()
    if arg and os.path.isfile(arg):
        with open(arg, 'r', encoding='utf-8-sig') as f:
            raw = f.read()
    else:
        raw = sys.stdin.read()

    nombres = [int(n) for n in re.findall(r'\d+', raw)]

    # 2. Boucle de traitement
    #
    # Phase 1 — apprentissage (20 valeurs) :
    #   On accumule assez de valeurs pour que recover_n soit robuste,
    #   puis on factorise le candidat gcd pour retrouver n exactement.
    #
    # Phase 2 — prédiction O(1) :
    #   x_next = x_current² mod n
    #
    LEARNING = 20

    buf = []
    n = None
    x_current = None

    for val in nombres:

        if n is None:
            buf.append(val)
            sys.stdout.write("0\n")

            if len(buf) >= LEARNING:
                n = recover_n(buf)
                if n:
                    x_current = buf[-1]

        else:
            x_current = (x_current * x_current) % n
            sys.stdout.write(f"{x_current}\n")

        sys.stdout.flush()


if __name__ == "__main__":
    main()