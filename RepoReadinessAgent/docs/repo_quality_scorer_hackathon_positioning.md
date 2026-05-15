# Repo Readiness Agent - Hackathon Positioning Pack

## Purpose of this artifact

This document is the scope guardrail for the hackathon version of `repo_quality_scorer`.

For the execution plan and single-agent product structure, also see `docs/repo_readiness_agent_plan.md`.

Use it to keep product decisions narrow, consistent, and founder-focused.

This is not just pitch copy. It is an operating constraint for future implementation, UX, output design, and demo decisions.

---

## Product name

**Repo Readiness Agent**

## Product category

Autonomous repo readiness agent for solo founders.

## One-line summary

An autonomous repo readiness agent for solo founders that reviews a GitHub repository and tells whether it is still a Prototype, already an MVP, or ready for handoff — plus the top fixes to make next.

---

## Primary user

**Solo founder / indie hacker**

Especially founders who:
- build fast
- often use AI coding tools
- are not fully confident assessing engineering maturity
- need a fast readiness judgment before demo, launch, or handoff

### Not primary users in the hackathon scope

These can exist later, but should not drive v1 decisions:
- enterprise engineering managers
- security teams
- generic developer tooling buyers
- investor due diligence workflows
- universal multi-persona code review platforms

---

## Core problem

Solo founders can build software quickly, but they often cannot objectively judge whether their repository is solid enough to:
- demo safely
- launch with confidence
- hand off to an engineer
- show to a client or investor without hidden engineering risk

The problem is not merely "code quality".

The real problem is **repo readiness uncertainty**.

---

## Core job-to-be-done

> Tell me whether my repo is still a prototype, already an MVP, or ready for handoff — and what I should fix next.

If a feature does not support this job directly, it is likely out of scope for the hackathon version.

---

## What the agent does

The agent:
1. accepts a GitHub repository URL
2. clones and inspects the repository autonomously
3. evaluates engineering signals across:
   - architecture
   - code quality
   - security
   - testing
   - documentation
   - production readiness
4. uses backbone analyzers when relevant
   - for example, `code-quality-check` can be treated as a technical reference/backbone analyzer for code-quality-specific signals
5. synthesizes findings into founder-friendly outputs:
   - stage classification
   - verdict
   - top risks
   - top fixes

### Preferred 4-phase product loop

To keep the product easy to explain, the agent should be framed as a compact end-to-end loop:

1. **Repo Intake**
   - accept the GitHub URL
   - clone or access the repository
2. **Signal Inspection**
   - inspect structure, docs, tests, config, and delivery signals
3. **Readiness Judgment**
   - classify the repo as Prototype, MVP, or Handoff-ready
4. **Founder Guidance**
   - return the verdict, top risks, and the next fixes that matter most

This phase framing is intentionally small. It gives the product a stronger autonomous shape without turning it into a sprawling multi-stage platform.

### Optional autonomous follow-up loop

To make the product feel more agentic over time, the same submitted repository can be re-checked on a daily cadence.

Daily follow-up loop:
1. re-open the submitted repository
2. run **Signal Inspection** again
3. run **Readiness Judgment** again
4. run **Founder Guidance** again
5. compare the latest result with the previous report
6. notify the founder if:
   - readiness improved
   - key blockers were removed
   - there is still no meaningful progress on the recommended fixes
7. stop the daily loop once the repository reaches the target confidence / readiness state

Suggested stop condition for hackathon framing:
- stop when the repo is already at the desired maturity target and the confidence is strong enough for the founder's goal
- example: the repo reaches **Handoff-ready** with **High confidence**
- or stop earlier if the founder only cares about becoming **demo-safe** or reaching **MVP**

This makes the agent feel like an active follow-up partner, not just a one-time evaluator.

---

## Solution statement

Repo Readiness Agent turns a GitHub repository into a clear, actionable readiness assessment for solo founders.

Instead of showing only technical warnings, it tells the founder what stage the repo is in, why, and what to fix before launch or handoff.

---

## Hackathon judging highlights

### Autonomous

