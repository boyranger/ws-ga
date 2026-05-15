"""Product-layer CLI entrypoint for Repo Readiness Agent."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict

from .engine import build_product_report, run_engine
from .formatter import render_text_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Repo Readiness Agent product CLI")
    parser.add_argument("repo", help="GitHub repository URL or local path")
    parser.add_argument("--branch", default=None, help="Optional git branch/ref to inspect")
    parser.add_argument("--subdir", default=None, help="Optional repository subdirectory to inspect")
    parser.add_argument("--strictness", choices=["relaxed", "balanced", "strict"], default="balanced")
    parser.add_argument("--language-hint", default=None, help="Override detected dominant language label")
    parser.add_argument("--format", choices=["text", "json", "both"], default="text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        score_report = run_engine(
            args.repo,
            branch=args.branch,
            subdir=args.subdir,
            strictness=args.strictness,
            language_hint=args.language_hint,
        )
        product_report = build_product_report(score_report)

        if args.format == "json":
            print(json.dumps(asdict(product_report), indent=2, ensure_ascii=False))
        elif args.format == "both":
            print(render_text_report(product_report))
            print("\n--- JSON ---")
            print(json.dumps(asdict(product_report), indent=2, ensure_ascii=False))
        else:
            print(render_text_report(product_report))
        return 0
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(exc.stderr or str(exc))
        return exc.returncode or 1
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"error: invalid engine JSON output: {exc}\n")
        return 1
    except Exception as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
