#!/usr/bin/env python3
"""Synthetic writeback validator: re-derives the verdict through the private step and compares it
with the staged output file, the way a real validator re-runs QA over generated records."""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import call_private  # noqa: E402

d = os.environ.get("PRIVATE_DIR", "")
r = call_private.contained(d, 7, 20) if os.environ.get("P5B_CONTAIN", "true") == "true" else call_private.direct(d, 7)
p = Path("auxsays/updates/generated/verdict.json")
out = json.loads(p.read_text()) if p.exists() else None
if r != out:
    print(f"validate_output: mismatch (status={r.get('status')})")
    sys.exit(1)
print("validate_output: ok")
