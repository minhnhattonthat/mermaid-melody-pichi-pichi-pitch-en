"""One-command check (pre-commit hook runs this): codec selftest, identity build, graphics lint.
    python -X utf8 tools/check.py
"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = [sys.executable, "-X", "utf8"]
STEPS = [
    ["tools/mmcomp.py", "--selftest"],
]
if os.path.exists(os.path.join(ROOT, "tools", "build.py")):
    STEPS.append(["tools/build.py", "check"])

fail = 0
for s in STEPS:
    r = subprocess.run(PY + s, cwd=ROOT)
    if r.returncode:
        print("FAIL:", " ".join(s)); fail = 1
sys.exit(fail)
