# NotebookLM Video Script - Repo Readiness Agent

Source: NotebookLM notebook `Repo Readiness Agent Hackathon Pitch`
Notebook ID: `3d49609f-88f4-4806-9212-0ec9b08f4f03`
Conversation ID: `5926365f-d185-43c2-87bd-102f76c5cb75`

## 90-second script

**Hook**
AI lets us ship software incredibly fast today, but there is a catch.

**Problem**
Solo founders can build quickly, but they often struggle to judge whether their codebase is actually solid enough to demo, launch, or hand off to an engineer. Existing tools usually return noisy technical warnings and raw lint issues, leaving founders to translate all that into a business decision by themselves.

**Product action**
Meet Repo Readiness Agent. It is a hackathon-ready product built for solo founders. You simply input a GitHub URL, and the agent turns that repository into a clear, actionable readiness assessment. It is currently best framed as a strong hackathon-ready product rather than a fully hardened SaaS.

**Autonomy loop**
The flow is intentionally simple and autonomous. The founder gives only the repository URL. The agent then performs four steps on its own: Repo Intake, Signal Inspection, Readiness Judgment, and Founder Guidance. The founder does not need to manually choose files or interpret raw engineering metrics.

**Sample output**
Instead of a generic code quality score, the agent returns exactly what a founder needs: Stage, Verdict, Top risks, Top 3 fixes, and Confidence. In one example run, the agent classifies the repo as MVP with Medium confidence, then points directly to the top fixes needed before safer handoff.

**Why it matters**
This matters because it reduces hidden technical risk and gives founders a focused next-action list instead of developer noise. It answers the real question: what stage is this repo in, what are the top blockers, and what should be fixed next?

**Close**
Whether you are preparing for a pitch, a launch, or hiring a contractor, Repo Readiness Agent turns raw repository evidence into a confident founder decision.

## Recording note

Recommended usage:
- use this as the narration base for the hackathon demo video
- pair it with:
  - `docs/demo_script.md`
  - `docs/demo_production_brief.md`
  - `pitch_deck/notebooklm/repo_readiness_agent_pitch_deck_notebooklm.pdf`
