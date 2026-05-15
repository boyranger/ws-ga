#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.1.0"

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent.parent

TEXT_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".kt", ".php", ".rb",
    ".cs", ".c", ".cpp", ".h", ".hpp", ".swift", ".scala", ".md", ".txt", ".json", ".yaml",
    ".yml", ".toml", ".ini", ".cfg", ".env", ".sh", ".sql", ".html", ".css",
}
CODE_SCAN_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".kt", ".php", ".rb",
    ".cs", ".c", ".cpp", ".h", ".hpp", ".swift", ".scala", ".sh", ".sql", ".html", ".css",
}
CONFIG_SCAN_EXTENSIONS = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env"}
PLACEHOLDER_SECRET_MARKERS = (
    "change_me",
    "example",
    "your_",
    "placeholder",
    "dummy",
    "sample",
    "test",
    "<api_key>",
    "<token>",
    "<secret>",
    "***",
)
SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "dist", "build", "target", "coverage", ".next",
    ".nuxt", ".idea", ".vscode", "__pycache__", ".mypy_cache", ".pytest_cache",
}
SOURCE_DIR_HINTS = ["src", "app", "server", "client", "backend", "frontend", "lib", "pkg"]
TEST_DIR_HINTS = ["tests", "test", "__tests__", "spec", "specs"]
DOC_FILENAMES = {"README.md", "README.MD", "readme.md"}
SECURITY_PATTERNS = [
    (re.compile(r"\beval\s*\("), "eval() usage"),
    (re.compile(r"new\s+Function\s*\("), "new Function() usage"),
    (re.compile(r"dangerouslySetInnerHTML"), "dangerouslySetInnerHTML usage"),
    (re.compile(r"innerHTML\s*="), "innerHTML assignment"),
    (re.compile(r"rejectUnauthorized\s*:\s*false"), "TLS verification disabled"),
    (re.compile(r"NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*['\"]0['\"]"), "TLS verification disabled via env"),
    (re.compile(r"Access-Control-Allow-Origin['\"]?\s*[:=]\s*['\"]\*['\"]"), "CORS wildcard origin"),
    (re.compile(r"cors\s*\(\s*\)"), "CORS without config"),
]
SECRET_PATTERNS = [
    (re.compile(r"(?im)^\s*(?:export\s+)?(?:[A-Z][A-Z0-9_]*?(?:API[_-]?KEY|SECRET|PASSWORD|TOKEN|PRIVATE[_-]?KEY)[A-Z0-9_]*|(?:api[_-]?key|secret|password|token|private[_-]?key))\s*[:=]\s*['\"][^'\"\n]{6,}['\"]\s*$"), "possible hardcoded secret"),
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"), "embedded private key"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "OpenAI-style key"),
]
DEBUG_PATTERNS = [
    re.compile(r"\bconsole\.log\s*\("),
    re.compile(r"\bprint\s*\("),
    re.compile(r"\bdebugger\b"),
    re.compile(r"TODO"),
    re.compile(r"FIXME"),
]
STRICTNESS_FACTORS = {
    "relaxed": 0.85,
    "balanced": 1.0,
    "strict": 1.2,
}


@dataclass
class AnalyzerInfo:
    name: str | None
    applied: bool
    status: str
    summary: str | None
    exit_code: int | None = None
    signals: dict[str, int] | None = None


@dataclass
class RepoFacts:
    repo: str
    local_path: str
    branch: str | None
    files_total: int
    source_files: int
    test_files: int
    doc_files: int
    has_readme: bool
    has_ci: bool
    has_docker: bool
    has_env_example: bool
    has_migrations: bool
    has_healthcheck: bool
    has_lockfile: bool
    has_tests: bool
    has_package_json: bool
    has_pyproject: bool
    has_go_mod: bool
    dominant_language: str
    languages: dict[str, int]
    max_file_lines: int
    top_large_files: list[dict[str, Any]]
    debug_hits: int
    security_hits: int
    secret_hits: int
    entrypoint_hits: int
    analyzer: AnalyzerInfo


@dataclass
class ScoreInputs:
    repo: str
    branch: str | None
    subdir: str | None
    strictness: str
    language_hint: str | None
    output_format: str


