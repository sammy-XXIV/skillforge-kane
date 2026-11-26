# SkillForge / Kane

**Your agent needs a capability. It builds a skill. Kane decides whether to keep it.**

[![Tests](https://github.com/sammy-XXIV/skillforge-kane/actions/workflows/ci.yml/badge.svg)](https://github.com/sammy-XXIV/skillforge-kane/actions/workflows/ci.yml)

SkillForge is an **agent skill that creates other agent skills** for browser
tasks. The result is a real `SKILL.md` package with a reusable procedure, typed
inputs, a script entrypoint, frozen acceptance criteria and verification evidence.
It does not generate browser mini apps. The included Dispatch app is just a
disposable target for the demonstration.

```text
Missing capability → freeze acceptance → generate skill → Kane executes
                                                          ↓
                  repair ← failure evidence ← Kane analyzes the result
                     ↓                                    ↓ all true
                  retry                             reusable registry
                                                          ↓ next request
                                                   execute + verify again
```

Kane is the runtime and admission gate. A passing action alone is insufficient:
a separate assertion-only call inspects the **same browser page** against every
frozen condition. A failed reuse removes the skill from discovery immediately.

## Verification status

The automated suite covers registry admission/revocation, frozen contracts,
package/evidence tampering, NDJSON parsing, child-process timeouts, argument
safety, CLI behavior and the demo UI. Unit-test fixtures are explicitly labeled;
they are **not real Kane verification**.

Kane CLI 0.10.9 was installed and a real first run attempted on the development
device. It refused because there is no TestMu login. Android/Termux also has no
supported desktop Chrome here. **No successful live Kane run is claimed.**
The manual [Real Kane verification workflow](../../actions/workflows/kane-live.yml)
runs the complete failure → correction → pass → fresh-process reuse demonstration
once `LT_USERNAME` and `LT_ACCESS_KEY` repository secrets are configured. Its
correction is a supplied procedure, not a claim of an autonomous LLM repair.

## Install

Use Linux or macOS with **Python 3.11+**, Node 18+, and Google Chrome installed.
The registry uses POSIX file locking. Windows and Android are not runtime targets.

```sh
git clone https://github.com/sammy-XXIV/skillforge-kane.git
cd skillforge-kane
python3 -m pip install -e .
npm install -g @testmuai/kane-cli@0.10.9
kane-cli login --oauth
skillforge doctor
```

No Python runtime dependencies. Without installation, replace `skillforge` with
`python3 /absolute/path/to/skillforge-kane/forge.py`. Optional environment settings:

| Setting | Purpose |
| --- | --- |
| `SKILLFORGE_HOME` | Registry directory; default `.skillforge` under the current working directory |
| `KANE_BIN` | Kane executable path; default `kane-cli` on PATH |
| `CHROME_BIN` | Chrome executable path, if it cannot be found automatically |

Copy [skills/skillforge-kane](skills/skillforge-kane) into your agent's skills
directory (for Codex, `~/.codex/skills/skillforge-kane`). The agent still needs
the SkillForge executable and access to its registry. Start a new agent session
so it discovers the skill. Example prompt:

> Use SkillForge. I need to ship order ORD-104 in the local Dispatch app. Look
> for a matching skill first; if none exists, create and verify one. Do not
> change payment status.

The coding agent authors and repairs the plain-English procedure. SkillForge
does not secretly call another model or require a separate LLM API key.

## Run the demonstration

Start the fixture in a separate terminal:

```sh
python3 demo/serve.py
```

Freeze the task, then generate an intentionally incorrect skill:

```sh
skillforge create examples/ship-order.contract.json
skillforge author dispatch-ship-order --objective examples/wrong-objective.md
skillforge verify dispatch-ship-order --values examples/first-request.json
```

The incorrect procedure records payment. The acceptance contract requires
shipment. **A functioning Kane connection should execute the procedure but
reject the final result.** A login refusal is not the intended demonstration.

Feed the actual failure back to your coding agent:

```sh
skillforge repair dispatch-ship-order
```

The agent reads the frozen contract and the action/analyzer evidence, changes
the procedure to confirm shipment, and reruns verification. For a repeatable
manual demonstration, the repository includes a corrected procedure:

```sh
skillforge author dispatch-ship-order --objective examples/ship-order.objective.md
skillforge verify dispatch-ship-order --values examples/first-request.json
skillforge find shipping
```

Open a **fresh terminal or agent session** in the same project. Reuse the saved
skill on a different order:

```sh
skillforge run dispatch-ship-order --values examples/reuse-request.json
```

This launches a new private browser and runs both Kane phases again. No cached
pass is reused. See [docs/DEMO.md](docs/DEMO.md) for the recording script.

## What is actually saved?

```text
.skillforge/                      # private runtime data; gitignored
├── contracts/<id>.json           # frozen task and acceptance conditions
├── skills/<id>/
│   ├── SKILL.md                  # agent instructions and when to use them
│   ├── manifest.json             # task, target, input constraints, contract hash
│   ├── objective.md              # reusable Kane procedure
│   └── scripts/run.py            # trusted wrapper calling SkillForge
├── evidence/<id>/<attempt>/      # request, action/analyzer logs, result
└── state/<id>.json               # eligibility, failures, hashes, evidence link
```

Candidate files exist in the skills directory, but only the gated `find` / `list`
interface exposes eligible skills. Packages, contracts and the saved result are
hashed. Any changed or missing artifact invalidates discovery. The runtime does
not execute arbitrary generated Python or shell code. To move a registry, retain
its evidence and update paths; moving a folder alone does not confer a pass.

`verify` admits candidates. `run` requires a current verified package and then
re-verifies it. `repair` prints context, not an automatic fix. `list --all` shows
drafts, candidates, failures and stale packages. Three consecutive failures stop
further execution for that contract; inspect the failure with the user rather
than starting an unlimited repair loop. There is no bypass/force-pass option.

Exit codes: **0** success, **1** attempted verification did not pass, **2**
usage/configuration refusal, **130** interrupted. A failed action may have had
side effects; inspect current state before trying it again.

## Isolation and limits

- Each invocation owns a new Chrome profile, loopback CDP endpoint and process
  group, cleaned up afterward. It does not attach to your everyday browser.
- The demo server exposes only three public assets. It cannot serve contracts,
  registry files or credentials. Its application has no network requests.
- **A browser profile is not an OS or network security sandbox.** The optional
  [container](docs/ISOLATION.md) limits host filesystem access. Network access
  remains necessary for Kane. The objective's origin restriction and final URL
  check are not an enforced browser egress allowlist.
- This version targets browser-task skills. It does not verify arbitrary local
  scripts or claim general agent self-improvement. Frozen tests reduce moving
  goalposts; Kane's AI assertions are not a mathematical proof of correctness.
- Reusing skills performs their actions. Target only authorized apps. Fresh
  profiles mean login-required tasks need additional explicit session setup;
  the supplied demo requires none.
- Evidence may contain page data. It stays private and gitignored by default.
  GitHub Actions artifacts are visible to people with repository access; only
  the synthetic fixture belongs in the supplied live workflow.
- Hashes protect against accidental changes, not a malicious registry owner.
  A verifier binary or registry that the owner deliberately forges is outside
  the trust boundary.

## Development

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q skillforge forge.py demo/serve.py
npm ci
npx playwright install --with-deps chromium
npm run test:browser
```

Python checks run locally and in Linux CI; browser checks run in Linux CI.
Neither command spends Kane credits. The opt-in live workflow requires a real
account and uses its Kane credits. No real-Kane workflow is triggered by a push.

Official references: [Kane agent output](https://www.testmuai.com/docs/kane-cli-agent-mode),
[CLI and analyzer flags](https://www.testmuai.com/docs/kane-cli-cli-reference),
[authentication](https://www.testmuai.com/docs/kane-cli-authentication).

Built for the [KaneCLI Online Hackathon](https://www.kaneclihack.sh/). See
[docs/SUBMISSION.md](docs/SUBMISSION.md) for status and draft submission copy.
MIT licensed.
