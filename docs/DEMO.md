# Record a 3–5 minute demo

Use real Kane output for the hackathon recording. Do not substitute unit-test
fixtures, a browser-only test or authentication failure for the Kane demonstration.
The deliberately incorrect first objective is an injected procedure defect; say
so. The application itself is functioning.

## Preparation

1. Install SkillForge, Kane CLI 0.10.9 and Chrome on Linux/macOS. Sign in to
   TestMu. Run `skillforge doctor`, `kane-cli whoami` and `kane-cli balance`.
2. Register for the event with the same email as your TestMu account.
3. Use a fresh registry by setting `SKILLFORGE_HOME` to a new empty directory.
   Run `python3 demo/serve.py` in a second terminal.
4. Keep real customer information out of the fixture and recording.

## Recording outline

**0:00–0:30 — Problem and artifact**

“A coding agent can write a procedure once. Can it keep that capability without
trusting its own claim that it worked? SkillForge creates actual agent skills,
and Kane controls admission and every later reuse.”

Show the generator's SKILL.md. Explain that the generated package will be
SKILL.md + objective + manifest + trusted script, not a new browser app.

**0:30–1:15 — Freeze and catch the mistake**

Show `examples/ship-order.contract.json` before the procedure. Acceptance says
the order must be shipped, with an activity-log confirmation.

```sh
skillforge create examples/ship-order.contract.json
skillforge author dispatch-ship-order --objective examples/wrong-objective.md
skillforge verify dispatch-ship-order --values examples/first-request.json
skillforge find shipping
```

Show that the action records payment but the independent analyzer rejects
shipment. Discovery remains empty. If the action never ran due to infrastructure,
stop and fix that; it is not a successful bug-catching demonstration.

**1:15–2:30 — Give evidence to the coding agent**

```sh
skillforge repair dispatch-ship-order
```

Ask your coding agent: “Read this failure context. Preserve the frozen contract.
Repair the procedure, then verify.” Show the actual edit and the rerun. The
example corrected objective is available if doing a manual walkthrough, but
identify that version as a scripted correction, not an autonomous agent repair.

Show the passing action **and** analyzer conditions, then the generated package.

**2:30–3:30 — Fresh-session reuse**

Open a new terminal or agent session in the same project:

```sh
skillforge find shipping
skillforge run dispatch-ship-order --values examples/reuse-request.json
```

The request uses ORD-105 rather than ORD-104. Show a new evidence attempt, a new
Chrome profile and a new analyzer pass. Do not merely print the old pass.

**3:30–4:00 — Limits**

Browser-task skills only. Fresh Chrome profile isolation; optional container for
host filesystem isolation. Frozen acceptance helps, but assertions remain AI
judgments. A failed reuse revokes discovery. The caller needs specific authority
for real external mutations. No general self-improvement claim.

## Evidence to retain

The generated skill directory, frozen contract, result.json for failure/pass/
reuse, both phases' stdout/stderr and Kane's evidence pack if available. Raw
evidence stays gitignored; review and redact anything you deliberately publish.
The browser CI screenshots show only the fixture, not a Kane run.
