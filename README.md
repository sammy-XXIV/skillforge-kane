# SkillForge / Kane

**Your agent needs a capability. It builds a skill. Kane decides whether to keep it.**

[![Tests](https://github.com/sammy-XXIV/skillforge-kane/actions/workflows/ci.yml/badge.svg)](https://github.com/sammy-XXIV/skillforge-kane/actions/workflows/ci.yml)

SkillForge is an **agent skill that creates other agent skills** for browser
tasks. When a capability is missing, the coding agent creates a reusable skill,
Kane executes it, and an independent Kane analysis checks the result. Passing
skills enter the registry. Every later reuse gets verified again.

Each generated skill contains `SKILL.md`, a parameterized procedure, an input
manifest, a script entrypoint and verification evidence.

```text
Find a saved skill → build if missing → Kane executes → Kane verifies
                                             ↑               ↓
                                      repair from evidence   save on pass
                                                             ↓
                                                   reuse and verify again
```

## Proven with real Kane runs

The complete **failure → correction → pass → fresh-process reuse** walkthrough
passed on November 26, 2026, using Kane CLI 0.10.9 and Chrome on Linux.

| Task | What happened | Registry result |
| --- | --- | --- |
| Incorrect procedure, ORD-104 | Marked paid; independent checks caught that shipment was incomplete | Rejected |
| Corrected procedure, ORD-104 | Shipment and activity-log checks passed | Skill saved |
| Fresh-process reuse, ORD-105 | The same saved skill passed on a different order | Re-verified |

[View the successful run and download its evidence](https://github.com/sammy-XXIV/skillforge-kane/actions/runs/45825042502)
· [Verification summary](docs/live-verification.json)
· [Technical verification record](docs/VERIFICATION.md)

The automated suite also passes **37 Python checks and 3 browser tests** in Linux
CI, including registry integrity, failure revocation and Chrome/CDP lifecycle.

## How it works

1. **Discover.** Search the registry for a verified skill matching the task.
2. **Freeze.** Define the target, inputs and observable acceptance criteria before authoring.
3. **Forge.** The coding agent writes the procedure; SkillForge generates its skill package.
4. **Execute and verify.** Kane performs the task. A separate assertion-only call checks every frozen condition on the same page.
5. **Repair.** Failure evidence returns to the coding agent, which revises the procedure and retries against the unchanged criteria.
6. **Keep and reuse.** Passing packages become discoverable. Every reuse executes and verifies again.

Package and evidence hashes bind verification to the exact saved skill. Editing
it invalidates the previous pass. A failed reuse removes it from discovery.

## Install

Requires **Linux or macOS, Python 3.11+, Node 18+, Google Chrome and a TestMu login**.

```sh
git clone https://github.com/sammy-XXIV/skillforge-kane.git
cd skillforge-kane
python3 -m pip install -e .
npm install -g @testmuai/kane-cli@0.10.9
kane-cli login --oauth
skillforge doctor
```

Copy [skills/skillforge-kane](skills/skillforge-kane) into your agent's skills
directory, such as `~/.codex/skills/skillforge-kane`, and start a fresh session.
Keep the CLI installed and run from the project whose registry you want to use.

> Use SkillForge. Ship order ORD-104 in the local Dispatch app. Look for a saved
> skill first; if none exists, create and verify one. Preserve payment status.

The calling coding agent authors and repairs procedures using its existing model.
SkillForge supplies the packaging, execution, evidence and admission gate.

## Try the walkthrough

Dispatch is the included disposable order desk. Start it in a separate terminal:

```sh
python3 demo/serve.py
```

Freeze acceptance and generate the intentionally incorrect candidate:

```sh
skillforge create examples/ship-order.contract.json
skillforge author dispatch-ship-order --objective examples/wrong-objective.md
skillforge verify dispatch-ship-order --values examples/first-request.json
skillforge repair dispatch-ship-order
```

Kane executes the payment procedure, then independent checks reject the missing
shipment. The repair command returns the frozen contract and failure evidence.

This repeatable walkthrough includes a corrected procedure. During normal agent
use, the calling agent writes its revision from that failure context.

```sh
skillforge author dispatch-ship-order --objective examples/ship-order.objective.md
skillforge verify dispatch-ship-order --values examples/first-request.json
skillforge find shipping
```

Open a fresh terminal or agent session in the same project and reuse it:

```sh
skillforge run dispatch-ship-order --values examples/reuse-request.json
```

The second request uses ORD-105, starts a fresh browser, and runs both Kane phases
again. See [the recording guide](docs/DEMO.md) for the full demo sequence.

## The generated package

```text
.skillforge/
├── contracts/<id>.json          # frozen target, inputs and acceptance criteria
├── skills/<id>/
│   ├── SKILL.md                 # agent instructions
│   ├── manifest.json            # inputs, criteria and contract hash
│   ├── objective.md             # reusable Kane procedure
│   └── scripts/run.py           # SkillForge entrypoint
├── evidence/<id>/<attempt>/     # request, action/analysis logs and result
└── state/<id>.json              # admission state and integrity hashes
```

Runtime evidence stays private and gitignored by default. Discovery uses
`find` or `list`; inspect candidates and failed attempts with `list --all`.
Three consecutive failures pause execution for inspection.

| Command | Purpose |
| --- | --- |
| `create` | Freeze a task contract |
| `author` | Generate or revise its candidate skill |
| `verify` | Verify a candidate for admission |
| `find` / `list` | Discover currently verified skills |
| `run` | Execute and re-verify a saved skill |
| `repair` | Return failure context to the coding agent |
| `doctor` | Check local prerequisites |

Set `SKILLFORGE_HOME` to choose a registry directory, `KANE_BIN` for a custom Kane
executable, or `CHROME_BIN` for a custom Chrome path. Without installing the CLI,
use `python3 /path/to/skillforge-kane/forge.py` in its place.

## Execution and development

Runs use fresh Chrome profiles and a trusted script entrypoint. The optional
container, authorization boundaries and network behavior are documented in
[Execution boundaries](docs/ISOLATION.md). Login-required target apps need session
setup; Dispatch is ready to use without an application login.

```sh
python3 -m unittest discover -s tests -v
npm ci
npx playwright install --with-deps chromium
npm run test:browser
```

The manually triggered [real Kane workflow](https://github.com/sammy-XXIV/skillforge-kane/actions/workflows/kane-live.yml)
uses TestMu credentials and Kane credits. Configure `LT_USERNAME` and
`LT_ACCESS_KEY` as repository secrets, or securely supply a temporary
`KANE_OAUTH_PROFILE`. Ordinary CI runs the automated tests without Kane credits.

Official docs: [agent output](https://www.testmuai.com/docs/kane-cli-agent-mode)
· [CLI reference](https://www.testmuai.com/docs/kane-cli-cli-reference)
· [authentication](https://www.testmuai.com/docs/kane-cli-authentication).

Built with Codex for the [KaneCLI Online Hackathon](https://www.kaneclihack.sh/).
[Submission guide](docs/SUBMISSION.md). MIT licensed.
