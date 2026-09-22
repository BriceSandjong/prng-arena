import sys
import traceback


def main():
    try:
        from z3 import BitVec, BitVecVal, Solver, sat, LShR, If

        if len(sys.argv) < 2: return
        with open(sys.argv[1], 'r') as f:
            nombres = [int(x.strip()) for x in f if x.strip().isdigit()]

        if len(nombres) < 10:
            for _ in range(len(nombres)): print(0, flush=True)
            return

        # On prend 5 observations (largement suffisant pour 32 bits)
        obs = nombres[:5]

        # --- Modèle 1 : LFSR Galois (Décalage à DROITE, 32 sauts par nombre) ---
        s_right = Solver()
        taps_r = BitVec('taps', 32)
        state_r = BitVec('state', 32)

        curr_r = state_r
        for val in obs:
            s_right.add(curr_r == val)
            for _ in range(32):
                bit = curr_r & 1
                curr_r = LShR(curr_r, 1) ^ If(bit == 1, taps_r, BitVecVal(0, 32))

        if s_right.check() == sat:
            m = s_right.model()
            cur_state = m[state_r].as_long()
            cur_taps = m[taps_r].as_long()

            for i in range(len(nombres)):
                if i < 5:
                    print(0, flush=True)
                else:
                    print(cur_state, flush=True)

                # Génération Python pour la prédiction
                for _ in range(32):
                    bit = cur_state & 1
                    mask = cur_taps if bit == 1 else 0
                    cur_state = ((cur_state >> 1) ^ mask) & 0xFFFFFFFF
            return

        # --- Modèle 2 : LFSR Galois (Décalage à GAUCHE, 32 sauts par nombre) ---
        s_left = Solver()
        taps_l = BitVec('taps', 32)
        state_l = BitVec('state', 32)

        curr_l = state_l
        for val in obs:
            s_left.add(curr_l == val)
            for _ in range(32):
                bit = LShR(curr_l, 31)
                curr_l = (curr_l << 1) ^ If(bit == 1, taps_l, BitVecVal(0, 32))

        if s_left.check() == sat:
            m = s_left.model()
            cur_state = m[state_l].as_long()
            cur_taps = m[taps_l].as_long()

            for i in range(len(nombres)):
                if i < 5:
                    print(0, flush=True)
                else:
                    print(cur_state, flush=True)

                for _ in range(32):
                    bit = (cur_state >> 31) & 1
                    mask = cur_taps if bit == 1 else 0
                    cur_state = ((cur_state << 1) ^ mask) & 0xFFFFFFFF
            return

        # Si l'algorithme est encore différent (improbable), on sort des 0
        for _ in range(len(nombres)): print(0, flush=True)

    except Exception:
        with open("mouchard_lfsr_z3.txt", "w") as f:
            f.write(traceback.format_exc())


if __name__ == '__main__':
    main()