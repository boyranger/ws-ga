"""Formatting helpers for Repo Readiness Agent product output."""

from __future__ import annotations

from .contract import ProductReport


def build_fix_prompts(report: ProductReport) -> list[str]:
    prompts: list[str] = []
    for index, fix in enumerate(report.top_fixes, start=1):
        prompts.append(
            "\n".join(
                [
                    f"Prompt {index}:",
                    "Kamu adalah senior software engineer yang sedang memperbaiki repository GitHub.",
                    f"Tujuan utama: {fix}",
                    f"Tahap repo saat ini: {report.stage}",
                    f"Confidence saat ini: {report.confidence}",
                    "Tolong:",
                    "1. Identifikasi file atau area kode yang paling mungkin perlu diubah.",
                    "2. Jelaskan akar masalah secara singkat.",
                    "3. Berikan rencana perubahan yang konkret dan minimal.",
                    "4. Tulis patch atau contoh implementasi yang relevan.",
                    "5. Tambahkan langkah verifikasi setelah perubahan.",
                    "6. Jika ada tradeoff, jelaskan keputusan yang paling aman untuk repo production-minded.",
                    "Jawab dengan format: Ringkasan masalah, file yang diubah, perubahan yang disarankan, patch/contoh kode, dan langkah verifikasi.",
                ]
            )
        )
    return prompts


def render_text_report(report: ProductReport) -> str:
    lines = [
        f"Stage: {report.stage}",
        f"Verdict: {report.verdict}",
        f"Confidence: {report.confidence}",
        "",
        "Risiko utama:",
    ]
    lines.extend(f"- {risk}" for risk in report.top_risks)
    lines.append("")
    lines.append("Top 3 perbaikan:")
    lines.extend(f"- {fix}" for fix in report.top_fixes)

    prompts = build_fix_prompts(report)
    if prompts:
        lines.extend(["", "Prompt rekomendasi untuk memperbaiki top 3 perbaikan:"])
        for prompt in prompts:
            lines.extend(["", prompt])

    if report.gates:
        lines.extend(
            [
                "",
                "Founder gates:",
                f"- Demo-safe? {report.gates.demo_safe}",
                f"- Launch-ready? {report.gates.launch_ready}",
                f"- Handoff-ready? {report.gates.handoff_ready}",
            ]
        )

    if report.follow_up:
        lines.extend(
            [
                "",
                "Follow-up:",
                f"- Status: {report.follow_up.status}",
                f"- Stop condition: {report.follow_up.stop_condition}",
            ]
        )

    return "\n".join(lines)
