# Verification record

## Initial implementation

- 30 Python tests passed locally on Python 3.14 / Android Termux.
- [Initial Linux CI](https://github.com/sammy-XXIV/skillforge-kane/actions/runs/45809860189)
  passed Python 3.11 and 3.13, package installation, and three real Chromium UI
  checks. Desktop and mobile screenshots were downloaded and visually inspected.
- Those checks validate the registry and fixture. They do not constitute a
  successful Kane run.

## Independent review and corrections

A separate reviewer inspected the source and reproduced four material findings:

1. A subprocess leader could exit while descendants held output pipes, causing
   an unbounded drain after timeout. A regression reproduced a four-second wait
   for a 0.1-second timeout. The implementation now kills the owned process group
   even after leader exit and bounds draining.
2. Interrupted verification lost result.json, breaking repair context and not
   consuming its retry budget. Interruptions now preserve a failed result and
   consume the attempt; abrupt kills retain an inspectable incomplete context.
3. Request and separate phase logs were not integrity-bound. Saved results now
   contain artifact hashes; modified or missing request/log files revoke
   discovery along with modified result/package/contract files.
4. A numeric URL in an otherwise valid JSON contract raised AttributeError
   instead of returning a structured refusal. Schema validation now rejects it.

Each reproduced issue had a failing regression test before its correction.
The reviewer did not assert that equal CDP endpoints alone proved page identity.
The adapter additionally checks a single final task page, closes only unused
blank tabs and confirms the page id and URL remain identical after analysis.
A real Chrome integration test exercises target selection and shutdown in Linux
CI; it is skipped on devices without desktop Chrome.

No findings were silently accepted as working behavior. The intentionally
remaining limits are in README.md: browser-task scope, AI assertion uncertainty,
no enforced network egress boundary, no arbitrary generated script execution,
and no successful live Kane evidence without a TestMu account.

## Real Kane preflight

Kane CLI 0.10.9 was installed under `~/.local/kane` on the development device.
`kane-cli whoami` reported no active authentication. A real `kane-cli run` emitted
its actual versioned stream start and refused with “Not authenticated.” This is
an observed blocker, not a passing task.

The production CLI contains no mock/fake success mode. Unit tests use explicitly
labeled in-process verdict fixtures and a subprocess fixture to exercise parsing;
neither is exposed as a production command or represented as Kane evidence.
