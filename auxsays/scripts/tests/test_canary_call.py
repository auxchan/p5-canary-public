#!/usr/bin/env python3
"""Synthetic suite: exercises the private call the way a real suite would (P5b proof)."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import call_private  # noqa: E402

PRIVATE_DIR = os.environ.get("PRIVATE_DIR", "")
CONTAIN = os.environ.get("P5B_CONTAIN", "true") == "true"

passed = failed = 0


def check(name, ok):
    global passed, failed
    if ok:
        passed += 1
    else:
        failed += 1
        print(f"FAIL {name}")


r = call_private.contained(PRIVATE_DIR, 7, 20) if CONTAIN else call_private.direct(PRIVATE_DIR, 7)
check("private step returns a status", "status" in r)
check("private step status is ok", r.get("status") == "ok")
print(f"Results: {passed}/{passed + failed} passed, {failed} failed")
sys.exit(0 if failed == 0 else 1)
