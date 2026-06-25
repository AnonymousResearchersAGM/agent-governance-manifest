"""CLI wrapper for maintainer-facing AGM review packet generation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agm.governance import AGMError, generate_review_packet, load_governance_config  # noqa: E402


def generate_packet(package_path: Path | str, output_dir: Path | str = ROOT / "review_packets") -> dict[str, Path]:
    return generate_review_packet(Path(package_path), Path(output_dir), load_governance_config(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate AGM review_packet.json and review_packet.md.")
    parser.add_argument("evidence_package", help="Path to an evidence package YAML file.")
    parser.add_argument("--output-dir", default=str(ROOT / "review_packets"), help="Directory for generated packet files.")
    args = parser.parse_args()

    try:
        outputs = generate_packet(args.evidence_package, args.output_dir)
    except AGMError as exc:
        print(json.dumps({"error": str(exc)}, indent=2))
        return 2
    print(json.dumps({key: str(value) for key, value in outputs.items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
