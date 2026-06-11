from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
api_src = ROOT / "apps/api/src"
if not api_src.exists():
    print("Missing apps/api/src")
    sys.exit(1)
 
print("API layout validation passed.")
