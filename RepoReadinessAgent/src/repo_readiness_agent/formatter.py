"""Formatting helpers for Repo Readiness Agent product output."""

from __future__ import annotations

from .contract import ImprovementBrief, ProductReport, RemediationHint


def _guess_fix_focus(fix: str) -> tuple[str, list[str], list[str]]:
    lowered = fix.lower()

    if any(token in lowered for token in ["ci", "workflow", "github actions", "test pipeline", "pipeline"]):
        return (
            "CI dan quality gate",
            [
                "Cari workflow yang belum ada atau belum lengkap di .github/workflows/",
                "Tambahkan langkah lint, test, dan validasi build yang relevan",
                "Pastikan workflow berjalan pada pull request dan push utama",
            ],
            [
                "Tunjukkan YAML workflow yang ditambahkan atau diperbaiki",
                "Jelaskan command verifikasi yang dijalankan di pipeline",
                "Sertakan cara mengecek bahwa workflow berhasil",
            ],
        )

    if any(token in lowered for token in ["readme", "documentation", "docs", "onboarding"]):
        return (
            "Dokumentasi dan onboarding",
            [
                "Cari README, docs, atau instruksi setup yang kurang jelas atau kurang lengkap",
                "Rapikan alur instalasi, konfigurasi, dan cara menjalankan project",
                "Tambahkan contoh penggunaan atau quickstart yang paling penting",
            ],
            [
                "Tulis revisi README atau file docs yang siap commit",
                "Pastikan ada langkah setup yang bisa diikuti dari nol",
                "Tambahkan checklist verifikasi bahwa instruksi benar-benar bisa diikuti",
            ],
        )

    if any(token in lowered for token in ["test", "coverage", "pytest", "unit test", "integration test"]):
        return (
            "Testing dan reliability",
            [
                "Cari area kode yang kritis tapi belum punya test",
                "Tambahkan test minimal untuk path utama dan edge case penting",
                "Pastikan struktur test sesuai stack project",
            ],
            [
                "Tulis file test yang perlu ditambahkan atau diubah",
                "Jelaskan skenario yang dicakup",
                "Sertakan command untuk menjalankan test dan hasil yang diharapkan",
            ],
        )

    if any(token in lowered for token in ["secret", "security", "auth", "token", "password", "exposed"]):
        return (
            "Security dan hardening",
            [
                "Cari sumber risiko di auth, secret handling, config, atau endpoint sensitif",
                "Usulkan perubahan yang mengurangi exposure tanpa merusak flow utama",
                "Pastikan secret dipindahkan ke env/config yang aman bila perlu",
            ],
            [
                "Tunjukkan patch konkret untuk mitigasi risiko",
                "Jelaskan dampak perubahan terhadap perilaku sistem",
                "Tambahkan langkah verifikasi keamanan dasar setelah patch",
            ],
        )

    if any(token in lowered for token in ["refactor", "structure", "architecture", "boundary", "ownership"]):
        return (
            "Arsitektur dan struktur kode",
            [
                "Identifikasi module/function yang ownership-nya kabur atau terlalu bercampur",
                "Usulkan refactor kecil yang memperjelas boundary tanpa rewrite besar",
                "Jaga backward compatibility sebisa mungkin",
            ],
            [
                "Berikan rencana refactor yang sempit dan jelas",
                "Tunjukkan file yang disentuh dan alasan tiap perubahan",
                "Tambahkan langkah verifikasi untuk memastikan behavior tetap sama",
            ],
        )

    return (
        "Perbaikan implementasi umum",
        [
            "Cari area kode, config, atau docs yang paling relevan dengan perbaikan ini",
            "Utamakan perubahan kecil yang paling berdampak",
            "Hindari rewrite besar bila tidak dibutuhkan",
        ],
        [
            "Berikan patch atau contoh perubahan yang siap diterapkan",
            "Jelaskan bagaimana memverifikasi hasilnya",
            "Sebutkan risiko atau tradeoff bila ada",
        ],
    )


def _find_hint_for_fix(report: ProductReport, fix: str) -> RemediationHint | None:
    if not report.remediation_hints:
        return None
    for hint in report.remediation_hints:
        if hint.fix == fix:
            return hint
    return None


def _relay_lines_for_fix(index: int, fix: str, hint: RemediationHint | None) -> list[str]:
    focus, _, deliverables = _guess_fix_focus(fix)
    target_files = hint.target_files if hint and hint.target_files else []
    primary_target = target_files[0] if target_files else "file atau area yang paling terkait dengan perbaikan ini"
    target_summary = ", ".join(target_files[:3]) if target_files else "file/area implementasi yang paling relevan"

    owner_self = (
        f"Buka {primary_target}, pahami masalah inti di area itu, lalu lakukan perubahan kecil yang langsung menaikkan readiness untuk fokus {focus.lower()}."
    )
    owner_delegate = (
        f"Minta engineer fokus pada {target_summary}, jelaskan bahwa tujuan utamanya adalah '{fix}', lalu minta perubahan yang sempit, bukan rewrite besar."
    )
    owner_acceptance = (
        f"{deliverables[0]}; {deliverables[1]}; {deliverables[2]}."
    )

    lines = [
        f"Relay {index}: {fix}",
        f"- Kalau kamu kerjakan sendiri: {owner_self}",
        f"- Kalau kamu delegasikan ke engineer: {owner_delegate}",
        f"- Hasil jadi yang harus kamu minta: {owner_acceptance}",
    ]
    if hint and hint.line_hints:
        lines.append(f"- Area awal yang sebaiknya dilihat dulu: {hint.line_hints[0]}")
    return lines


