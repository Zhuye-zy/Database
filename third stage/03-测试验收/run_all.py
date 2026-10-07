#!/usr/bin/env python3
"""Run C tests on an existing baseline DB; failures stop with nonzero exit."""
from pathlib import Path
import subprocess,sys
HERE=Path(__file__).resolve().parent
for name in ['smoke_test.py','fk_violation_test.py','complex_boundary_test.py','frontend_test.py']:
    result=subprocess.run([sys.executable,str(HERE/name)])
    if result.returncode:raise SystemExit(result.returncode)
print('C acceptance PASS; for fresh deploy/dump/restore use 06-运行管理/verify_fresh.py')
