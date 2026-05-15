# Repo Readiness Agent - Demo Script

## Goal

Show, in a short live flow, that Repo Readiness Agent does not just inspect a GitHub repository once.

It turns repository evidence into a founder-facing decision, generates the next execution brief, and can follow up autonomously over time.

---

## 30-second version

1. Open RepoReadinessAgent
2. Say the promise in one sentence:
   - a founder submits a GitHub repo
   - the agent inspects it autonomously
   - the agent returns a readiness judgment plus what to do next
3. Show one prepared report
4. Highlight:
   - Stage
   - Verdict
   - Top risks
   - Top 3 fixes
   - Autonomous improvement brief
5. Close with the point:
   - this helps a founder decide whether the repo is still a Prototype, already an MVP, or ready for handoff

Suggested close:
> Repo Readiness Agent turns repository evidence into a founder decision and a next-action brief.

Suggested sample to open first:
- `examples/sample_outputs/qris_payment_bot_report.txt`
- or run `PYTHONPATH=src python3 -m repo_readiness_agent.cli inspect <repo-url>`

---

## 2-minute version

### 1. Problem
Solo founders can build quickly, but often cannot confidently judge whether their repository is solid enough to demo, launch, or hand off.

### 2. Input
The founder provides a GitHub repository URL.

### 3. Core autonomous loop
The agent performs:
1. Repo Intake
2. Signal Inspection
3. Readiness Judgment
4. Founder Guidance

### 4. What the founder gets immediately
The system returns:
- Stage
- Verdict
- Top risks
- Top 3 fixes
- Confidence
- Autonomous improvement brief

Optional founder-facing gates:
- Demo-safe?
- Launch-ready?
- Handoff-ready?

### 5. Why this matters
Instead of giving raw code warnings only, the product gives a founder decision and an execution-ready next step.

### 6. Follow-up autonomy loop
For tracked repositories, the agent can re-check progress later and notify whether the repo improved, stayed unchanged, or is still blocked.

The follow-up loop now has a stronger autonomous story:
1. re-check the same repo later
2. compare the new result with the previous report
3. generate an autonomous delta brief
4. tell the founder what improved, what is still blocked, and what matters next
5. stop once the target readiness/confidence state is reached

Suggested follow-up artifacts to show:
- `examples/sample_outputs/qris_payment_bot_followup_before.json`
- `examples/sample_outputs/qris_payment_bot_followup_after.json`
- `examples/sample_outputs/qris_payment_bot_followup_result.json`
- or run `PYTHONPATH=src python3 -m repo_readiness_agent.cli followup examples/sample_outputs/qris_payment_bot_followup_before.json examples/sample_outputs/qris_payment_bot_followup_after.json`

### 7. Best demo beat order
If you have only a short slot, use this sequence:
1. Show one inspect result
2. Point to the autonomous improvement brief
3. Explain that the founder can do it personally or delegate it
4. Show one follow-up result
5. Point to the autonomous delta brief
6. Close on the idea that this is a compact single-agent readiness loop, not a one-shot checker

---

## Presenter notes

Emphasize:
- single-agent clarity
- founder-facing usefulness
- evidence-based repo inspection
- top-next-fix guidance
- autonomous improvement brief
- autonomous delta brief

Avoid over-emphasizing:
- multi-agent complexity
- generic AI hype
- raw scoring as the whole product

If judges ask why this is more than a code checker, answer:
- it does not stop at warnings
- it produces a readiness judgment
- it generates an execution-ready improvement brief
- it follows up later and reinterprets progress through a delta brief
