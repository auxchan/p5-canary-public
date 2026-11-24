#!/usr/bin/env python3
"""Public caller of the private (synthetic) module, for the P5b boundary proof.

--direct   imports the module in-process (Option A as specified: no containment).
--contain  runs it in a child process whose stdout and stderr are discarded; only a fixed status
           and a value from a closed set cross back. Timeout and kill map to fixed statuses.
Writes {"status": ..., "verdict": ...} to --out. Exit 0 when status is ok, 3 otherwise.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

ALLOWED = {"HOLD", "PASS"}
CHILD = (
    "import json,sys\n"
    "sys.path.insert(0, sys.argv[1])\n"
    "import p5b_canary as m\n"
    "v = m.decide(int(sys.argv[3]))\n"
    "open(sys.argv[2], 'w').write(json.dumps({'verdict': v}))\n"
)


def contained(private_dir, n, timeout):
    fd, res = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    try:
        proc = subprocess.run([sys.executable, "-c", CHILD, private_dir, res, str(n)],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                              stdin=subprocess.DEVNULL, timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "verdict": "NOT_ESTABLISHED"}
    try:
        if proc.returncode < 0:
            return {"status": "killed", "verdict": "NOT_ESTABLISHED"}
        if proc.returncode != 0:
            return {"status": "failed", "verdict": "NOT_ESTABLISHED"}
        try:
            v = json.load(open(res)).get("verdict")
        except Exception:
            v = None
        if v not in ALLOWED:
            return {"status": "bad_output", "verdict": "NOT_ESTABLISHED"}
        return {"status": "ok", "verdict": v}
    finally:
        os.unlink(res)


def direct(private_dir, n):
    sys.path.insert(0, private_dir)
    import p5b_canary as m  # noqa: E402
    return {"status": "ok", "verdict": m.decide(n)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--private-dir", required=True)
    ap.add_argument("--n", type=int, default=7)
    ap.add_argument("--out", default=None)
    ap.add_argument("--timeout", type=int, default=20)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--contain", action="store_true")
    g.add_argument("--direct", action="store_true")
    a = ap.parse_args()
    r = contained(a.private_dir, a.n, a.timeout) if a.contain else direct(a.private_dir, a.n)
    if a.out:
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        with open(a.out, "w") as f:
            json.dump(r, f, sort_keys=True)
            f.write("\n")
    print(f"private step: status={r['status']} verdict={r['verdict']}")
    return 0 if r["status"] == "ok" else 3


if __name__ == "__main__":
    raise SystemExit(main())
