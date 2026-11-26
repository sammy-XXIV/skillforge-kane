# Hackathon delivery status

Project: **SkillForge / Kane**

Repository: https://github.com/sammy-XXIV/skillforge-kane

## Description draft

SkillForge is an agent skill that creates reusable browser-task agent skills when
a capability is missing. Before authoring, the coding agent freezes the task's
target, input constraints and acceptance conditions. It writes a procedure and
SkillForge generates SKILL.md, a manifest and a trusted script entrypoint.

Kane executes the procedure in a disposable Chrome profile. A separate Kane
analyzer invocation inspects the same resulting page. The registry admits the
skill only after successful process exits, complete versioned result streams and
explicitly true verdicts for every frozen condition. Failures give the coding
agent a repair brief. Later reuse executes and verifies again; a failed reuse
revokes discovery. Evidence is bound to the exact package and contract by hashes.

The project was built with Codex. The included demonstration uses a local order
desk: an injected incorrect procedure marks an order paid instead of shipped,
unchanged acceptance catches it, the procedure is corrected, and a fresh session
reuses the resulting shipping skill for a different order.

## Before submitting

- Confirm event registration and TestMu signup use the same email; claim credits.
- Done: real Kane failure → corrected pass → fresh-session reuse:
  https://github.com/sammy-XXIV/skillforge-kane/actions/runs/45825042502
- If showing agent repair, record the agent making the edit from actual failure
  context; the CI example uses a supplied corrected procedure.
- Record and upload a 3–5 minute YouTube demo.
- Publish two separate public project posts; drafts are below.
- Submit the public repository URL and YouTube URL using the event's form.
- Include working setup instructions and recorded fallback evidence for judges.
- Stop pushing before the published deadline: November 26, 11:59 PM IST
  (7:29 PM Lagos), unless the organizer explicitly changes it.

The code being public and the real Kane run passing is not a submitted hackathon
entry. No uploaded YouTube demo, public announcement or submitted entry is
claimed here. The owner completed TestMu OAuth login; the live run used that
account with a temporary access token, and the repository secret was removed.

## Announcement drafts — not posted

The real Kane demo has passed. These drafts have not been posted.

**Post 1**

I built SkillForge for the Kane CLI hackathon: an agent skill that creates other
agent skills. It freezes acceptance criteria before authoring, lets Kane execute
and independently inspect the result, and saves the skill only after it passes.
Every reuse gets verified again. Repo: https://github.com/sammy-XXIV/skillforge-kane

**Post 2**

The useful part of an agent writing a skill isn't the file—it's knowing when to
trust it again. SkillForge keeps evidence with each generated browser-task skill.
Failed reuse revokes it; the coding agent gets the unchanged contract and failure
context for repair. Here's the actual failure → repair → reuse demo: [YouTube URL]

## Remaining account-dependent work

Confirm event registration, record the demo, upload it to YouTube, publish two
announcements and submit the final form. TestMu login and the real Linux Kane
run are complete. A future rerun needs a valid login or repository credentials;
the temporary access-token secret was deliberately removed after this run.
