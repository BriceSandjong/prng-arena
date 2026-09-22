import sys


def main():
    # Lecture des arguments : seed (ag[0]) et itérations (ag[1])
    # Par défaut : seed 0xACE1, n=1000
    try:
        seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0xACE1
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    except (ValueError, IndexError):
        seed, n = 0xACE1, 1000

    # L'état ne doit jamais être 0
    state = seed if seed != 0 else 0xACE1

    # Polynôme de Galois 32 bits : x^32 + x^22 + x^2 + x^1 + 1
    # Masque correspondant : 0x80000057
    mask = 0x80000057

    for _ in range(n):
        # On effectue 32 décalages pour sortir un nombre de 32 bits complet
        for _ in range(32):
            lsb = state & 1
            state >>= 1
            if lsb:
                state ^= mask

        # Sortie brute avec flush pour éviter les deadlocks
        sys.stdout.write(f"{state & 0xFFFFFFFF}\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()