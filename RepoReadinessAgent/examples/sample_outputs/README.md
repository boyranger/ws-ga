# Sample Outputs

This directory stores example Repo Readiness Agent outputs.

Current contents:
- `qris_payment_bot_report.txt` - sample product-layer text output generated from the current CLI
- `qris_payment_bot_report.json` - sample product-layer JSON output generated from the current CLI
- `qris_payment_bot_followup_before.json` - example earlier-state report for a follow-up scenario
- `qris_payment_bot_followup_after.json` - example later-state report for a follow-up scenario
- `qris_payment_bot_followup_result.json` - example comparison result produced by the product-layer follow-up logic
- `build_followup_example.py` - small helper that generates the follow-up comparison artifact

Suggested future additions:
- multiple repo-stage examples (Prototype / MVP / Handoff-ready)

The purpose is to make the repo easier to demo and easier to understand without requiring a live run every time.
