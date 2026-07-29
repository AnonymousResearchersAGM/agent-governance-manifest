"""Render and click every deterministic PR diagnostic with Chromium."""
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from generate_pr_diagnostic_demos import SCENARIOS  # noqa: E402

MOBILE_SCENARIOS = {
    "D2_high_risk_missing",
    "D3_high_risk_ready",
    "D6A_declaration_conflict",
    "D7_stale_test",
    "D9_contributor_waiting",
}


def _has_horizontal_overflow(scroll_width: int, inner_width: int) -> bool:
    return scroll_width > inner_width


def _stop(proc: subprocess.Popen[str]) -> None:
    if proc.poll() is not None:
        return
    if os.name == "nt":
        proc.send_signal(signal.CTRL_BREAK_EVENT)
    else:
        proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / ".agm-work" / "visual_review" / "phase2_1_3_final",
    )
    args = parser.parse_args()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit("Install the optional Playwright package to run Chromium review.") from exc

    args.output.mkdir(parents=True, exist_ok=True)
    report = {
        "pages": 0,
        "mobile_pages": 0,
        "artifact_clicks": 0,
        "http_200": 0,
        "http_404": 0,
        "console_errors": [],
        "uncaught_exceptions": [],
        "horizontal_overflow": [],
        "read_audit_records": 0,
        "invalid_audit_lines": 0,
    }
    executable = os.environ.get("AGM_CHROMIUM_EXECUTABLE")
    with sync_playwright() as playwright:
        launch = {"headless": True}
        if executable:
            launch["executable_path"] = executable
        browser = playwright.chromium.launch(**launch)
        try:
            for slug, *_ in SCENARIOS:
                before = {
                    path.resolve()
                    for path in Path(tempfile.gettempdir()).glob(
                        "agm-pr-diagnostic-server-*"
                    )
                }
                flags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
                proc = subprocess.Popen(
                    [
                        sys.executable,
                        str(ROOT / "scripts" / "serve_pr_diagnostic_demos.py"),
                        slug,
                    ],
                    cwd=ROOT,
                    stdout=subprocess.PIPE,
                    text=True,
                    creationflags=flags,
                )
                try:
                    assert proc.stdout is not None
                    url = proc.stdout.readline().strip()
                    health = urllib.request.urlopen(
                        urllib.request.urljoin(url, "healthz"), timeout=10
                    )
                    if health.status != 200:
                        raise RuntimeError(f"health check failed: {slug}")
                    context = browser.new_context(viewport={"width": 1280, "height": 900})
                    page = context.new_page()
                    page.on(
                        "console",
                        lambda message, scenario=slug: report["console_errors"].append(
                            {"scenario": scenario, "text": message.text}
                        )
                        if message.type == "error"
                        else None,
                    )
                    page.on(
                        "pageerror",
                        lambda error, scenario=slug: report[
                            "uncaught_exceptions"
                        ].append({"scenario": scenario, "text": str(error)}),
                    )
                    response = page.goto(url, wait_until="networkidle")
                    if response is None or response.status != 200:
                        raise RuntimeError(f"page failed: {slug}")
                    report["pages"] += 1
                    report["http_200"] += 1
                    dimensions = page.evaluate(
                        "() => ({scroll: document.documentElement.scrollWidth, inner: window.innerWidth})"
                    )
                    if _has_horizontal_overflow(
                        dimensions["scroll"], dimensions["inner"]
                    ):
                        report["horizontal_overflow"].append(
                            {"scenario": slug, "viewport": "desktop"}
                        )
                    page.screenshot(
                        path=str(args.output / f"{slug}-desktop.png"), full_page=True
                    )
                    hrefs = page.locator('a[href*="/artifacts/"]').evaluate_all(
                        "(items) => items.map((item) => item.getAttribute('href'))"
                    )
                    for href in hrefs:
                        locator = page.locator(f'a[href="{href}"]').first
                        with page.expect_navigation(wait_until="domcontentloaded") as navigation:
                            locator.click()
                        artifact_response = navigation.value
                        if artifact_response is None or artifact_response.status != 200:
                            report["http_404"] += (
                                artifact_response is not None
                                and artifact_response.status == 404
                            )
                            raise RuntimeError(f"artifact failed: {href}")
                        if not page.locator("pre").is_visible():
                            raise RuntimeError(f"artifact was not rendered inertly: {href}")
                        report["artifact_clicks"] += 1
                        report["http_200"] += 1
                        page.go_back(wait_until="domcontentloaded")
                    context.close()

                    if slug in MOBILE_SCENARIOS:
                        mobile = browser.new_context(
                            viewport={"width": 390, "height": 844},
                            device_scale_factor=1,
                            is_mobile=True,
                        )
                        mobile_page = mobile.new_page()
                        mobile_response = mobile_page.goto(url, wait_until="networkidle")
                        if mobile_response is None or mobile_response.status != 200:
                            raise RuntimeError(f"mobile page failed: {slug}")
                        dimensions = mobile_page.evaluate(
                            "() => ({scroll: document.documentElement.scrollWidth, inner: window.innerWidth})"
                        )
                        if _has_horizontal_overflow(
                            dimensions["scroll"], dimensions["inner"]
                        ):
                            report["horizontal_overflow"].append(
                                {"scenario": slug, "viewport": "390x844"}
                            )
                        mobile_page.screenshot(
                            path=str(args.output / f"{slug}-mobile-390x844.png"),
                            full_page=True,
                        )
                        report["mobile_pages"] += 1
                        mobile.close()
                    audit = json.loads(
                        urllib.request.urlopen(
                            urllib.request.urljoin(url, "audit-summary"), timeout=10
                        ).read()
                    )
                    report["read_audit_records"] += audit["records"]
                    report["invalid_audit_lines"] += audit["invalid"]
                finally:
                    _stop(proc)
                deadline = time.time() + 5
                while time.time() < deadline and (
                    {
                        path.resolve()
                        for path in Path(tempfile.gettempdir()).glob(
                            "agm-pr-diagnostic-server-*"
                        )
                    }
                    - before
                ):
                    time.sleep(0.05)
                if {
                    path.resolve()
                    for path in Path(tempfile.gettempdir()).glob(
                        "agm-pr-diagnostic-server-*"
                    )
                } - before:
                    raise RuntimeError(f"runtime cleanup failed: {slug}")
        finally:
            browser.close()
    (args.output / "browser-review.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf8"
    )
    print(json.dumps(report, ensure_ascii=False))
    return 0 if not (
        report["http_404"]
        or report["console_errors"]
        or report["uncaught_exceptions"]
        or report["horizontal_overflow"]
        or report["invalid_audit_lines"]
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
