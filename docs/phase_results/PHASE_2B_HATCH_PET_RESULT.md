# Phase Result

## Phase

Phase 2B — Retry Camino A (Hermes's native AI generation pipeline,
`hatch_pet()`) with real OpenRouter budget, now that the user funded the
account. This is the **Path A pivot** the user asked for after reviewing
Phase 3/4's deterministic `_vary()` sine-wave bob/tilt/scale transform of a
single static keyframe (`docs/phase_results/PHASE_4_RESULT.md`) and judging
it does not read as real animation. The goal was a REAL multi-pose
animation strip per state, grounded on `assets/reference/jorgito_canonical.png`,
generated end-to-end by `agent.pet.generate.hatch_pet()`.

**This does not replace Phase 2's original decision or Phase 3/4's work.**
`docs/phase_results/PHASE_2_RESULT.md` and `PHASE_4_RESULT.md` are
unmodified. Whether to actually switch to Path A is still the user's call,
and — see Status below — there is nothing to gate yet: the hatch did not
produce an installable atlas.

## Status

**FAIL / BLOCKED.** `hatch_pet()` raised `GenerationError` after generating
8 of 9 rows (`running-left` is always mirrored, never generated directly):
only 4 of 8 generated rows produced a usable strip, and `running-right` —
one of the three hard-required states (`idle`, `running-right`, `waving`,
per `orchestrate.py`'s `_REQUIRED_STATES`) — was not among them, so the call
failed before reaching `atlas.compose_atlas()` / `store.register_local_pet()`.
**No atlas was composed, no pet was installed** (isolated profile's
`pets/jorgito-hatch/` was never created — verified below). There is nothing
to validate, install, render, or build a contact sheet for. Per the task's
explicit instruction, this was **not retried in a loop**; it is reported as
BLOCKED with the exact error and balance delta.

## What was run

`scripts/hatch_pet_run.py` (new, this phase):

- Sets `HERMES_HOME=/home/chegusan/.hermes-jorgito-test` (isolated profile
  only) and loads its `.env` via Hermes's own
  `hermes_cli.env_loader.load_hermes_dotenv()` — not a hand-rolled shell
  export — so `OPENROUTER_API_KEY` / `OPENROUTER_IMAGE_MODEL=google/gemini-3-pro-image`
  are picked up exactly the way the real CLI picks them up.
- Refuses to run if `HERMES_HOME` resolves to the real `~/.hermes`.
- Checks the free `GET https://openrouter.ai/api/v1/credits` endpoint
  immediately before and after the call (no cost).
- Resolves the provider via `imagegen.resolve_provider(require_references=True, prefer="openrouter")`
  and passes the resulting `SpriteProvider` explicitly to `hatch_pet()`.
- Calls `hatch_pet(base_image="assets/reference/jorgito_canonical.png", slug="jorgito-hatch", display_name="Jorgito", concept="a small friendly Petdex-style pixel-art dragon mascot, crimson/burgundy body, large green eyes, yellow belly/neck plates and wing membranes, red wings, curled tail", provider=sprite, on_progress=...)`.
  Used slug **`jorgito-hatch`**, not `jorgito`, so it would not collide with
  the existing Phase 4 deterministic-transform pet already installed under
  `jorgito` in the same isolated profile.
- Writes a JSON report (`assets/keyframes/hatch_pet_report.json`, gitignored
  — see Files changed) with balances, per-event progress log, and the exact
  error.

```text
$ /home/chegusan/.hermes/hermes-agent/venv/bin/python3 scripts/hatch_pet_run.py
loaded env from: ['/home/chegusan/.hermes-jorgito-test/.env']
balance before: $10.6857
resolved provider: name='openrouter' supports_references=True
...
FAIL (GenerationError): missing required animation row(s): running-right
balance after: $8.2838
spent: $2.4019
```

## Per-state result (from Hermes's own log output + progress callback)

`hatch_pet()` generates all 8 non-mirrored rows concurrently (4 workers),
each with up to 3 internal attempts (`_ROW_GEN_ATTEMPTS=3`); a row succeeds
on whichever attempt first slices cleanly.

| State           | Attempts | Outcome | Failure reason (last attempt) |
|------------------|:-:|---------|--------------------------------|
| `waving`         | 1 | **usable** | — (clean on first attempt) |
| `idle`           | 2 | **usable** | attempt 1: could not segment 6 padded sprites from strip |
| `jumping`        | 3 | **usable** | attempts 1–2: could not segment 5 padded sprites from strip |
| `waiting`        | 3 | **usable** | attempts 1–2: could not segment 6 padded sprites from strip |
| `running-right`  | 3 | **gave up** | frame 5 contains multiple separated subjects |
| `failed`         | 3 | **gave up** | frame 3 contains multiple separated subjects |
| `running`        | 3 | **gave up** | frame 5 contains multiple separated subjects |
| `review`         | 3 | **gave up** | frame 3 contains multiple separated subjects |
| `running-left`   | — | **not attempted** | mirror source (`running-right`) never produced a usable strip |

4 of 9 rows usable (`idle`, `waving`, `jumping`, `waiting`) — below both hard
gates: `running-right` is a required state (`_REQUIRED_STATES`), and even
ignoring that, 4 filled states is below `_MIN_FILLED_STATES=6`. The
`GenerationError` message names the required-state gate specifically because
that check runs first.

The two distinct failure signatures — `could not segment N padded sprites
from strip` (early attempts, strict `components` slicing) and `frame N
contains multiple separated subjects` (final attempt, lenient `auto`
slicing) — both point the same direction: the model-generated multi-pose
row strips did not consistently produce clean, single-subject, evenly
gapped poses for `hermes`'s frame-extraction step, worse for the
higher-motion states (`running-right`/`running`, wide limb spread) and the
UI-reaction states (`failed`/`review`, which likely include extra
compositional elements) than for the more contained ones (`idle`/`waving`/
`waiting`/`jumping`).

## Cost (real money, OpenRouter, `google/gemini-3-pro-image`)

| | |
|---|---|
| Balance before | $10.6857 |
| Balance after  | $8.2838 |
| **Spent this run** | **$2.4019** |
| Wall-clock | 192.7s |

Checked via the free `GET /api/v1/credits` endpoint, once before and once
after, per the task's instruction (no extra checks were made).

## Safety verification

- `HERMES_HOME` used throughout: `/home/chegusan/.hermes-jorgito-test` only.
- Real `~/.hermes/config.yaml`: md5 `66684dd3b378e4584ab08ab097024ed4`,
  mtime `1786786713` — **identical before and after** this run.
- Real `~/.hermes/pets/`: empty before and after this run.
- Isolated profile's `pets/` after the failed run: unchanged (`boba`,
  `jorgito`, `jorgito-test` — the same three pre-existing entries; no
  `jorgito-hatch` directory, confirming `store.register_local_pet()` was
  never reached).

