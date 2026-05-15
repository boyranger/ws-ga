# Repo Readiness Agent - Pitch Pack

## 1. Final product narrative

Repo Readiness Agent is an autonomous repo readiness product for solo founders.

It helps founders answer a practical question that most code tools do not answer clearly:

> Is my repository still a Prototype, already an MVP, or ready to hand off confidently?

Instead of only showing technical warnings, the product inspects the repository, judges its engineering maturity, highlights the biggest risks, and recommends the top fixes that matter next.

---

## 2. Short pitch

Repo Readiness Agent is an autonomous agent for solo founders that reviews a GitHub repository and tells whether it is still a Prototype, already an MVP, or ready for handoff — plus the top risks and next fixes that matter most.

---

## 3. Autonomy explanation

The product is autonomous because the founder only provides a repository.

The agent then performs the rest of the decision loop itself:
1. **Repo Intake** - accept the GitHub URL
2. **Signal Inspection** - inspect relevant engineering signals
3. **Readiness Judgment** - determine the maturity stage
4. **Founder Guidance** - return the verdict, risks, and next fixes
5. **Autonomous Improvement Brief** - translate the top fixes into an execution-ready brief
6. **Follow-up Loop** - re-check the same repo later, compare progress, and generate a delta brief

The founder does not need to manually choose files, define checks, or interpret technical evidence step by step.

What makes the autonomy visible in the current product:
- the agent identifies the likely target files
- the agent can point to grounded line/area hints when scan evidence exists
- the agent generates a founder-usable improvement brief
- the agent can automatically re-check a tracked repo and send a delta brief later

---

## 4. Why one agent is enough

One agent is enough because the product job is narrow and clear:
- inspect the repo
- judge its readiness
- explain the result
- suggest the next improvements

Adding multiple agents would increase complexity faster than it increases founder value for the hackathon version.

---

## 5. Founder value explanation

Founders can ship quickly, especially with AI coding help, but often still cannot confidently judge whether the repo is solid enough to demo, launch, or hand off.

Repo Readiness Agent closes that gap by turning repo evidence into a practical founder decision.

---

## 6. Demo reminder

When presenting, emphasize:
- repo readiness uncertainty is the real problem
- the product gives a founder decision, not just a code score
- the output is actionable: stage, risks, next fixes, and an improvement brief
- the follow-up loop makes the product feel like a real agent over time
- the delta brief shows that the agent does not just re-run checks, but also reinterprets progress
- the sample output and live CLI wording should stay consistent

## 7. Suggested demo assets

Open these assets first during presentation prep:
- `examples/sample_outputs/qris_payment_bot_report.txt`
- `examples/sample_outputs/qris_payment_bot_report.json`
- `examples/sample_outputs/qris_payment_bot_followup_result.json`

## 8. Best one-line autonomy claim

> Repo Readiness Agent is a compact single-agent loop that inspects a repo, judges its readiness, generates the next improvement brief, then follows up later with a delta brief until the target state is reached.
