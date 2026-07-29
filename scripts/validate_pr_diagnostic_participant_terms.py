"""Fail when internal implementation terms leak into the participant layer."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "examples" / "pr_native_diagnostic" / "outputs"
FORBIDDEN = (
    "governance",
    "治理状态",
    "obligation",
    "canonical",
    "transition",
    "attestation",
    "fingerprint",
    "digest",
    "actor",
    "compiler",
    "finding",
    "supervision",
    "delegation scope",
)


class _VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def main() -> int:
    failures: list[str] = []
    pages = sorted(OUTPUT.glob("D*/report.html"))
    for page in pages:
        parser = _VisibleText()
        parser.feed(page.read_text(encoding="utf8").split("<details>", 1)[0])
        visible = " ".join(parser.parts).lower()
        for term in FORBIDDEN:
            if term.lower() in visible:
                failures.append(f"{page.relative_to(ROOT)}: {term}")
    if failures:
        raise SystemExit("\n".join(failures))
    print(f"Participant-facing term scan passed for {len(pages)} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
