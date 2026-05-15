"""Product-layer CLI entrypoint for Repo Readiness Agent."""

from __future__ import annotations

import argparse
import subprocess
import sys

from .contract import load_product_report, product_report_to_json
from .engine import build_product_report, run_engine
from .followup import build_follow_up
from .formatter import render_text_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Repo Readiness Agent product CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect", help="Inspect a GitHub repository or local path")
    inspect_parser.add_argument("repo", help="GitHub repository URL or local path")
    inspect_parser.add_argument("--branch", default=None, help="Optional git branch/ref to inspect")
    inspect_parser.add_argument("--subdir", default=None, help="Optional repository subdirectory to inspect")
    inspect_parser.add_argument("--strictness", choices=["relaxed", "balanced", "strict"], default="balanced")
    inspect_parser.add_argument("--language-hint", default=None, help="Override detected dominant language label")
    inspect_parser.add_argument("--format", choices=["text", "json", "both"], default="text")

    followup_parser = subparsers.add_parser("followup", help="Compare two product-layer JSON reports")
    followup_parser.add_argument("before", help="Path to the earlier product-layer JSON report")
    followup_parser.add_argument("after", help="Path to the later product-layer JSON report")
    followup_parser.add_argument("--target-stage", default="Handoff-ready", help="Target stage for stop-condition evaluation")
    followup_parser.add_argument("--target-confidence", default="High", help="Target confidence for stop-condition evaluation")
    followup_parser.add_argument("--format", choices=["text", "json", "both"], default="text")

    return parser.parse_args()


def run_inspect(args: argparse.Namespace) -> int:
    score_report = run_engine(
        args.repo,
        branch=args.branch,
        subdir=args.subdir,
        strictness=args.strictness,
        language_hint=args.language_hint,
    )
    product_report = build_product_report(score_report)

    if args.format == "json":
        print(product_report_to_json(product_report))
    elif args.format == "both":
        print(render_text_report(product_report))
        print("\n--- JSON ---")
        print(product_report_to_json(product_report))
    else:
        print(render_text_report(product_report))
    return 0


def run_followup(args: argparse.Namespace) -> int:
    before = load_product_report(args.before)
    after = load_product_report(args.after)
    after.follow_up = build_follow_up(
        before,
        after,
        target_stage=args.target_stage,
        target_confidence=args.target_confidence,
    )

    if args.format == "json":
        print(product_report_to_json(after))
    elif args.format == "both":
        print(render_text_report(after))
        print("\n--- JSON ---")
        print(product_report_to_json(after))
    else:
        print(render_text_report(after))
    return 0


def main() -> int:
    args = parse_args()

    try:
        if args.command == "inspect":
            return run_inspect(args)
        if args.command == "followup":
            return run_followup(args)
        raise ValueError(f"unsupported command: {args.command}")
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(exc.stderr or str(exc))
        return exc.returncode or 1
    except Exception as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