@dataclass
class ScoreReport:
    schema_version: str
    repo: str
    local_path: str
    confidence: str
    verdict: str
    maturity_level: str
    code_quality_score: float
    production_readiness_score: float
    founder_gates: dict[str, str]
    follow_up_status_options: list[str]
    monitoring_stop_conditions: list[str]
    breakdown: dict[str, float]
    strengths: list[str]
    risks: list[str]
    red_flags: list[str]
    top_improvements: list[str]
    inputs: ScoreInputs
    facts: RepoFacts


def run(cmd: list[str], cwd: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, check=check, text=True, capture_output=True)


def clone_repo(repo_url: str, branch: str | None, dest: Path) -> Path:
    cmd = ["git", "clone", "--depth", "1"]
    if branch:
        cmd += ["--branch", branch]
    cmd += [repo_url, str(dest)]
    run(cmd)
    return dest


def detect_language_from_name(name: str) -> str | None:
    return {
        ".py": "Python",
        ".js": "JavaScript",
        ".jsx": "JavaScript",
        ".ts": "TypeScript",
        ".tsx": "TypeScript",
        ".go": "Go",
        ".rs": "Rust",
        ".java": "Java",
        ".kt": "Kotlin",
        ".php": "PHP",
        ".rb": "Ruby",
        ".cs": "C#",
        ".c": "C/C++",
        ".cpp": "C/C++",
        ".h": "C/C++",
        ".hpp": "C/C++",
        ".swift": "Swift",
        ".scala": "Scala",
    }.get(Path(name).suffix.lower())


