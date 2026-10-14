"""Check the registers of model/. Prints every problem and ends with 'Problems found: N'.

Usage: python tools/check.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pfmmap.model import Model  # noqa: E402
from pfmmap.validate import check  # noqa: E402


def main():
    m = Model()
    problems, warnings = check(m)
    for w in warnings:
        print("warning:", w)
    for p in problems:
        print("problem:", p)
    counts = {k: len(v) for k, v in m.t.items()}
    print("Rows:", ", ".join(f"{k} {v}" for k, v in counts.items()))
    print(f"Problems found: {len(problems)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
