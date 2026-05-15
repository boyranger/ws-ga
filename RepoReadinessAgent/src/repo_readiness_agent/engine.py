"""Engine adapter for Repo Readiness Agent.

This module bridges the lower-level repo_quality_scorer engine into the
product-facing report contract used by Repo Readiness Agent.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from .contract import FounderGates, ProductReport, RemediationHint

PACKAGE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_ROOT.parent.parent
SCORER_PATH = REPO_ROOT / "tools" / "repo_quality_scorer" / "repo_quality_scorer.py"


def run_engine(
    repo: str,
    *,
    branch: str | None = None,
    subdir: str | None = None,
    strictness: str = "balanced",
    language_hint: str | None = None,
) -> dict[str, Any]:
    cmd = [sys.executable, str(SCORER_PATH), repo, "--format", "json", "--strictness", strictness]
    if branch:
        cmd.extend(["--branch", branch])
    if subdir:
        cmd.extend(["--subdir", subdir])
    if language_hint:
        cmd.extend(["--language-hint", language_hint])

    completed = subprocess.run(cmd, text=True, capture_output=True, check=True)
    return json.loads(completed.stdout)


def derive_founder_gates(score_report: dict[str, Any]) -> FounderGates:
    stage = score_report["maturity_level"]
    production_score = float(score_report["production_readiness_score"])
    code_score = float(score_report["code_quality_score"])
    confidence = score_report["confidence"]

    demo_safe = "yes" if stage in {"MVP", "Handoff-ready"} or production_score >= 6.0 else "not yet"
    launch_ready = "yes" if stage == "Handoff-ready" and production_score >= 7.5 and confidence != "Low" else "not yet"
    handoff_ready = "yes" if stage == "Handoff-ready" and code_score >= 7.0 and confidence == "High" else "not yet"

    return FounderGates(
        demo_safe=demo_safe,
        launch_ready=launch_ready,
        handoff_ready=handoff_ready,
    )


def _build_remediation_hints(score_report: dict[str, Any], fixes: list[str]) -> list[RemediationHint]:
    facts = score_report.get("facts") or {}
    debug_examples = facts.get("debug_examples") or []
    security_examples = facts.get("security_examples") or []
    secret_examples = facts.get("secret_examples") or []
    top_large_files = facts.get("top_large_files") or []

    hints: list[RemediationHint] = []
    for fix in fixes:
        lowered = fix.lower()
        target_files: list[str] = []
        line_hints: list[str] = []
        why = "Perkiraan target ini diambil dari sinyal scan repo saat ini."

        if "ci" in lowered or "workflow" in lowered:
            target_files = [".github/workflows/ci.yml", ".github/workflows/test.yml"]
            why = "Repo belum menunjukkan workflow CI, jadi perbaikan paling mungkin adalah menambah file workflow baru."
        elif "test" in lowered:
            target_files = ["tests/", "test/", "src/<core-module>"]
            why = "Skor testing rendah biasanya berarti perlu menambah file test di area core flow yang sudah ada."
        elif ".env.example" in lowered or "config template" in lowered or "environment example" in lowered:
            target_files = [".env.example", "README.md"]
            why = "Repo belum punya template konfigurasi yang jelas, jadi file env example dan instruksi setup jadi target utama."
        elif "security" in lowered or "secret" in lowered or "credential" in lowered:
            target_files = [item["path"] for item in (secret_examples + security_examples)[:3]] or ["config/", "src/"]
            why = "Ada sinyal security/secret pattern yang bisa ditinjau langsung di file terkait."
            line_hints = [f"{item['path']}:{item['line']} — {item['label']}" for item in (secret_examples + security_examples)[:3]]
        elif "oversized" in lowered or "smaller units" in lowered or "clearer boundaries" in lowered or "split" in lowered:
            target_files = [item["path"] for item in top_large_files[:3]] or ["src/"]
            why = "Repo punya file besar yang kemungkinan menjadi pusat kompleksitas dan kandidat refactor awal."
            line_hints = [f"{item['path']} — sekitar {item['lines']} baris, mulai review dari area function/class terbesar" for item in top_large_files[:3]]
        elif "health" in lowered or "readiness" in lowered:
            target_files = ["src/", "app/", "server/", "README.md"]
            why = "Perbaikan operability biasanya menyentuh endpoint runtime dan dokumentasi deployment/health check."
        else:
            target_files = [item["path"] for item in top_large_files[:2]] or ["README.md", "src/"]
            why = "Belum ada target tunggal yang pasti, jadi mulai dari file besar atau entrypoint dokumentasi/kode paling mungkin memberi dampak cepat."

        if not line_hints and debug_examples and ("debug" in lowered or "review" in lowered or "insecure" in lowered):
            line_hints = [f"{item['path']}:{item['line']} — {item['label']}" for item in debug_examples[:3]]

        deduped_targets: list[str] = []
        for item in target_files:
            if item and item not in deduped_targets:
                deduped_targets.append(item)

        hints.append(
            RemediationHint(
                fix=fix,
                target_files=deduped_targets[:3],
                why=why,
                line_hints=line_hints[:3],
            )
        )
    return hints


def build_product_report(score_report: dict[str, Any]) -> ProductReport:
    risks = list(score_report.get("risks") or [])[:3]
    fixes = list(score_report.get("top_improvements") or [])[:3]

    if not risks:
        risks = ["No major risks were surfaced by the current lightweight scan."]
    if not fixes:
        fixes = ["No specific next fixes were surfaced by the current lightweight scan."]

    return ProductReport(
        stage=score_report["maturity_level"],
        verdict=score_report["verdict"],
        confidence=score_report["confidence"],
        top_risks=risks,
        top_fixes=fixes,
        remediation_hints=_build_remediation_hints(score_report, fixes),
        gates=derive_founder_gates(score_report),
    )
