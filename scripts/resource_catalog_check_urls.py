#!/usr/bin/env python3
"""List every URL in shared/fixtures/resources.json that does not return a success status.

Usage (from the repo root):
    python scripts/resource_catalog_check_urls.py
    python scripts/resource_catalog_check_urls.py --file shared/fixtures/resources.json --timeout 15

Exit code is 1 if any URL fails, so it can also run in CI. This only checks that a
URL answers; a person still has to open each one and confirm it is the right resource.
"""
import argparse
import json
import sys
import urllib.error
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Delphi resource checker)"}


def status_of(url: str, timeout: float) -> tuple[bool, str]:
    """Try HEAD first, then GET (some sites reject HEAD). Redirects are followed."""
    last = "unknown error"
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers=UA)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if 200 <= resp.status < 300:
                    return True, str(resp.status)
                last = f"HTTP {resp.status}"
        except urllib.error.HTTPError as exc:
            last = f"HTTP {exc.code}"
        except (urllib.error.URLError, OSError, ValueError) as exc:
            last = f"{type(exc).__name__}: {exc}"
    return False, last


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default="shared/fixtures/resources.json")
    ap.add_argument("--timeout", type=float, default=10)
    args = ap.parse_args()

    with open(args.file, encoding="utf-8") as f:
        resources = json.load(f)

    bad = 0
    for r in resources:
        ok, info = status_of(r["url"], args.timeout)
        if not ok:
            bad += 1
            print(f"BAD  {r.get('id')}  {r['url']}  ({info})")
    print(f"\n{len(resources) - bad} of {len(resources)} URLs OK, {bad} failing.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
