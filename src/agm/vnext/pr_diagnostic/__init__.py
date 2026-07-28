"""PR-native, read-only diagnostic projection of compiled AGM cases."""

from .compiler import compile_pr_diagnostic
from .models import PRDiagnosticView
from .presenters import render_pr_diagnostic_html, render_pr_diagnostic_json, render_pr_diagnostic_markdown
from .sidecar import EvidenceArtifactRef, EvidencePackageReceipt, SidecarEvidenceStore

__all__ = [
    "EvidenceArtifactRef", "EvidencePackageReceipt", "PRDiagnosticView",
    "SidecarEvidenceStore", "compile_pr_diagnostic", "render_pr_diagnostic_html",
    "render_pr_diagnostic_json", "render_pr_diagnostic_markdown",
]
