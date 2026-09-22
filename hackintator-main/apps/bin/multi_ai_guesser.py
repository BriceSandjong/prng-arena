from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

MOD32 = 2 ** 32
GAMMA32 = 0x9E3779B9


def parse_numbers(text: str) -> list[int]:
    return [int(x) for x in re.findall(r"-?\d+", text)]


def xorshift32_next(value: int) -> int:
    value &= 0xFFFFFFFF
    value ^= (value << 13) & 0xFFFFFFFF
    value ^= (value >> 17) & 0xFFFFFFFF
    value ^= (value << 5) & 0xFFFFFFFF
    return value & 0xFFFFFFFF


def mix32(value: int) -> int:
    value &= 0xFFFFFFFF
    value = (value ^ (value >> 16)) * 0x85EBCA6B & 0xFFFFFFFF
    value = (value ^ (value >> 13)) * 0xC2B2AE35 & 0xFFFFFFFF
    value ^= value >> 16
    return value & 0xFFFFFFFF


def rotr32(value: int, rot: int) -> int:
    value &= 0xFFFFFFFF
    rot &= 31
    return ((value >> rot) | (value << ((-rot) & 31))) & 0xFFFFFFFF


def pcg32_output(state: int) -> int:
    xorshifted = (((state >> 18) ^ state) >> 27) & 0xFFFFFFFF
    rot = (state >> 59) & 31
    return rotr32(xorshifted, rot)


def load_state(path: Path) -> dict:
    if not path.exists():
        return {"version": 1, "transition": {}, "runs": 0}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"version": 1, "transition": {}, "runs": 0}


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def detect_lcg(series: list[int]) -> tuple[int, int] | None:
    if len(series) < 6:
        return None

    # Estimate parameters from the first three values only and validate over the full prefix.
    x0, x1, x2 = series[0], series[1], series[2]
    delta = (x1 - x0) % MOD32
    if delta == 0 or delta % 2 == 0:
        return None

    try:
        inv_delta = pow(delta, -1, MOD32)
    except ValueError:
        return None

    a = ((x2 - x1) * inv_delta) % MOD32
    c = (x1 - a * x0) % MOD32

    # Require consistency for almost the entire context to avoid false positives.
    checks = 0
    for j in range(0, len(series) - 1):
        checks += 1
        if (a * series[j] + c) % MOD32 != series[j + 1]:
            return None

    if checks < 5:
        return None

    return int(a), int(c)


def detect_xorshift32(series: list[int]) -> bool:
    if len(series) < 3:
        return False

    for i in range(min(len(series) - 1, 20)):
        if xorshift32_next(series[i]) != series[i + 1]:
            return False
    return True


def detect_splitmix32(series: list[int], search_limit: int = 200000) -> int | None:
    if len(series) < 3:
        return None

    target = series[0] & 0xFFFFFFFF
    for state in range(search_limit):
        if mix32(state + GAMMA32) == target:
            s = state & 0xFFFFFFFF
            ok = True
            for index in range(min(len(series), 16)):
                s = (s + GAMMA32) & 0xFFFFFFFF
                if mix32(s) != (series[index] & 0xFFFFFFFF):
                    ok = False
                    break
            if ok:
                return state & 0xFFFFFFFF
    return None


def detect_pcg32(series: list[int], search_limit: int = 200000) -> int | None:
    if len(series) < 3:
        return None

    target = series[0] & 0xFFFFFFFF
    for seed in range(search_limit):
        state = (seed + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
        state = (state * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
        if pcg32_output(state) != target:
            continue

        ok = True
        tmp = state
        for index in range(1, min(len(series), 12)):
            tmp = (tmp * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
            if pcg32_output(tmp) != (series[index] & 0xFFFFFFFF):
                ok = False
                break
        if ok:
            return seed
    return None


def learn_transition_model(state: dict, series: list[int], order: int = 3) -> None:
    model = state.setdefault("transition", {})
    for i in range(len(series) - order):
        key = ",".join(str(v) for v in series[i : i + order])
        next_value = str(series[i + order])
        bucket = model.setdefault(key, {})
        bucket[next_value] = int(bucket.get(next_value, 0)) + 1


def predict_from_transition(prefix: list[int], total_len: int, state: dict, order: int = 3) -> list[int]:
    out = prefix[:]
    model = state.get("transition", {})

    while len(out) < total_len:
        if len(out) < order:
            out.append(out[-1] if out else 0)
            continue

        key = ",".join(str(v) for v in out[-order:])
        bucket = model.get(key)
        if bucket:
            next_value = int(max(bucket.items(), key=lambda item: item[1])[0])
            out.append(next_value)
        else:
            # fallback: continue with last delta
            if len(out) >= 2:
                delta = (out[-1] - out[-2]) % MOD32
                out.append((out[-1] + delta) % MOD32)
            else:
                out.append(out[-1])

    return out


def predict_series(series: list[int], state: dict, context_size: int) -> tuple[list[int], str]:
    if not series:
        return [], "unknown"

    prefix_len = max(1, min(context_size, len(series)))
    prefix = series[:prefix_len]

    if detect_xorshift32(prefix):
        out = prefix[:]
        while len(out) < len(series):
            out.append(xorshift32_next(out[-1]))
        return out, "xorshift32"

    splitmix_seed = detect_splitmix32(prefix)
    if splitmix_seed is not None:
        out = []
        s = splitmix_seed
        for _ in range(len(series)):
            s = (s + GAMMA32) & 0xFFFFFFFF
            out.append(mix32(s))
        return out, "splitmix32"

    pcg_seed = detect_pcg32(prefix)
    if pcg_seed is not None:
        out = []
        st = (pcg_seed + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
        for _ in range(len(series)):
            st = (st * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
            out.append(pcg32_output(st))
        return out, "pcg32"

    lcg = detect_lcg(prefix)
    if lcg is not None:
        a, c = lcg
        out = prefix[:]
        while len(out) < len(series):
            out.append((a * out[-1] + c) % MOD32)
        return out, "lcg"

    return predict_from_transition(prefix, len(series), state), "transition"


def main() -> int:
    parser = argparse.ArgumentParser(description="Adaptive multi-generator guesser")
    parser.add_argument("input_file")
    parser.add_argument("--context-size", type=int, default=32)
    parser.add_argument("--state-file", default="apps/bin/multi_ai_state.json")
    args, unknown = parser.parse_known_args()

    # tolerate unquoted paths with spaces
    input_text = args.input_file
    if unknown:
        input_text = " ".join([input_text, *unknown]).strip()

    input_path = Path(input_text)
    if not input_path.exists():
        return 1

    series = parse_numbers(input_path.read_text(encoding="utf-8", errors="ignore"))
    if not series:
        return 0

    state_path = Path(args.state_file)
    state = load_state(state_path)

    prediction, family = predict_series(series, state, args.context_size)

    # Learn only after predicting to avoid training on the same evaluation sequence.
    learn_transition_model(state, series)

    state["runs"] = int(state.get("runs", 0)) + 1
    state["last_family"] = family
    save_state(state_path, state)

    for value in prediction:
        print(value)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
