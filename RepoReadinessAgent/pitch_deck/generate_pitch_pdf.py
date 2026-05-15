from pathlib import Path

SLIDES = [
    {
        "title": "Repo Readiness Agent",
        "subtitle": "Autonomous repo readiness for solo founders",
        "bullets": [
            "Hackathon product: founder-facing repo readiness agent",
            "Input: a GitHub repository URL",
            "Output: a clear readiness decision",
            "Core promise: Is this repository still a Prototype, already an MVP, or ready for handoff?",
        ],
    },
    {
        "title": "The Problem",
        "subtitle": "Founders can ship fast, but still lack engineering certainty",
        "bullets": [
            "AI tools help solo founders build quickly",
            "But speed does not guarantee repo quality or readiness",
            "Existing tools give warnings, scores, and code smells",
            "They usually do not answer the founder's real question",
            "Founder question: Is this repo solid enough to demo, launch, or hand off?",
        ],
    },
    {
        "title": "The Solution",
        "subtitle": "Repo Readiness Agent turns repo evidence into a founder decision",
        "bullets": [
            "Founder submits a GitHub repository",
            "Agent inspects the repo autonomously",
            "Agent synthesizes engineering signals into founder language",
            "Founder-facing output: Stage, Verdict, Top risks, Top 3 fixes, Confidence",
        ],
    },
    {
        "title": "Why This Is an Agent",
        "subtitle": "The user gives only the repository. The agent does the rest.",
        "bullets": [
            "Repo Intake",
            "Signal Inspection",
            "Readiness Judgment",
            "Founder Guidance",
            "Optional follow-up: Improved / Unchanged / Still blocked until target reached",
        ],
    },
    {
        "title": "Demo Output Example",
        "subtitle": "Sample founder-facing result from a public repository",
        "bullets": [
            "Stage: MVP",
            "Verdict: usable for demos or early users, but still needs focused hardening before handoff",
            "Confidence: Medium",
            "Top risks: large files and missing environment template",
            "Top fixes: split oversized files, review flagged security patterns, add .env.example",
            "Founder gates: Demo-safe yes, Launch-ready not yet, Handoff-ready not yet",
        ],
    },
    {
        "title": "Why It Matters",
        "subtitle": "Better next-step decisions for solo founders",
        "bullets": [
            "Know whether a repo is ready for a demo",
            "Reduce hidden technical risk before launch",
            "Prepare cleaner handoff to engineers or contractors",
            "Focus only on the fixes that matter most next",
            "Closing line: Repo Readiness Agent turns repository evidence into a founder decision.",
        ],
    },
]


def esc(text: str) -> str:
    return text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')


def wrap_text(text: str, width: int):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = word if not current else current + " " + word
        if len(candidate) <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def build_pdf(out_path: Path):
    objects = []

    def add_object(data: bytes):
        objects.append(data)
        return len(objects)

    font_obj = add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    bold_font_obj = add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")

    page_objs = []
    content_objs = []

    width = 792
    height = 612

    for slide in SLIDES:
        lines = []
        lines.append("BT")
        lines.append("/F2 26 Tf")
        lines.append("1 0 0 1 56 548 Tm")
        lines.append(f"({esc(slide['title'])}) Tj")
        lines.append("ET")

        lines.append("BT")
        lines.append("/F1 15 Tf")
        lines.append("0.2 0.2 0.2 rg")
        lines.append("1 0 0 1 56 518 Tm")
        lines.append(f"({esc(slide['subtitle'])}) Tj")
        lines.append("ET")

        y = 470
        for bullet in slide["bullets"]:
            wrapped = wrap_text(bullet, 72)
            first = True
            for subline in wrapped:
                lines.append("BT")
                lines.append("/F1 18 Tf")
                lines.append("0 0 0 rg")
                lines.append(f"1 0 0 1 72 {y} Tm")
                prefix = "• " if first else "  "
                lines.append(f"({esc(prefix + subline)}) Tj")
                lines.append("ET")
                y -= 26
                first = False
            y -= 4

        stream = "\n".join(lines).encode("utf-8")
        content_obj = add_object(b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream")
        content_objs.append(content_obj)
        page_objs.append(None)

    pages_kids_refs = []
    for idx, content_obj in enumerate(content_objs):
        page_dict = (
            f"<< /Type /Page /Parent {{PAGES}} 0 R /MediaBox [0 0 {width} {height}] "
            f"/Resources << /Font << /F1 {font_obj} 0 R /F2 {bold_font_obj} 0 R >> >> "
            f"/Contents {content_obj} 0 R >>"
        ).encode("utf-8")
        page_obj = add_object(page_dict)
        page_objs[idx] = page_obj
        pages_kids_refs.append(f"{page_obj} 0 R")

    pages_obj_num = add_object(
        f"<< /Type /Pages /Count {len(page_objs)} /Kids [{' '.join(pages_kids_refs)}] >>".encode("utf-8")
    )

    for i, obj in enumerate(objects):
        if b"{PAGES}" in obj:
            objects[i] = obj.replace(b"{PAGES}", str(pages_obj_num).encode("utf-8"))

    catalog_obj = add_object(f"<< /Type /Catalog /Pages {pages_obj_num} 0 R >>".encode("utf-8"))

    pdf = bytearray()
    pdf.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{i} 0 obj\n".encode("utf-8"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_pos = len(pdf)
    pdf.extend(f"xref\n0 {len(objects)+1}\n".encode("utf-8"))
    pdf.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        pdf.extend(f"{off:010d} 00000 n \n".encode("utf-8"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects)+1} /Root {catalog_obj} 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("utf-8")
    )

    out_path.write_bytes(pdf)


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "repo_readiness_agent_pitch_deck.pdf"
    build_pdf(out)
    print(out)
