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

---

## Addendum — single-pose pilot (`review` state only)

**Status: PILOT DONE, awaiting human visual gate.** Not a retry of option
1/2/4 above — a different mechanism entirely, generating ONE centered pose
per API call instead of a multi-pose row strip, to test whether that
sidesteps the segmentation failures this phase hit (`review` was one of the
4 states that failed all 3 row-strip attempts: "frame 3 contains multiple
separated subjects").

### Why this is possible without more `hatch_pet()` spend

`imagegen.generate(prompt, n=1, reference_images=[...], provider=...)`
(`agent/pet/generate/imagegen.py`) already does single-image-per-call
generation — no strip, no slicing — it's the same primitive
`generate_base_drafts()` uses in production. `hatch_pet()`'s row-strip
failure is specific to `build_row_prompt()`'s multi-pose-per-call approach,
not to the underlying generation call.

### What was built

- **`scripts/prompts_single_pose.py`** (new) — `build_single_pose_prompt(state,
  concept, style)`. Based directly on Hermes's own
  `agent.pet.generate.prompts.build_row_prompt()` (same identity-grounding
  and chroma-key background framing), with all strip/gutter/spacing/
  multi-frame language removed and a `review`-specific action from this
  project's `docs/09_DECISIONS.md` D-004 ("Jorgito thinking/reading:
  glasses + open book").
  **Deviation from the task as given:** this function was NOT added in place
  to `agent/pet/generate/prompts.py`. That path resolves to
  `/home/chegusan/.hermes/hermes-agent/agent/pet/generate/prompts.py` —
  which is both this task's declared read-only Hermes reference tree *and*
  physically inside the real `~/.hermes/` this project's guardrails say never
  to touch. Editing it in place would violate that guardrail, so the new
  function lives in the Jorgito repo instead, at
  `scripts/prompts_single_pose.py`, and is imported by the pilot script.
  `agent/pet/generate/prompts.py` itself was not modified — confirmed by the
  real-`~/.hermes` md5/mtime check below.
- **`scripts/generate_single_pose.py`** (new) — isolated-profile-only
  (same refusal guard as `scripts/hatch_pet_run.py`), checks OpenRouter
  balance, resolves the OpenRouter provider, builds the prompt above for
  `state="review"`, and makes **exactly one** `imagegen.generate(n=1, ...)`
  call — no retry loop, no provider fallback. Feeds the resulting raw image
  through the same chroma-key + fit-to-cell primitives
  `scripts/keyframe_processing.py` wraps (`atlas.remove_background` /
  `atlas._fit_to_cell`, called directly since the generated file isn't in
  `keyframe_processing.py`'s `raw_dir/{state}.jpeg` layout) to produce a
  normalized 192x208 cell.
- **Branch note:** `scripts/keyframe_processing.py` and
  `assets/keyframes/processed/review.png` (the approved Phase 1 keyframe,
  needed for the side-by-side gate) did not exist on this branch —
  `phase2b-hatch-pet-regen` branches from `master`, and Phase 1/3/4 landed on
  separate never-merged branches (`phase-1-minimal-visual-proof`,
  `phase-3-comfyui-keyframes`, `phase-4-full-atlas`). Both files were pulled
  in unmodified from `phase-4-full-atlas` (`git show
  phase-4-full-atlas:<path>`) rather than reimplemented.

### Result

One API call, `state="review"`. Output:
`assets/keyframes/raw_single_pose/review.png` (raw, 1024x1024) →
`assets/keyframes/processed/review_singlepose_pilot.png` (processed,
192x208 RGBA). Chroma-keyed cleanly, single subject, no segmentation
artifacts — the exact failure mode this pilot targets did not reproduce.
Side-by-side preview for the visual gate:
`assets/keyframes/pilot_review_single_pose_preview.png` (old Phase 1
`review.png` vs. new single-pose pilot, both labeled).

### Cost

| | |
|---|---|
| Balance before | $7.7148 |
| Balance after (settled) | $7.5734 |
| **Spent this pilot** | **$0.1415** |
| Wall-clock | 24.4s |

(OpenRouter's `/credits` usage figure lags the actual charge by roughly a
minute — an immediate post-call check still showed the pre-call total; the
figure above is from a re-check once `total_usage` had moved. Both readings
are in `assets/keyframes/single_pose_pilot_report.json`.) Two orders of
magnitude cheaper than the $2.40 row-strip run, consistent with generating
one pose instead of an up-to-8-pose strip per call.

### Safety verification

- `HERMES_HOME` used throughout: `/home/chegusan/.hermes-jorgito-test` only.
- Real `~/.hermes/config.yaml`: md5 `66684dd3b378e4584ab08ab097024ed4`,
  mtime `1786786713` — **identical before and after** this pilot (same
  values as Phase 2B's original run above).
- Real `~/.hermes/pets/`: empty before and after.
- Isolated profile's `pets/`: unchanged (`boba`, `jorgito`, `jorgito-test`)
  — this pilot called `imagegen.generate()` directly, not `hatch_pet()`, so
  no pet install/registration was attempted or expected.

### Decision

**PILOT ONLY — stopped after `review` as instructed.** Awaiting the user's
visual-gate judgment on
`assets/keyframes/pilot_review_single_pose_preview.png` before running the
remaining 7 states with this approach. If approved, the natural next step is
the same single-pose call for each remaining state, followed by
`atlas.compose_atlas()` to assemble the 9-row sheet (not attempted here —
out of scope for this single-state pilot).

### Files changed (this addendum)

- `scripts/prompts_single_pose.py` (new).
- `scripts/generate_single_pose.py` (new).
- `scripts/keyframe_processing.py` (pulled in from `phase-4-full-atlas`,
  unmodified — this branch didn't have it).
- `assets/keyframes/processed/review.png` (pulled in from
  `phase-4-full-atlas`, unmodified — the approved Phase 1 keyframe, needed
  for the side-by-side gate).
- `assets/keyframes/raw_single_pose/review.png` (new — raw generated image).
- `assets/keyframes/processed/review_singlepose_pilot.png` (new — processed
  cell).
- `assets/keyframes/pilot_review_single_pose_preview.png` (new — the
  side-by-side gate image).
- `assets/keyframes/single_pose_pilot_report.json` (new — balances, prompt,
  paths).
- `docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md` (this addendum).
- `docs/08_PROJECT_STATE.md` (updated).
