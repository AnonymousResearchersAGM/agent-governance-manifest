"""Run the frozen AGM interactive handler against P92-owned runtime state."""

from __future__ import annotations

import argparse
import json
import secrets
import sys
from http.server import ThreadingHTTPServer
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--actor", required=True)
    parser.add_argument("--role", required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--session-marker", required=True)
    parser.add_argument("--ready-file", type=Path, required=True)
    args = parser.parse_args()

    source = str(args.repo_root.resolve() / "src")
    if source not in sys.path:
        sys.path.insert(0, source)

    from agm.vnext.briefing.actions.draft import ReviewDraftStore
    from agm.vnext.briefing.actions.preview import PreviewTokenRegistry
    from agm.vnext.briefing.actions.server import _handler_class
    from agm.vnext.guidance import ActorContext
    from agm.vnext.service import GovernanceService

    service = GovernanceService(
        args.project_root.resolve(),
        work_root=args.work_root.resolve(),
    )
    service.storage.load_case(args.case_id)
    csrf_token = secrets.token_urlsafe(32)
    token_registry = PreviewTokenRegistry()
    draft_store = ReviewDraftStore(service.storage)
    server = ThreadingHTTPServer(
        ("127.0.0.1", args.port),
        _handler_class(
            service,
            case_id=args.case_id,
            actor=ActorContext(
                actor=args.actor,
                role=args.role,
                human=True,
            ),
            csrf_token=csrf_token,
            token_registry=token_registry,
            draft_store=draft_store,
        ),
    )
    args.ready_file.parent.mkdir(parents=True, exist_ok=True)
    args.ready_file.write_text(
        json.dumps(
            {
                "ready": True,
                "host": "127.0.0.1",
                "port": server.server_port,
                "case_id": args.case_id,
                "session_marker": args.session_marker,
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