def should_scan_text(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS or path.name in {"Dockerfile", ".env.example"}


def should_scan_code_patterns(path: Path) -> bool:
    return path.suffix.lower() in CODE_SCAN_EXTENSIONS or path.name == "Dockerfile"


def should_scan_config_patterns(path: Path) -> bool:
    return path.name == ".env.example" or path.suffix.lower() in CONFIG_SCAN_EXTENSIONS


def looks_like_placeholder_secret(value: str) -> bool:
    lowered = value.strip().lower()
    return any(marker in lowered for marker in PLACEHOLDER_SECRET_MARKERS)


def resolve_repo_path(repo_path: Path, subdir: str | None) -> Path:
    if not subdir:
        return repo_path
    resolved = (repo_path / subdir).resolve()
    try:
        resolved.relative_to(repo_path.resolve())
    except ValueError as exc:
        raise ValueError(f"subdir escapes repository root: {subdir}") from exc
    if not resolved.exists() or not resolved.is_dir():
        raise FileNotFoundError(f"Subdirectory not found in repo: {subdir}")
    return resolved


def walk_repo(repo_path: Path, repo_label: str, branch: str | None, language_hint: str | None) -> RepoFacts:
    language_counter: Counter[str] = Counter()
    files_total = 0
    source_files = 0
    test_files = 0
    doc_files = 0
    debug_hits = 0
    security_hits = 0
    secret_hits = 0
    entrypoint_hits = 0
    max_file_lines = 0
    top_large_files: list[dict[str, Any]] = []

    has_readme = False
    has_ci = False
    has_docker = False
    has_env_example = False
    has_migrations = False
    has_healthcheck = False
    has_lockfile = False
    has_package_json = False
    has_pyproject = False
    has_go_mod = False

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        root_path = Path(root)
        rel_root = root_path.relative_to(repo_path)

        if ".github" in rel_root.parts and "workflows" in rel_root.parts:
            has_ci = True
        if any(part in {"migrations", "alembic", "db", "schema", "prisma"} for part in rel_root.parts):
            has_migrations = True

        for filename in files:
            files_total += 1
            path = root_path / filename
            rel = path.relative_to(repo_path)
            rel_str = rel.as_posix()
            lower_name = filename.lower()

            if filename in DOC_FILENAMES:
                has_readme = True
                doc_files += 1
            if lower_name.startswith("readme") or lower_name.endswith(".md") or lower_name.endswith(".mdx"):
                doc_files += 1
            if filename == "Dockerfile" or lower_name.endswith("docker-compose.yml") or lower_name.endswith("docker-compose.yaml"):
                has_docker = True
            if lower_name in {"package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb", "poetry.lock", "pdm.lock", "uv.lock", "cargo.lock", "go.sum"}:
                has_lockfile = True
            if filename in {".env.example", ".env.sample", ".env.template", "env.example"}:
                has_env_example = True
            if filename == "package.json":
                has_package_json = True
            if filename == "pyproject.toml":
                has_pyproject = True
            if filename == "go.mod":
                has_go_mod = True
            if re.search(r"health|ping|ready|live", rel_str, re.IGNORECASE):
                has_healthcheck = True
            if re.search(r"main\.|app\.|server\.|api\.|index\.", filename, re.IGNORECASE):
                entrypoint_hits += 1

            is_test = any(part.lower() in TEST_DIR_HINTS for part in rel.parts) or re.search(r"(test|spec)\.(py|js|ts|go|rb|php|java|kt|rs)$", lower_name)
            is_source = any(part.lower() in SOURCE_DIR_HINTS for part in rel.parts) or path.suffix.lower() in {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".kt", ".php", ".rb"}

            lang = detect_language_from_name(filename)
            if lang:
                language_counter[lang] += 1
            if is_source:
                source_files += 1
            if is_test:
                test_files += 1

            if not should_scan_text(path):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            line_count = text.count("\n") + 1
            if line_count > max_file_lines:
                max_file_lines = line_count
            if line_count >= 250:
                top_large_files.append({"path": rel_str, "lines": line_count})

            if should_scan_code_patterns(path):
                for pattern in DEBUG_PATTERNS:
                    debug_hits += len(pattern.findall(text))
                for pattern, _label in SECURITY_PATTERNS:
                    security_hits += len(pattern.findall(text))

            if should_scan_code_patterns(path) or should_scan_config_patterns(path):
                for pattern, _label in SECRET_PATTERNS:
                    for match in pattern.finditer(text):
                        snippet = match.group(0)
                        if looks_like_placeholder_secret(snippet):
                            continue
                        secret_hits += 1

    top_large_files = sorted(top_large_files, key=lambda item: item["lines"], reverse=True)[:10]
    dominant_language = language_hint or (language_counter.most_common(1)[0][0] if language_counter else "Unknown")

    return RepoFacts(
        repo=repo_label,
        local_path=str(repo_path),
        branch=branch,
        files_total=files_total,
        source_files=source_files,
        test_files=test_files,
        doc_files=doc_files,
        has_readme=has_readme,
        has_ci=has_ci,
        has_docker=has_docker,
        has_env_example=has_env_example,
        has_migrations=has_migrations,
        has_healthcheck=has_healthcheck,
        has_lockfile=has_lockfile,
        has_tests=test_files > 0,
        has_package_json=has_package_json,
        has_pyproject=has_pyproject,
        has_go_mod=has_go_mod,
        dominant_language=dominant_language,
        languages=dict(language_counter),
        max_file_lines=max_file_lines,
        top_large_files=top_large_files,
        debug_hits=debug_hits,
        security_hits=security_hits,
        secret_hits=secret_hits,
        entrypoint_hits=entrypoint_hits,
        analyzer=AnalyzerInfo(name=None, applied=False, status="skipped", summary=None),
    )


def maybe_run_backbone(repo_path: Path, facts: RepoFacts) -> AnalyzerInfo:
    detected_js_like = facts.has_package_json or facts.has_go_mod or facts.dominant_language in {"JavaScript", "TypeScript", "Go"}
    if not detected_js_like:
        return AnalyzerInfo(name="code-quality-check", applied=False, status="skipped", summary="ecosystem not applicable in v1")

    tool_repo = Path("/tmp/code-quality-check")
    if not tool_repo.exists():
        return AnalyzerInfo(name="code-quality-check", applied=False, status="missing", summary="backbone repo not available locally")

    try:
        result = run(["node", str(tool_repo / "bin" / "code-quality.js")], cwd=str(repo_path), check=False)
        combined = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
        return AnalyzerInfo(
            name="code-quality-check",
            applied=True,
            status="pass" if result.returncode == 0 else "warn",
            exit_code=result.returncode,
            summary=combined[-4000:] or None,
            signals={
                "failed_mentions": combined.lower().count("failed"),
                "warn_mentions": combined.lower().count("warn"),
                "pass_mentions": combined.lower().count("pass"),
            },
        )
    except Exception as exc:
        return AnalyzerInfo(name="code-quality-check", applied=True, status="error", summary=str(exc))


def clamp(value: float, low: float = 1.0, high: float = 10.0) -> float:
    return round(max(low, min(high, value)), 1)


def strict_penalty(amount: float, strictness: str) -> float:
    return amount * STRICTNESS_FACTORS[strictness]


def score_architecture(facts: RepoFacts, strictness: str) -> float:
    score = 5.5
    if facts.source_files >= 8:
        score += 1.0
    if len(facts.languages) == 1 and facts.source_files > 0:
        score += 0.3
    if facts.has_migrations:
        score += 0.4
    if facts.entrypoint_hits >= 2:
        score += 0.5
    if facts.max_file_lines > 800:
        score -= strict_penalty(1.0, strictness)
    elif facts.max_file_lines > 500:
        score -= strict_penalty(0.6, strictness)
    if len(facts.top_large_files) >= 5:
        score -= strict_penalty(0.7, strictness)
    return clamp(score)


def score_code_quality(facts: RepoFacts, strictness: str) -> float:
    score = 6.0
    if facts.has_lockfile:
        score += 0.4
    if facts.debug_hits > 0:
        score -= min(1.5, strict_penalty(facts.debug_hits * 0.1, strictness))
    if facts.analyzer.applied:
        if facts.analyzer.status == "pass":
            score += 0.8
        elif facts.analyzer.status == "warn":
            score -= strict_penalty(0.8, strictness)
        elif facts.analyzer.status == "error":
            score -= strict_penalty(0.5, strictness)
    if facts.max_file_lines > 600:
        score -= strict_penalty(0.5, strictness)
    return clamp(score)


def score_security(facts: RepoFacts, strictness: str) -> float:
    score = 6.2
    if facts.has_env_example:
        score += 0.6
    if facts.secret_hits > 0:
        score -= min(3.5, strict_penalty(facts.secret_hits * 1.8, strictness))
    if facts.security_hits > 0:
        score -= min(2.5, strict_penalty(facts.security_hits * 0.7, strictness))
    if not facts.has_env_example and (facts.has_package_json or facts.has_pyproject or facts.has_go_mod):
        score -= strict_penalty(0.5, strictness)
    if facts.has_ci:
        score += 0.2
    return clamp(score)


def score_testing(facts: RepoFacts, strictness: str) -> float:
    if not facts.has_tests:
        return clamp(2.0 - (0.4 if strictness == "strict" else 0.0))
    score = 3.5
    if facts.test_files >= 1:
        score += 0.8
    if facts.test_files >= 3:
        score += 1.0
    if facts.test_files >= 10:
        score += 1.0
    if facts.has_ci:
        score += 1.0
    if facts.test_files >= max(3, facts.source_files // 3):
        score += 0.8
    if strictness == "strict" and facts.test_files < max(2, facts.source_files // 5):
        score -= 0.4
    return clamp(score)


def score_documentation(facts: RepoFacts, strictness: str) -> float:
    if not facts.has_readme:
        return clamp(3.0 - (0.3 if strictness == "strict" else 0.0))
    score = 5.8
    if facts.doc_files >= 3:
        score += 1.0
    if facts.doc_files >= 6:
        score += 0.5
    if facts.has_env_example:
        score += 0.5
    if facts.has_docker:
        score += 0.3
    return clamp(score)


def score_production_readiness(facts: RepoFacts, strictness: str) -> float:
    score = 4.8
    if facts.has_ci:
        score += 1.3
    if facts.has_docker:
        score += 1.0
    if facts.has_env_example:
        score += 0.6
    if facts.has_healthcheck:
        score += 0.6
    if facts.has_migrations:
        score += 0.9
    if facts.has_lockfile:
        score += 0.4
    if facts.has_tests:
        score += 0.3
    else:
        score -= strict_penalty(1.0, strictness)
    if facts.secret_hits > 0:
        score -= min(2.0, strict_penalty(1.2, strictness))
    if strictness == "strict" and not facts.has_ci:
        score -= 0.5
    return clamp(score)


def confidence_for(facts: RepoFacts) -> str:
    evidence = 0
    evidence += 1 if facts.has_readme else 0
    evidence += 1 if facts.source_files > 0 else 0
    evidence += 1 if facts.has_tests else 0
    evidence += 1 if facts.has_ci else 0
    evidence += 1 if facts.analyzer.applied else 0
    evidence += 1 if facts.has_env_example else 0
    if evidence >= 5:
        return "High"
    if evidence >= 3:
        return "Medium"
    return "Low"


def classify_report(code_quality_score: float, production_readiness_score: float) -> tuple[str, str]:
    combined = round((code_quality_score + production_readiness_score) / 2, 1)
    floor = min(code_quality_score, production_readiness_score)

    if combined >= 8.5 and floor >= 8.0:
        return "Handoff-ready", "This repository looks ready for handoff, with strong engineering discipline and only limited cleanup left."
    if combined >= 7.2 and floor >= 6.5:
        return "Handoff-ready", "This repository is close to handoff-ready, but a few hardening steps should be finished before relying on it fully."
    if combined >= 5.5 and floor >= 4.5:
        return "MVP", "This repository looks usable for demos or early users, but it still needs focused hardening before handoff."
    return "Prototype", "This repository still behaves like a prototype and needs more engineering work before it is safe to rely on broadly."


def founder_gates_for(maturity_level: str, confidence: str, production_readiness_score: float, testing_score: float) -> dict[str, str]:
    demo_safe = "yes" if maturity_level in {"MVP", "Handoff-ready"} and confidence != "Low" else "not yet"
    launch_ready = "yes" if maturity_level == "Handoff-ready" and production_readiness_score >= 7.0 else "not yet"
    handoff_ready = "yes" if maturity_level == "Handoff-ready" and production_readiness_score >= 7.5 and testing_score >= 6.0 else "not yet"
    return {
        "demo_safe": demo_safe,
        "launch_ready": launch_ready,
        "handoff_ready": handoff_ready,
    }


def synthesize_notes(facts: RepoFacts, breakdown: dict[str, float], strictness: str) -> tuple[list[str], list[str], list[str], list[str]]:
    strengths: list[str] = []
    risks: list[str] = []
    red_flags: list[str] = []
    improvements: list[str] = []

    if facts.has_readme:
        strengths.append("README exists, so the repository has at least a basic documentation entrypoint.")
    if facts.has_tests:
        strengths.append(f"Repository includes tests ({facts.test_files} detected test files).")
    if facts.has_ci:
        strengths.append("CI workflow files were detected, which improves delivery discipline.")
    if facts.has_docker:
        strengths.append("Deployment/containerization hints exist via Docker-related files.")
    if facts.has_migrations:
        strengths.append("Schema or migration-related files were found, suggesting some persistence discipline.")
    if facts.analyzer.applied and facts.analyzer.status == "pass":
        strengths.append("Backbone analyzer completed successfully for the detected ecosystem.")

    if not facts.has_tests:
        risks.append("No tests were detected, which materially lowers trust in correctness and safe iteration.")
        improvements.append("Add a real test suite for core flows before trusting the repo more broadly.")
    elif strictness == "strict" and facts.test_files < max(2, facts.source_files // 5):
        risks.append("Test presence exists, but breadth still looks thin under strict scoring.")
        improvements.append("Expand tests to cover core modules and critical edge cases, not just happy paths.")
    if not facts.has_ci:
        risks.append("No CI workflow was detected, so quality gates may rely on manual discipline.")
        improvements.append("Add CI to run lint/typecheck/tests on every change.")
    if facts.max_file_lines > 600:
        risks.append("At least one very large file was detected, which may indicate concentrated complexity.")
        improvements.append("Split oversized files/functions into smaller units with clearer boundaries.")
    if facts.security_hits > 0:
        red_flags.append(f"Detected {facts.security_hits} security-pattern hit(s) that deserve manual review.")
        improvements.append("Review the flagged security patterns and remove insecure constructs/defaults.")
    if facts.secret_hits > 0:
        red_flags.append(f"Detected {facts.secret_hits} possible secret exposure hit(s).")
        improvements.append("Review possible hardcoded credentials and keep real secrets in environment/config management.")
    if not facts.has_env_example:
        risks.append("No environment example/template was found, which weakens onboarding and config discipline.")
        improvements.append("Add a .env.example or equivalent config template.")
    if breakdown["production_readiness"] < 5.5:
        risks.append("Production readiness appears below strong deployment confidence.")
        improvements.append("Add missing operational basics: CI, health checks, deployment clarity, and resilience rules.")
    if strictness == "strict" and not facts.has_healthcheck:
        risks.append("Strict mode expects clearer runtime operability signals such as health/readiness endpoints.")
        improvements.append("Add health or readiness indicators to improve operational confidence.")

    if not improvements:
        improvements.append("Calibrate the scorer on more repositories and deepen language-specific analyzers.")

    def dedupe(items: list[str]) -> list[str]:
        seen = set()
        out = []
        for item in items:
            if item not in seen:
                seen.add(item)
                out.append(item)
        return out

    return dedupe(strengths)[:5], dedupe(risks)[:5], dedupe(red_flags)[:5], dedupe(improvements)[:5]


def compute_report(repo_url: str, repo_path: Path, branch: str | None, subdir: str | None, strictness: str, language_hint: str | None, output_format: str) -> ScoreReport:
    scan_path = resolve_repo_path(repo_path, subdir)
    facts = walk_repo(scan_path, repo_url, branch, language_hint)
    facts.analyzer = maybe_run_backbone(scan_path, facts)

    architecture = score_architecture(facts, strictness)
    code_quality = score_code_quality(facts, strictness)
    security = score_security(facts, strictness)
    testing = score_testing(facts, strictness)
    documentation = score_documentation(facts, strictness)
    production_readiness = score_production_readiness(facts, strictness)

    breakdown = {
        "architecture": architecture,
        "code_quality": code_quality,
        "security": security,
        "testing": testing,
        "documentation": documentation,
        "production_readiness": production_readiness,
    }
    code_quality_score = clamp(
        architecture * 0.25 + code_quality * 0.30 + security * 0.15 + testing * 0.20 + documentation * 0.10,
        low=1.0,
        high=10.0,
    )
    production_readiness_score = clamp(
        production_readiness * 0.40 + security * 0.20 + testing * 0.20 + architecture * 0.10 + documentation * 0.10,
        low=1.0,
        high=10.0,
    )
    strengths, risks, red_flags, improvements = synthesize_notes(facts, breakdown, strictness)
    confidence = confidence_for(facts)
    maturity_level, verdict = classify_report(code_quality_score, production_readiness_score)
    founder_gates = founder_gates_for(maturity_level, confidence, production_readiness_score, testing)

    return ScoreReport(
        schema_version=SCHEMA_VERSION,
        repo=repo_url,
        local_path=str(scan_path),
        confidence=confidence,
        verdict=verdict,
        maturity_level=maturity_level,
        code_quality_score=code_quality_score,
        production_readiness_score=production_readiness_score,
        founder_gates=founder_gates,
        follow_up_status_options=["Improved", "Unchanged", "Still blocked"],
        monitoring_stop_conditions=["Target reached", "Keep monitoring"],
        breakdown=breakdown,
        strengths=strengths,
        risks=risks,
        red_flags=red_flags,
        top_improvements=improvements[:3],
        inputs=ScoreInputs(
            repo=repo_url,
            branch=branch,
            subdir=subdir,
            strictness=strictness,
            language_hint=language_hint,
            output_format=output_format,
        ),
        facts=facts,
    )


def render_text(report: ScoreReport) -> str:
    lines = [
        f"Repo: {report.repo}",
        "",
        f"Stage: {report.maturity_level}",
        f"Verdict: {report.verdict}",
        f"Confidence: {report.confidence}",
        f"Demo-safe? {report.founder_gates['demo_safe']}",
        f"Launch-ready? {report.founder_gates['launch_ready']}",
        f"Handoff-ready? {report.founder_gates['handoff_ready']}",
        "",
        f"Code Quality Score: {report.code_quality_score:.1f} / 10",
        f"Production Readiness Score: {report.production_readiness_score:.1f} / 10",
        "",
        "Top risks:",
    ]
    lines.extend([f"- {item}" for item in (report.risks[:3] or ["None noted."])])
    lines.append("")
    lines.append("Top 3 fixes:")
    for idx, item in enumerate(report.top_improvements[:3] or ["None noted."], start=1):
        lines.append(f"{idx}. {item}")
    lines.append("")
    lines.append("Signal breakdown:")
    lines.extend([
        f"- Architecture: {report.breakdown['architecture']:.1f}",
        f"- Code quality: {report.breakdown['code_quality']:.1f}",
        f"- Security: {report.breakdown['security']:.1f}",
        f"- Testing: {report.breakdown['testing']:.1f}",
        f"- Documentation: {report.breakdown['documentation']:.1f}",
        f"- Production readiness: {report.breakdown['production_readiness']:.1f}",
    ])
    lines.append("")
    lines.append("Strengths:")
    lines.extend([f"- {item}" for item in (report.strengths or ["None noted."])])
    lines.append("")
    lines.append("Red flags:")
    lines.extend([f"- {item}" for item in (report.red_flags or ["None noted."])])
    lines.append("")
    lines.append("Follow-up status options:")
    lines.extend([f"- {item}" for item in report.follow_up_status_options])
    lines.append("")
    lines.append("Monitoring stop conditions:")
    lines.extend([f"- {item}" for item in report.monitoring_stop_conditions])
    lines.append("")
    lines.append("Inputs:")
    lines.append(f"- Strictness: {report.inputs.strictness}")
    lines.append(f"- Branch: {report.inputs.branch or 'default'}")
    lines.append(f"- Subdir: {report.inputs.subdir or '/'}")
    lines.append(f"- Language hint: {report.inputs.language_hint or 'auto'}")
    lines.append("")
    lines.append("Facts:")
    lines.append(f"- Dominant language: {report.facts.dominant_language}")
    lines.append(f"- Source files: {report.facts.source_files}")
    lines.append(f"- Test files: {report.facts.test_files}")
    lines.append(f"- Has CI: {report.facts.has_ci}")
    lines.append(f"- Has Docker: {report.facts.has_docker}")
    lines.append(f"- Has env example: {report.facts.has_env_example}")
    lines.append(f"- Has migrations: {report.facts.has_migrations}")
    lines.append(f"- Largest file lines: {report.facts.max_file_lines}")
    lines.append(f"- Backbone analyzer: {report.facts.analyzer.status}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score GitHub repositories for code quality and production readiness")
    parser.add_argument("repo", help="GitHub repository URL or local path")
    parser.add_argument("--branch", help="Optional git branch/ref to clone", default=None)
    parser.add_argument("--subdir", help="Optional repository subdirectory to score", default=None)
    parser.add_argument("--strictness", choices=["relaxed", "balanced", "strict"], default="balanced")
    parser.add_argument("--language-hint", help="Override detected dominant language label", default=None)
    parser.add_argument("--format", choices=["text", "json", "both"], default="text")
    parser.add_argument("--keep-repo", action="store_true", help="Keep cloned temporary repo for inspection")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cleanup_dir: Path | None = None

    try:
        repo_arg = args.repo
        if re.match(r"^(https://|git@|ssh://)", repo_arg):
            cleanup_dir = Path(tempfile.mkdtemp(prefix="repo-quality-"))
            clone_repo(repo_arg, args.branch, cleanup_dir)
            repo_path = cleanup_dir
        else:
            repo_path = Path(repo_arg).resolve()
            if not repo_path.exists():
                raise FileNotFoundError(f"Path not found: {repo_path}")

        report = compute_report(
            repo_url=repo_arg,
            repo_path=repo_path,
            branch=args.branch,
            subdir=args.subdir,
            strictness=args.strictness,
            language_hint=args.language_hint,
            output_format=args.format,
        )
        payload = asdict(report)
        if args.format == "json":
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        elif args.format == "both":
            print(render_text(report))
            print("\n--- JSON ---")
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(render_text(report))
        return 0
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(exc.stderr or str(exc))
        return exc.returncode or 1
    except Exception as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 1
    finally:
        if cleanup_dir and cleanup_dir.exists() and not args.keep_repo:
            shutil.rmtree(cleanup_dir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
