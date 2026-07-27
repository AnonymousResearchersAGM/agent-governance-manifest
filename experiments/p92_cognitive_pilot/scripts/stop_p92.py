"""Stop only processes carrying the active P92 session marker."""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import signal
import subprocess
import time
from pathlib import Path
from typing import Any

from common import package_root


def _command_line(pid: int) -> str:
    proc = Path("/proc") / str(pid) / "cmdline"
    if proc.exists():
        return proc.read_bytes().replace(b"\x00", b" ").decode(
            "utf-8", errors="replace"
        )
    if os.name == "nt":
        command = (
            "(Get-CimInstance Win32_Process -Filter "
            f"'ProcessId = {pid}' -ErrorAction SilentlyContinue).CommandLine"
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        return result.stdout.strip()
    return ""


def _process_table() -> dict[int, dict[str, Any]]:
    if os.name == "nt":
        command = (
            "Get-CimInstance Win32_Process | "
            "Select-Object ProcessId,ParentProcessId,CommandLine | "
            "ConvertTo-Json -Compress"
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(
                "Unable to enumerate Windows processes for P92 cleanup."
            )
        raw = json.loads(result.stdout or "[]")
        rows = raw if isinstance(raw, list) else [raw]
        return {
            int(row["ProcessId"]): {
                "parent_pid": int(row.get("ParentProcessId") or 0),
                "command_line": str(row.get("CommandLine") or ""),
            }
            for row in rows
            if row and row.get("ProcessId") is not None
        }

    table: dict[int, dict[str, Any]] = {}
    proc_root = Path("/proc")
    if not proc_root.exists():
        return table
    for entry in proc_root.iterdir():
        if not entry.name.isdigit():
            continue
        try:
            command_line = (entry / "cmdline").read_bytes().replace(
                b"\x00", b" "
            ).decode("utf-8", errors="replace")
            stat = (entry / "stat").read_text(
                encoding="utf-8", errors="replace"
            )
            parent_pid = int(stat.rsplit(")", 1)[1].split()[1])
        except (FileNotFoundError, PermissionError, IndexError, ValueError):
            continue
        table[int(entry.name)] = {
            "parent_pid": parent_pid,
            "command_line": command_line,
        }
    return table


def _matching_process_ids(marker: str) -> set[int]:
    return {
        pid
        for pid, item in _process_table().items()
        if marker in item["command_line"]
    }


def _alive(pid: int) -> bool:
    if os.name == "nt":
        process_query_limited_information = 0x1000
        still_active = 259
        handle = ctypes.windll.kernel32.OpenProcess(
            process_query_limited_information,
            False,
            pid,
        )
        if not handle:
            return False
        try:
            exit_code = ctypes.c_ulong()
            if not ctypes.windll.kernel32.GetExitCodeProcess(
                handle, ctypes.byref(exit_code)
            ):
                return False
            return exit_code.value == still_active
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def stop_marked_processes(root: Path | None = None) -> dict[str, Any]:
    base = (root or package_root()).resolve()
    process_file = base / "runtime" / "processes.json"
    if not process_file.exists():
        return {"stopped": [], "skipped": [], "process_file": None}
    payload = json.loads(process_file.read_text(encoding="utf-8"))
    marker = str(payload.get("session_marker", ""))
    if not marker:
        raise RuntimeError("P92 process marker is missing.")
    table = _process_table()
    recorded: set[int] = set()
    skipped = []
    for item in payload.get("processes", []):
        pid = int(item["pid"])
        recorded.add(pid)
        if not _alive(pid):
            continue
        command_line = str(
            table.get(pid, {}).get("command_line") or _command_line(pid)
        )
        if marker not in command_line:
            skipped.append(
                {"pid": pid, "reason": "session marker not found"}
            )
    candidates = {
        pid
        for pid, item in table.items()
        if marker in item["command_line"]
    }
    candidates.update(
        pid
        for pid in recorded
        if marker
        in str(table.get(pid, {}).get("command_line") or _command_line(pid))
    )

    def depth(pid: int) -> int:
        observed: set[int] = set()
        current = pid
        result = 0
        while current in table and current not in observed:
            observed.add(current)
            current = int(table[current]["parent_pid"])
            result += 1
        return result

    stopped = []
    for pid in sorted(candidates, key=depth, reverse=True):
        if not _alive(pid):
            continue
        os.kill(pid, signal.SIGTERM)
        stopped.append(pid)
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and any(_alive(pid) for pid in stopped):
        time.sleep(0.1)
    process_file.unlink(missing_ok=True)
    return {
        "stopped": stopped,
        "skipped": skipped,
        "process_file": str(process_file),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", type=Path, default=package_root())
    args = parser.parse_args()
    print(json.dumps(stop_marked_processes(args.package_root), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
