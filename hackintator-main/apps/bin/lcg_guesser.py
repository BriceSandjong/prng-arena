import sys
import re
import os
import math

# --- Fonctions mathématiques pour l'inversion modulaire ---

def egcd(a, b):
    """Algorithme d'Euclide étendu"""
    if a == 0:
        return (b, 0, 1)
    g, y, x = egcd(b % a, a)
    return (g, x - (b // a) * y, y)

def modinv(a, m):
    """Inverse modulaire de a modulo m"""
    g, x, y = egcd(a, m)
    if g != 1:
        return None  # L'inverse n'existe pas
    return x % m

# --- Algorithme principal ---

def main():
    # 1. Récupération des données (via fichier ou stdin)
    arg = " ".join(sys.argv[1:]).replace('"', '').strip()
    if arg and os.path.isfile(arg):
        with open(arg, 'r', encoding='utf-8-sig') as f:
            raw = f.read()
    else:
        raw = sys.stdin.read()

    nombres = [int(n) for n in re.findall(r'-?\d+', raw)]

    # Variables d'état
    history = []
    m = None
    a = None
    c = None

    for val in nombres:
        history.append(val)
        
        # Si on a déjà cracké les paramètres de ce LCG
        if m is not None and a is not None and c is not None:
            # Phase de prédiction réelle
            prediction = (a * history[-2] + c) % m
            sys.stdout.write(f"{prediction}\n")
            sys.stdout.flush()
            continue

        # Sinon, on est en apprentissage : on accumule et on répond 0
        sys.stdout.write("0\n")
        sys.stdout.flush()

        # Tentative de cassage dès qu'on a au moins 6 nombres
        if len(history) >= 6 and m is None:
            # Étape 1 : Différences entre nombres successifs pour annuler 'c'
            t = [history[i+1] - history[i] for i in range(len(history)-1)]
            
            # Étape 2 : Déterminants pour isoler des multiples de 'm'
            u = [abs(t[i+2] * t[i] - t[i+1]**2) for i in range(len(t)-2)]
            
            # Étape 3 : 'm' est un diviseur du PGCD de toutes ces valeurs 'u'
            m_est = 0
            for ui in u:
                m_est = math.gcd(m_est, ui)
            
            if m_est > 1:
                # Étape 4 : Retrouver 'a'
                # a = t_{i+1} * inverse(t_i) modulo m
                for i in range(len(t)-1):
                    inv = modinv(t[i] % m_est, m_est)
                    if inv is not None:
                        a_est = (t[i+1] * inv) % m_est
                        
                        # Étape 5 : Retrouver 'c'
                        # c = x_1 - a * x_0 modulo m
                        c_est = (history[i+1] - a_est * history[i]) % m_est
                        
                        # Étape 6 : Validation stricte sur tout l'historique
                        valid = True
                        for j in range(len(history)-1):
                            if (a_est * history[j] + c_est) % m_est != history[j+1]:
                                valid = False
                                break
                        
                        if valid:
                            # Paramètres trouvés ! On fige l'apprentissage.
                            m = m_est
                            a = a_est
                            c = c_est
                            break

if __name__ == "__main__":
    main()