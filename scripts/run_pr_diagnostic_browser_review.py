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
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from generate_pr_diagnostic_demos import SCENARIOS  # noqa: E402

MOBILE_SCENARIOS = {item[0] for item in SCENARIOS}

INLINE_ASSERTION_DETAILS = (
    "D8 denied operation",
    "D10 final receipt",
    "D10 host-platform boundary",
)


def _empty_report() -> dict[str, object]:
    return {
        "desktop_pages": 0,
        "mobile_pages": 0,
        "artifact_link_clicks": 0,
        "structured_artifacts": 0,
        "structured_artifact_pages": 0,
        "structured_artifact_types": [],
        "readable_views": 0,
        "raw_views": 0,
        "tab_switches": 0,
        "keyboard_tab_switches": 0,
        "copy_actions": 0,
        "exact_raw_copy_checks": 0,
        "formatted_copy_checks": 0,
        "wrap_toggle_actions": 0,
        "raw_pane_local_scroll_checks": 0,
        "raw_panes_with_horizontal_scroll": 0,
        "inline_object_assertions": 0,
        "inline_assertion_details": [],
        "http_200": 0,
        "http_404": 0,
        "unexpected_5xx": 0,
        "console_errors": [],
        "uncaught_exceptions": [],
        "external_requests": [],
        "csp_violations": [],
        "overflow_failures": [],
        "read_audit_records": 0,
        "invalid_audit_lines": 0,
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


def _track_page(page, report: dict[str, object], slug: str, origin: str) -> None:
    page.on(
        "console",
        lambda message: report["console_errors"].append(
            {"scenario": slug, "text": message.text}
        )
        if message.type == "error"
        else None,
    )
    page.on(
        "pageerror",
        lambda error: report["uncaught_exceptions"].append(
            {"scenario": slug, "text": str(error)}
        ),
    )
    page.on(
        "request",
        lambda request: report["external_requests"].append(
            {"scenario": slug, "url": request.url}
        )
        if f"{urllib.parse.urlparse(request.url).scheme}://{urllib.parse.urlparse(request.url).netloc}" != origin
        else None,
    )
    page.on(
        "response",
        lambda response: report.__setitem__(
            "http_404", int(report["http_404"]) + 1
        )
        if response.status == 404
        else report.__setitem__(
            "unexpected_5xx", int(report["unexpected_5xx"]) + 1
        )
        if response.status >= 500
        else None,
    )


def _assert_page_overflow(page, report: dict[str, object], slug: str, viewport: str) -> None:
    dimensions = page.evaluate(
        "() => ({scroll: document.documentElement.scrollWidth, inner: window.innerWidth})"
    )
    if _has_horizontal_overflow(dimensions["scroll"], dimensions["inner"]):
        report["overflow_failures"].append({"scenario": slug, "viewport": viewport})


def _inspect_structured_artifact(
    page,
    *,
    report: dict[str, object],
    slug: str,
    viewport: str,
    seen: set[tuple[str, str]],
) -> None:
    if page.locator('[role="tablist"][aria-label="材料视图"]').count() != 1:
        if not page.locator("pre").is_visible():
            raise RuntimeError(f"non-structured artifact was not rendered inertly: {page.url}")
        return
    artifact_id = page.locator("[data-artifact-viewer]").get_attribute("data-raw")
    artifact_type_text = page.locator(
        "main > details.technical > ul > li"
    ).first.text_content()
    artifact_type = artifact_type_text.split(
        "：" if "：" in artifact_type_text else ":", 1
    )[-1].strip()
    identity = (page.url, viewport)
    if identity not in seen:
        seen.add(identity)
        report["structured_artifact_pages"] += 1
    types = set(report["structured_artifact_types"])
    types.add(artifact_type)
    report["structured_artifact_types"] = sorted(types)
    readable = page.locator("#tab-readable")
    raw_tab = page.locator("#tab-raw")
    if readable.get_attribute("aria-selected") != "true":
        raise RuntimeError("readable view is not the default")
    report["readable_views"] += 1
    raw_tab.click()
    report["tab_switches"] += 1
    report["raw_views"] += 1
    if raw_tab.get_attribute("aria-selected") != "true":
        raise RuntimeError("raw tab did not activate")
    raw_code = page.locator("#raw-code")
    style = raw_code.evaluate(
        "(node) => ({whiteSpace:getComputedStyle(node).whiteSpace,"
        "overflowX:getComputedStyle(node).overflowX,"
        "scrollWidth:node.scrollWidth,clientWidth:node.clientWidth})"
    )
    if style["whiteSpace"] != "pre" or style["overflowX"] not in {"auto", "scroll"}:
        raise RuntimeError("desktop raw view does not preserve lines with local scroll")
    report["raw_pane_local_scroll_checks"] += 1
    if style["scrollWidth"] > style["clientWidth"]:
        report["raw_panes_with_horizontal_scroll"] += 1
    raw_expected = page.evaluate(
        "() => new TextDecoder().decode(Uint8Array.from(atob("
        "document.querySelector('[data-artifact-viewer]').dataset.raw), c => c.charCodeAt(0)))"
    )
    formatted_expected = raw_code.text_content()
    page.locator('[data-copy="raw"]').click()
    page.wait_for_function("() => document.querySelector('[role=status]').textContent.includes('原始')")
    copied_raw = page.evaluate("navigator.clipboard.readText()")
    if copied_raw.replace("\r\n", "\n") != raw_expected.replace("\r\n", "\n"):
        raise RuntimeError("exact raw copy differs from canonical source")
    report["copy_actions"] += 1
    report["exact_raw_copy_checks"] += 1
    page.locator('[data-copy="formatted"]').click()
    page.wait_for_function("() => document.querySelector('[role=status]').textContent.includes('格式化')")
    copied_formatted = page.evaluate("navigator.clipboard.readText()")
    if copied_formatted.replace("\r\n", "\n") != formatted_expected.replace("\r\n", "\n"):
        raise RuntimeError("formatted copy differs from pretty display")
    report["copy_actions"] += 1
    report["formatted_copy_checks"] += 1
    wrap = page.locator("#wrap-raw")
    wrap.check()
    if raw_code.evaluate("(node) => getComputedStyle(node).whiteSpace") != "pre-wrap":
        raise RuntimeError("wrap toggle did not enable wrapping")
    wrap.uncheck()
    if raw_code.evaluate("(node) => getComputedStyle(node).whiteSpace") != "pre":
        raise RuntimeError("wrap toggle did not restore exact line display")
    report["wrap_toggle_actions"] += 2
    raw_tab.press("ArrowLeft")
    report["keyboard_tab_switches"] += 1
    report["tab_switches"] += 1
    if readable.get_attribute("aria-selected") != "true":
        raise RuntimeError("keyboard tab switch failed")
    if artifact_id is None:
        raise RuntimeError("artifact raw identity is missing")
    _assert_page_overflow(page, report, slug, viewport)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / ".agm-work" / "visual_review" / "phase2_1_3_semantic_hardening",
    )
    args = parser.parse_args()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit("Install the optional Playwright package to run Chromium review.") from exc

    args.output.mkdir(parents=True, exist_ok=True)
    report = _empty_report()
    structured_seen: set[tuple[str, str]] = set()
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
                    context.grant_permissions(
                        ["clipboard-read", "clipboard-write"], origin=url.rstrip("/")
                    )
                    page = context.new_page()
                    origin=f"{urllib.parse.urlparse(url).scheme}://{urllib.parse.urlparse(url).netloc}"
                    _track_page(page,report,slug,origin)
                    page.add_init_script(
                        "window.__cspViolations=[];"
                        "document.addEventListener('securitypolicyviolation',"
                        "event=>window.__cspViolations.push(event.violatedDirective));"
                    )
                    response = page.goto(url, wait_until="networkidle")
                    if response is None or response.status != 200:
                        raise RuntimeError(f"page failed: {slug}")
                    report["desktop_pages"] += 1
                    report["http_200"] += 1
                    visible_text = page.locator("main").inner_text()
                    if slug == "D8_system_handled":
                        if (
                            "系统已阻止一次未经授权的操作" not in visible_text
                            or "尝试完成材料验证" not in visible_text
                            or "verify_evidence" in visible_text.split("技术详情", 1)[0]
                        ):
                            raise RuntimeError("D8 denied-operation wording is invalid")
                        report["inline_object_assertions"] += 1
                        report["inline_assertion_details"].append(
                            "D8 denied operation"
                        )
                    if slug == "D10_final_recommendation":
                        if "最终审查建议回执" not in visible_text:
                            raise RuntimeError("D10 final receipt is not visible")
                        report["inline_object_assertions"] += 1
                        report["inline_assertion_details"].append(
                            "D10 final receipt"
                        )
                        if (
                            "未连接代码托管平台" not in visible_text
                            or "未通过本页批准 PR" not in visible_text
                            or "未通过本页合并 PR" not in visible_text
                        ):
                            raise RuntimeError("D10 platform boundary is not visible")
                        report["inline_object_assertions"] += 1
                        report["inline_assertion_details"].append(
                            "D10 host-platform boundary"
                        )
                    _assert_page_overflow(page,report,slug,"desktop")
                    page.screenshot(
                        path=str(args.output / f"{slug}-desktop.png"), full_page=True
                    )
                    hrefs = page.locator('a[href*="/artifacts/"]').evaluate_all(
                        "(items) => [...new Set(items.map((item) => item.getAttribute('href')))]"
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
                        _inspect_structured_artifact(
                            page,report=report,slug=slug,viewport="desktop",
                            seen=structured_seen,
                        )
                        report["csp_violations"].extend(
                            {"scenario":slug,"directive":item}
                            for item in page.evaluate("window.__cspViolations || []")
                        )
                        report["artifact_link_clicks"] += 1
                        report["http_200"] += 1
                        page.go_back(wait_until="domcontentloaded")
                    context.close()

                    if slug in MOBILE_SCENARIOS:
                        mobile = browser.new_context(
                            viewport={"width": 390, "height": 844},
                            device_scale_factor=1,
                            is_mobile=True,
                        )
                        mobile.grant_permissions(
                            ["clipboard-read", "clipboard-write"], origin=url.rstrip("/")
                        )
                        mobile_page = mobile.new_page()
                        _track_page(mobile_page,report,slug,origin)
                        mobile_page.add_init_script(
                            "window.__cspViolations=[];"
                            "document.addEventListener('securitypolicyviolation',"
                            "event=>window.__cspViolations.push(event.violatedDirective));"
                        )
                        mobile_response = mobile_page.goto(url, wait_until="networkidle")
                        if mobile_response is None or mobile_response.status != 200:
                            raise RuntimeError(f"mobile page failed: {slug}")
                        report["http_200"] += 1
                        _assert_page_overflow(mobile_page,report,slug,"390x844")
                        mobile_hrefs = mobile_page.locator('a[href*="/artifacts/"]').evaluate_all(
                            "(items) => [...new Set(items.map((item) => item.getAttribute('href')))]"
                        )
                        for href in mobile_hrefs:
                            response=mobile_page.goto(
                                urllib.parse.urljoin(url,href),wait_until="domcontentloaded"
                            )
                            if response is None or response.status != 200:
                                raise RuntimeError(f"mobile artifact failed: {href}")
                            _inspect_structured_artifact(
                                mobile_page,report=report,slug=slug,
                                viewport="390x844",seen=structured_seen,
                            )
                            report["csp_violations"].extend(
                                {"scenario":slug,"directive":item}
                                for item in mobile_page.evaluate("window.__cspViolations || []")
                            )
                            report["artifact_link_clicks"] += 1
                            report["http_200"] += 1
                            mobile_page.goto(url,wait_until="domcontentloaded")
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
                    expected_reads=len(hrefs)+(len(mobile_hrefs) if slug in MOBILE_SCENARIOS else 0)
                    if audit["records"] != expected_reads:
                        raise RuntimeError(
                            f"tab switches changed read audit identity: {audit['records']} != {expected_reads}"
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
    report["structured_artifacts"] = len(
        {url for url, _viewport in structured_seen}
    )
    (args.output / "browser-review.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf8"
    )
    print(json.dumps(report, ensure_ascii=False))
    return 0 if not (
        report["http_404"]
        or report["unexpected_5xx"]
        or report["console_errors"]
        or report["uncaught_exceptions"]
        or report["external_requests"]
        or report["csp_violations"]
        or report["overflow_failures"]
        or report["invalid_audit_lines"]
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
