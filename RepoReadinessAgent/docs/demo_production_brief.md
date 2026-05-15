# Repo Readiness Agent - Demo Production Brief

## Purpose

This brief is the fastest single file to use when preparing:
- demo video
- pitch deck slides
- presenter brief

It consolidates the existing product narrative, demo script, and best current artifacts.

---

## 1. Where everything is

### Demo video script
- `RepoReadinessAgent/docs/demo_script.md`

### Pitch / story / slide narrative
- `RepoReadinessAgent/docs/pitch_pack.md`

### Hackathon submission brief
- `RepoReadinessAgent/docs/hackathon_submission.md`

### Product contract
- `RepoReadinessAgent/docs/repo_readiness_product_contract.md`

### Best sample outputs to show
- `RepoReadinessAgent/examples/sample_outputs/qris_payment_bot_report.txt`
- `RepoReadinessAgent/examples/sample_outputs/qris_payment_bot_report.json`
- `RepoReadinessAgent/examples/sample_outputs/flask_product_report.txt`
- `RepoReadinessAgent/examples/sample_outputs/flask_product_report.json`

### Follow-up autonomy demo assets
- `RepoReadinessAgent/examples/sample_outputs/qris_payment_bot_followup_before.json`
- `RepoReadinessAgent/examples/sample_outputs/qris_payment_bot_followup_after.json`
- `RepoReadinessAgent/examples/sample_outputs/qris_payment_bot_followup_result.json`

### Calibration references
- `RepoReadinessAgent/examples/calibration/full_stack_fastapi_template.txt`
- `RepoReadinessAgent/examples/calibration/click.txt`

---

## 2. Recommended demo structure

Use a short 90-second to 2-minute flow.

### Opening: the problem
Say:

> Solo founders can build fast, especially with AI, but they still struggle to judge whether a repository is solid enough to demo, launch, or hand off.

### Product promise
Say:

> Repo Readiness Agent takes a GitHub repository and turns it into a founder-facing decision: is this still a Prototype, already an MVP, or ready for handoff?

### Show the autonomous loop
Use this exact sequence:
1. Repo Intake
2. Signal Inspection
3. Readiness Judgment
4. Founder Guidance

### Show the output
Highlight only these fields first:
- Stage
- Verdict
- Top risks
- Top 3 fixes
- Confidence

Optional second layer:
- Demo-safe?
- Launch-ready?
- Handoff-ready?

### Close
Say:

> Repo Readiness Agent turns repository evidence into a founder decision.

---

## 3. Best assets for the demo video

### Safest primary demo asset
Use:
- `RepoReadinessAgent/examples/sample_outputs/qris_payment_bot_report.txt`

Why:
- already product-shaped
- founder-facing
- low risk during recording

### Best secondary proof asset
Use:
- `RepoReadinessAgent/examples/sample_outputs/flask_product_report.txt`

Why:
- shows the same product layer working on a public repository
- supports credibility

### Best autonomy/follow-up asset
Use:
- `RepoReadinessAgent/examples/sample_outputs/qris_payment_bot_followup_result.json`

Why:
- demonstrates that the product can compare progress over time
- helps satisfy autonomy storytelling for judges

---

## 4. Recommended pitch deck outline

Use 6 slides max.

### Slide 1 - Title
- Repo Readiness Agent
- Autonomous repo readiness for solo founders

### Slide 2 - Problem
- founders can ship fast
- but they cannot confidently judge repo readiness
- existing tools give warnings, not a founder decision

### Slide 3 - Solution
- submit GitHub repo
- agent inspects repo autonomously
- returns stage, verdict, risks, and top fixes

### Slide 4 - Why it is an agent
- Repo Intake
- Signal Inspection
- Readiness Judgment
- Founder Guidance
- optional follow-up monitoring over time

### Slide 5 - Demo output
Show one clean example with:
- Stage
- Verdict
- Top risks
- Top 3 fixes
- Confidence

### Slide 6 - Why it matters
- helps founders decide whether to demo, launch, or hand off
- reduces hidden technical risk
- gives a focused next-action list instead of noisy diagnostics

---

## 5. Suggested speaking brief

### 15-second intro
> Repo Readiness Agent is an autonomous product for solo founders. You give it a GitHub repository, and it tells you whether the repo is still a Prototype, already an MVP, or ready for handoff, plus the top fixes that matter next.

### 30-second value explanation
> Most code tools surface technical issues, but they do not answer the founder's real question: is this repo actually ready for the next business step? Our agent turns repository evidence into a clear founder decision.

### 20-second autonomy explanation
> The user only gives the repository. The agent performs repo intake, signal inspection, readiness judgment, and founder guidance on its own. The founder does not need to manually choose files or interpret raw engineering signals.

### 15-second close
> This is useful before demos, launches, hiring, and handoff. Repo Readiness Agent turns repository evidence into a founder decision.

---

## 6. Recommended live/demo commands

From `RepoReadinessAgent/`:

### Inspect a repository
```bash
PYTHONPATH=src python3 -m repo_readiness_agent.cli inspect https://github.com/pallets/flask --format text
```

### Show JSON output
```bash
PYTHONPATH=src python3 -m repo_readiness_agent.cli inspect https://github.com/pallets/flask --format json
```

### Show follow-up comparison
```bash
PYTHONPATH=src python3 -m repo_readiness_agent.cli followup \
  examples/sample_outputs/qris_payment_bot_followup_before.json \
  examples/sample_outputs/qris_payment_bot_followup_after.json \
  --format text
```

---

## 7. Video recording recommendation

For the hackathon, the safest recording flow is:
1. open slide with problem + solution
2. switch to terminal
3. show one prepared sample output first
4. optionally run one live inspect command
5. show follow-up artifact briefly
6. close with founder value

If time is tight, prefer:
- prepared sample output first
- live CLI second or optional

That reduces demo failure risk.

---

## 8. What to avoid in the demo

Avoid emphasizing:
- multi-agent complexity
- generic code-quality scoring as the main story
- too many technical details about heuristics
- unstable live setup if prepared artifacts already prove the point

Keep the story anchored on:
- founder user
- readiness decision
- autonomous inspection
- actionable next fixes

---

## 9. Current status note

As of the latest prep:
- product-layer CLI works
- founder-facing output is consistent
- sample outputs exist
- calibration outputs exist
- the main remaining improvement area is threshold calibration, not missing product structure
