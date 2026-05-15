"""Repo Readiness Agent product package."""

from .contract import FollowUpStatus, FounderGates, ProductReport
from .engine import build_follow_up, build_product_report, derive_founder_gates, run_engine
from .formatter import render_text_report

__all__ = [
    "FollowUpStatus",
    "FounderGates",
    "ProductReport",
    "run_engine",
    "derive_founder_gates",
    "build_product_report",
    "build_follow_up",
    "render_text_report",
]
