"""Formatting helpers for Repo Readiness Agent product output."""

from __future__ import annotations

from .contract import ProductReport


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
