"""Check the frozen SHA-256 list for PR-native diagnostic demos."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def check_hashes(output: Path = ROOT / "examples" / "pr_native_diagnostic" / "outputs") -> list[str]:
    expected = json.loads((output / "expected_sha256.json").read_text(encoding="utf-8")); errors = []
    for relative, digest in expected.items():
        path = output / relative
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "missing"
        if actual != digest: errors.append(f"{relative}: expected {digest}, got {actual}")
    return errors

if __name__ == "__main__":
    failures = check_hashes()
    if failures: raise SystemExit("\n".join(failures))
    print("PR diagnostic demo hashes match")