## Files changed

- `scripts/hatch_pet_run.py` (new) — the orchestration script described
  above.
- `docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md` (this file).
- `docs/08_PROJECT_STATE.md` (updated — see that file for the current
  summary).
- `assets/keyframes/hatch_pet_report.json` — raw JSON report from this run
  (balances, full progress log, error). Kept as evidence for this doc;
  not meant to be regenerated/diffed on every run, so it is not
  authoritative on its own — this document is.

## Problems

- **Blocking for this phase's goal:** `hatch_pet()`'s frame-slicing step
  (`atlas.extract_strip_frames(..., method="components"|"auto")`) is not
  reliable enough yet against `google/gemini-3-pro-image` row strips for
  this character/prompt combination — 4/8 generated rows failed all 3
  attempts. This is a pipeline/model-fit problem, not an environment,
  credentials, or budget problem (the isolated profile, provider
  resolution, and `.env` loading all worked exactly as designed).
- Real money was spent (`$2.4019`) on a run that produced no usable atlas.
  Flagging explicitly per the task's cost-discipline instruction, not
  retried further without the user's go-ahead.

## Decision

**BLOCKED** — do not retry automatically. Options for the user to choose
between, none started without explicit go-ahead given the real cost of
each attempt:

1. Retry `hatch_pet()` as-is (same prompt/model) — outcome is
   attempt-dependent per the log above; not guaranteed better next time,
   same ~$2.40/run order of cost.
2. Try a different `OPENROUTER_IMAGE_MODEL` (something with more reliable
   multi-pose-strip generation / gutter discipline) before re-spending on
   the same model.
3. Abandon Path A for this MVP and keep Phase 3/4's Camino B (deterministic
   `_vary()` transform) as-is, accepting its known "not real animation"
   limitation, and revisit Path A later as a post-MVP polish item.
4. Adjust the prompt (`agent.pet.generate.prompts.build_row_prompt`) to more
   strongly enforce clean per-pose gutters, if the user wants one more
   attempt at Path A before falling back to option 3.

## Next phase/task

None dispatched automatically — this phase surfaces the result and cost for
the user to decide among the options above. No visual gate to run (nothing
was produced to gate).