def build_founder_relays(report: ProductReport) -> list[str]:
    relays: list[str] = []
    for index, fix in enumerate(report.top_fixes, start=1):
        hint = _find_hint_for_fix(report, fix)
        relays.append("\n".join(_relay_lines_for_fix(index, fix, hint)))
    return relays


def build_autonomous_improvement_briefs(report: ProductReport) -> list[str]:
    briefs = report.improvement_briefs or []
    rendered: list[str] = []
    for index, brief in enumerate(briefs, start=1):
        rendered.append(
            "\n".join(
                [
                    f"Brief {index}: {brief.fix}",
                    f"- Objective: {brief.objective}",
                    f"- Kenapa sekarang: {brief.why_now}",
                    "- File target:",
                    *[f"  - {item}" for item in brief.target_files],
                    "- Kalau kamu kerjakan sendiri:",
                    *[f"  - {item}" for item in brief.do_it_yourself],
                    "- Kalau kamu delegasikan ke engineer:",
                    *[f"  - {item}" for item in brief.delegate_to_engineer],
                    "- Acceptance criteria:",
                    *[f"  - {item}" for item in brief.acceptance_criteria],
                    "- Verifikasi:",
                    *[f"  - {item}" for item in brief.verification_steps],
                ]
            )
        )
    return rendered


def build_fix_prompts(report: ProductReport) -> list[str]:
    prompts: list[str] = []
    for index, fix in enumerate(report.top_fixes, start=1):
        focus, guidance, deliverables = _guess_fix_focus(fix)
        prompts.append(
            "\n".join(
                [
                    f"Prompt {index}:",
                    "Kamu adalah senior software engineer yang sedang memperbaiki repository GitHub agar lebih siap dipakai untuk demo, early users, atau handoff.",
                    f"Fokus perbaikan: {focus}",
                    f"Tujuan utama: {fix}",
                    f"Tahap repo saat ini: {report.stage}",
                    f"Confidence saat ini: {report.confidence}",
                    "Konteks penting: prioritaskan output yang benar-benar applicable dan bisa langsung dieksekusi oleh engineer.",
                    "Tolong kerjakan dengan pendekatan berikut:",
                    f"1. {guidance[0]}",
                    f"2. {guidance[1]}",
                    f"3. {guidance[2]}",
                    "4. Jelaskan akar masalah secara singkat dan langsung ke inti.",
                    "5. Berikan perubahan paling kecil yang memberi dampak paling nyata.",
                    "6. Jika perlu, tulis patch, potongan kode, atau struktur file final yang diusulkan.",
                    "Deliverable yang wajib ada di jawaban:",
                    f"- {deliverables[0]}",
                    f"- {deliverables[1]}",
                    f"- {deliverables[2]}",
                    "Format jawaban yang diminta: Ringkasan masalah, file/area yang diubah, patch/contoh perubahan, langkah verifikasi, dan risiko/tradeoff.",
                    "Jangan beri saran generik. Buat jawaban yang siap dipakai untuk implementasi nyata.",
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

    if report.remediation_hints:
        lines.extend(["", "Panduan file target untuk perbaikan:"])
        for hint in report.remediation_hints:
            lines.append("")
            lines.append(f"Perbaikan: {hint.fix}")
            lines.append(f"Kenapa target ini: {hint.why}")
            lines.append("File yang kemungkinan perlu disentuh:")
            lines.extend(f"- {path}" for path in (hint.target_files or ["Belum ada target file yang cukup kuat dari scan saat ini."]))
            if hint.line_hints:
                lines.append("Line/area yang patut dicek dulu:")
                lines.extend(f"- {item}" for item in hint.line_hints)

    briefs = build_autonomous_improvement_briefs(report)
    if briefs:
        lines.extend(["", "Autonomous improvement brief:"])
        for brief in briefs:
            lines.extend(["", brief])

    relays = build_founder_relays(report)
    if relays:
        lines.extend(["", "Relay rekomendasi untuk solo founder:"])
        for relay in relays:
            lines.extend(["", relay])

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

    if report.delta_brief:
        lines.extend(
            [
                "",
                "Autonomous delta brief:",
                f"- Ringkasan: {report.delta_brief.summary}",
                "- Yang membaik:",
                *[f"  - {item}" for item in report.delta_brief.what_improved],
                "- Yang masih menghambat:",
                *[f"  - {item}" for item in report.delta_brief.what_still_blocked],
                f"- Prioritas sekarang: {report.delta_brief.priority_now}",
                f"- Aksi founder: {report.delta_brief.founder_action}",
                f"- Aksi engineer: {report.delta_brief.engineer_action}",
            ]
        )

    return "\n".join(lines)
