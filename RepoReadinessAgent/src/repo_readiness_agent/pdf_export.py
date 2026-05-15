"""PDF export helpers for Repo Readiness Agent."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer

from .contract import ProductReport
from .formatter import build_autonomous_improvement_briefs, build_fix_prompts, build_founder_relays


def _styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="RepoTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#1d4ed8"),
            spaceBefore=10,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodySmall",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#111827"),
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Meta",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#374151"),
            spaceAfter=4,
        )
    )
    return styles


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )


def _bullet_list(items: list[str], style: ParagraphStyle) -> ListFlowable:
    return ListFlowable(
        [ListItem(Paragraph(_escape(item), style)) for item in items],
        bulletType="bullet",
        start="circle",
        leftIndent=14,
    )


def export_report_to_pdf(report: ProductReport, output_path: str | Path, repo_label: str | None = None) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    styles = _styles()
    doc = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="Laporan Repo Readiness Agent",
        author="Repo Readiness Agent",
    )

    story = []
    story.append(Paragraph("Laporan Repo Readiness Agent", styles["RepoTitle"]))
    if repo_label:
        story.append(Paragraph(f"Repository: {_escape(repo_label)}", styles["Meta"]))
    story.append(Paragraph(f"Tahap: {_escape(report.stage)}", styles["Meta"]))
    story.append(Paragraph(f"Confidence: {_escape(report.confidence)}", styles["Meta"]))
    story.append(Spacer(1, 4))

    story.append(Paragraph("Verdict", styles["SectionHeading"]))
    story.append(Paragraph(_escape(report.verdict), styles["BodySmall"]))

    story.append(Paragraph("Risiko utama", styles["SectionHeading"]))
    story.append(_bullet_list(report.top_risks or ["Tidak ada risiko utama yang terdeteksi pada scan saat ini."], styles["BodySmall"]))

    story.append(Paragraph("Top 3 perbaikan", styles["SectionHeading"]))
    story.append(_bullet_list(report.top_fixes or ["Tidak ada perbaikan utama yang terdeteksi pada scan saat ini."], styles["BodySmall"]))

    if report.remediation_hints:
        story.append(Paragraph("Panduan file target untuk perbaikan", styles["SectionHeading"]))
        for hint in report.remediation_hints:
            story.append(Paragraph(f"Perbaikan: {_escape(hint.fix)}", styles["BodySmall"]))
            story.append(Paragraph(f"Kenapa target ini: {_escape(hint.why)}", styles["BodySmall"]))
            story.append(Paragraph("File yang kemungkinan perlu disentuh:", styles["BodySmall"]))
            story.append(_bullet_list(hint.target_files or ["Belum ada target file yang cukup kuat dari scan saat ini."], styles["BodySmall"]))
            if hint.line_hints:
                story.append(Paragraph("Line/area yang patut dicek dulu:", styles["BodySmall"]))
                story.append(_bullet_list(hint.line_hints, styles["BodySmall"]))
            story.append(Spacer(1, 3))

    briefs = build_autonomous_improvement_briefs(report)
    if briefs:
        story.append(Paragraph("Autonomous improvement brief", styles["SectionHeading"]))
        for brief in briefs:
            story.append(Paragraph(_escape(brief), styles["BodySmall"]))
            story.append(Spacer(1, 3))

    relays = build_founder_relays(report)
    if relays:
        story.append(Paragraph("Relay rekomendasi untuk solo founder", styles["SectionHeading"]))
        for relay in relays:
            story.append(Paragraph(_escape(relay), styles["BodySmall"]))
            story.append(Spacer(1, 3))

    prompts = build_fix_prompts(report)
    if prompts:
        story.append(Paragraph("Prompt rekomendasi untuk memperbaiki top 3 perbaikan", styles["SectionHeading"]))
        for prompt in prompts:
            story.append(Paragraph(_escape(prompt), styles["BodySmall"]))
            story.append(Spacer(1, 3))

    if report.gates:
        story.append(Paragraph("Founder gates", styles["SectionHeading"]))
        story.append(_bullet_list([
            f"Demo-safe? {report.gates.demo_safe}",
            f"Launch-ready? {report.gates.launch_ready}",
            f"Handoff-ready? {report.gates.handoff_ready}",
        ], styles["BodySmall"]))

    if report.follow_up:
        story.append(Paragraph("Follow-up", styles["SectionHeading"]))
        story.append(_bullet_list([
            f"Status: {report.follow_up.status}",
            f"Stop condition: {report.follow_up.stop_condition}",
        ], styles["BodySmall"]))

    doc.build(story)
    return output