The agent independently:
- accepts a GitHub repository as input
- decides what repository signals matter
- inspects relevant files, project structure, and delivery signals
- runs supporting analysis when applicable
- synthesizes a maturity judgment
- prioritizes the next actions without step-by-step user direction

For presentation, the autonomy should be explained as a complete decision loop:
1. **Observe** -> ingest repo URL and inspect the repository
2. **Interpret** -> determine which engineering signals are meaningful
3. **Judge** -> classify the repo as Prototype, MVP, or Handoff-ready
4. **Recommend** -> produce the top risks and the next fixes

The important point is that the user does not need to manually tell the system which folders to read, which checks to run, or how to interpret the findings. The agent performs the judgment workflow end-to-end.

### Creativity

The creative leap is not "another code quality checker".

It may reuse lower-level analyzers such as `code-quality-check`, but the product value stays at the repo-readiness decision layer.

It reframes repository analysis into a **founder decision-support system**.

The product answers a founder question in plain language:
- Is this still a Prototype?
- Is it already an MVP?
- Is it ready for handoff?

### Clarity

The product is intentionally narrow and easy to explain.

- **Who is it for?** Solo founders
- **What problem does it solve?** Repo readiness uncertainty
- **What does the agent do?** Reviews a repo and classifies its maturity
- **What is the solution?** A clear readiness verdict with top next fixes

---

## Founder-facing output contract

Every visible report should try to answer these questions clearly:
1. What stage is this repo in?
2. Can I demo, launch, or hand this off yet?
3. What are the top risks?
4. What are the next 3 fixes that matter most?

### Preferred founder-facing gates

The report should feel like a founder decision artifact, not just a technical scan.

Preferred visible gates:
- **Demo-safe?** yes / not yet
- **Launch-ready?** yes / not yet
- **Handoff-ready?** yes / not yet
- **Confidence:** Low / Medium / High

These gates do not replace the maturity stage. They enrich it by making the output easier to act on.

### Preferred stage labels for hackathon scope

- Prototype
- MVP
- Handoff-ready

Note: existing implementation may still use `Production-capable` internally or in broader docs. For hackathon-facing presentation, prefer the founder-friendly stage language above.

---

## Scope constraints for the hackathon version

### In scope

- GitHub URL input
- autonomous repo inspection
- founder-friendly readiness classification
- verdict
- top risks
- top 3 next fixes
- explainable scoring basis

### Out of scope

- enterprise compliance workflows
- full security auditing
- autofix / code rewriting
- PR bot behavior
- coverage-grade testing analytics
- deep language-complete static analysis for all ecosystems
- broad persona switching
- generic engineering management dashboards

---

## Product framing rules

### Say this

- repo readiness agent for solo founders
- founder-facing repo maturity assessment
- prototype / MVP / handoff-ready classification
- top fixes before launch or handoff

### Avoid this

- universal code quality platform
- AI for all developers
- enterprise SDLC intelligence suite
- full autonomous software auditor
- generic GitHub analysis assistant

These broader framings weaken clarity and reduce the niche strength of the product.

---

## Demo spine

### 30-second version

1. founder pastes GitHub URL
2. agent inspects the repo
3. result appears:
   - Stage: MVP
   - Verdict: safe to demo, not ready for handoff
   - Top fixes: add CI, improve critical-path tests, document env setup
4. founder immediately knows what to do next

### Demo message

"This helps solo founders understand whether the repo they built quickly is actually ready to ship or hand off."

---

## Decision filter for future changes

Before adding a feature, ask:

1. Does this help a solo founder make a better launch/handoff decision?
2. Does this strengthen autonomy, clarity, or founder usefulness?
3. Does this keep the product narrow and demoable?
4. Would this still make sense if the output had to fit in a 30-second demo?

If the answer is mostly no, do not prioritize it for the hackathon scope.

---

## Submission-ready short form

For the copy-paste submission artifact, see `docs/hackathon_submission.md`.


**Product:** Repo Readiness Agent

**User:** Solo founders

**Problem:** They can build quickly, but cannot objectively judge whether their repository is ready to demo, launch, or hand off.

**Agent action:** The agent autonomously reviews a GitHub repo and classifies its engineering maturity.

**Solution:** A clear stage verdict with top risks and the next fixes that matter most.
