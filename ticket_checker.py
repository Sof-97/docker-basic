#!/usr/bin/env python3
import random
import string
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://play-the-future-vfu.up.railway.app/vote"
CHARSET = string.ascii_uppercase  # A-Z only
CODE_LENGTH = 8
TOTAL_CODES = 100
WORKERS = 10
INVALID_MARKER = "ticket non valido"


def random_code():
    return "".join(random.choices(CHARSET, k=CODE_LENGTH))


def check_code(code):
    url = f"{BASE_URL}/{code}"
    try:
        r = requests.get(url, timeout=10)
        body = r.text.lower()
        if INVALID_MARKER not in body:
            return url, r.status_code, r.text[:200]
    except requests.RequestException as e:
        print(f"[ERR] {code}: {e}")
    return None


def main():
    codes = [random_code() for _ in range(TOTAL_CODES)]
    valid = []

    print(f"Testing {TOTAL_CODES} random {CODE_LENGTH}-char codes against {BASE_URL}\n")

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(check_code, code): code for code in codes}
        for i, future in enumerate(as_completed(futures), 1):
            code = futures[future]
            result = future.result()
            status = "VALID" if result else "."
            print(f"[{i:3}/{TOTAL_CODES}] {code}  {status}", end="\r" if not result else "\n")
            if result:
                valid.append(result)

    print(f"\n\nRisultati: {len(valid)} ticket validi trovati su {TOTAL_CODES} testati")
    if valid:
        print("\n--- Ticket validi ---")
        for url, status_code, preview in valid:
            print(f"  URL     : {url}")
            print(f"  Status  : {status_code}")
            print(f"  Preview : {preview!r}")
            print()

    return valid


if __name__ == "__main__":
    main()
