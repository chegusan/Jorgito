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

---

## Addendum #2 — real pose variation for `review` (3 poses, ping-pong row)

### Problem with addendum #1

The single-pose pilot above fixed identity/quality (clean single-subject
output, no segmentation artifacts) but the human reviewer flagged a real
gap: `scripts/build_full_atlas.py` (on `phase-4-full-atlas`) only ever had
**one** real source keyframe per state, expanded to a row's full frame count
via `_vary()` — a deterministic sine-driven bob/tilt/scale wobble
(cross-reviewed and fixed in Phase 4, commit `7353a27`, to stop mirrored
columns collapsing to identical hashes). That wobble guarantees frame
hashes aren't byte-identical, but it is not real animation: every column is
the *same pose*, nudged. The human wants genuine pose variation — for
`review`, the book shown at different page-turn positions across the row,
not one photo wobbled.

### Step 1 — real row frame count for `review`

Checked the real Hermes source directly (read-only,
`/home/chegusan/.hermes/hermes-agent/agent/pet/generate/atlas.py`,
`ROW_SPECS`):

```python
ROW_SPECS: list[tuple[str, int, int]] = [
    ("idle", 0, 6),
    ("running-right", 1, 8),
    ("running-left", 2, 8),
    ("waving", 3, 4),
    ("jumping", 4, 5),
    ("failed", 5, 8),
    ("waiting", 6, 6),
    ("running", 7, 6),
    ("review", 8, 6),
]
```

**`review` requires exactly 6 frames.** Cross-checked against the already-
validated Phase 4 full-atlas run on `phase-4-full-atlas`
(`PHASE_4_RESULT.md`'s `validate_atlas()` output lists `review=6` in its
per-state frame-count breakdown) — same number, same source of truth
(`atlas.ROW_SPECS`), not re-derived independently.

### Step 2 — plan: 3 real poses (not 6), chained references, ping-pong row

Per the task's cost discipline (~1 generation attempt per meaningful visual
unit) and "minimal, use judgment": generated **2 additional** real poses on
top of the existing pilot pose, for **3 real poses total** covering a
page-turn progression — book open/starting (pose 1, existing) → mid-page-
turn (pose 2, new) → page turned further along (pose 3, new). 3 was judged
sufficient to read as real progression without tripling cost for a 6-frame
row where the wobble math can still cover the remaining columns.

New `scripts/generate_review_sequence.py`: exactly one
`imagegen.generate(n=1, ...)` call per new pose (**2 calls total**, no
retry, no fallback provider — same discipline as addendum #1), each
grounded on **both** `assets/reference/jorgito_canonical.png` (identity
lock) **and** the immediately-preceding pose's raw generated image
(continuity of motion), via `generate()`'s documented
`reference_images: list[Path]` support. Chained, not fixed: pose 3 grounds
on canonical + pose 2's raw output (not pose 1's), so the progression reads
as one continuous action rather than three independent riffs on the
original pilot image. `scripts/prompts_single_pose.py`'s
`build_single_pose_prompt()` gained one new optional parameter,
`action_override`, so each pose in the sequence can describe its specific
page-turn moment while still routing through the same identity/background/
style template the pilot used — no duplicated prompt-building logic.

### Step 3 — processing

Both new raw images went through the same chroma-key + fit-to-cell
primitives as the pilot (`atlas.remove_background` /
`atlas._fit_to_cell`, `chroma_key=None` so `remove_background` auto-detects
the actual backdrop rather than assuming pure magenta) →
`assets/keyframes/processed/review_pose2_midturn.png` and
`review_pose3_turned.png`, both 192x208 RGBA, clean single-subject output
(no segmentation artifacts, confirming addendum #1's fix generalizes to new
prompts).

### Step 4 — building the real `review` row (6 frames, 3 real poses)

New `scripts/build_review_row.py`. Since the row needs 6 frames and only 3
real poses exist, they're distributed in a **ping-pong** order —
`[pose1, pose2, pose3, pose3, pose2, pose1]` — a forward-then-back page-turn
that shows the full progression twice (forward and reverse) across one loop
and keeps the loop seam smooth (the row's last and first frames are both
close to the "settled" pose rather than jump-cutting from fully-turned back
to closed).

Each of the 6 columns then gets the Phase 4 deterministic bob/tilt/scale
wobble **on top of its real assigned pose** (not instead of it) — `_vary()`
copied verbatim (unmodified) from `phase-4-full-atlas`'s
`scripts/full_atlas.py` (that branch is never merged into this one, so it
can't be imported directly; the cross-review fix from commit `7353a27` —
decoupling bob/tilt/scale onto `sin`/`cos` respectively so mirrored columns
don't collapse — is preserved exactly). This is what makes the two columns
that share a base pose (pose 1 at columns 0 and 5, pose 3 at columns 2 and
3) still hash-distinct instead of relying on pose variation alone for 4/6
columns and identical pixels for the other 2.

No new wobble math was needed — the row-count/assignment logic (`ROW_POSE_ORDER`
+ loading 3 poses instead of 1) is new, but `_vary()` itself is untouched,
per the task's instruction to reuse the existing fix rather than touch the
math.

### Step 5 — validation

Built a full-size (1536×1872) atlas image via Hermes's own
`atlas.compose_atlas({"review": frames})` with **only** the `review` row
filled — every other row's cells stay fully transparent, which is
`compose_atlas`'s own documented behavior for missing states, not a
workaround. Ran Hermes's real, unmodified `atlas.validate_atlas()` against
it directly (turned out to be practical without the full 9-state atlas,
since `validate_atlas()` only *warns* — doesn't error — on an unfilled state
row):

```json
{
  "ok": true,
  "width": 1536,
  "height": 1872,
  "errors": [],
  "warnings": [
    "state 'idle' has no frames", "state 'running-right' has no frames",
    "state 'running-left' has no frames", "state 'waving' has no frames",
    "state 'jumping' has no frames", "state 'failed' has no frames",
    "state 'waiting' has no frames", "state 'running' has no frames"
  ],
  "filled_states": ["review"]
}
```

`ok: true`, zero errors — correct geometry, no multi-pose outliers, no
collapsed-row detection, no transparency residue. The 8 warnings are
expected and harmless (this run intentionally only fills `review`, per the
task's "stop after review" scope).

Frame-hash uniqueness (evidence requested as a fallback, but obtained
alongside the real validator, not instead of it):

| col | pose | sha256[:16] |
|---|---|---|
| 0 | pose 1 (book open, starting) | `fd6e4f6455889d04` |
| 1 | pose 2 (mid-page-turn) | `e1479549f5bf67b3` |
| 2 | pose 3 (page turned) | `ebd74364db9e3ff6` |
| 3 | pose 3 (page turned) | `e91911268077781b` |
| 4 | pose 2 (mid-page-turn) | `8bf546ebff5d0e11` |
| 5 | pose 1 (book open, starting) | `3bc84d95348d49fe` |

**6/6 unique** — including the two column-pairs sharing a base pose (0/5,
2/3), which the wobble alone resolves.

### Step 6 — visual gate evidence

- `assets/keyframes/review_row_contact_sheet.png` — all 6 row frames,
  labeled `col{i}: pose{N}`, in row order left→right. The page-turn
  progression is visually legible across columns (hand/page position
  changes), not a static image repeated with a wobble.
- `assets/keyframes/review_row_preview.gif` — looping animated preview of
  the same 6 frames (280ms/frame, upscaled 3x on a checker backdrop) so the
  page-turning motion can be watched, not just compared frame-by-frame.
- `assets/keyframes/review_row_atlas_fragment.png` — the full-size atlas
  image used for `validate_atlas()`, review row only.
- `assets/keyframes/review_row_report.json` — row order, all 6 hashes,
  full `validate_atlas()` output, file paths.

### Cost

| | |
|---|---|
| Balance before (settled, = pilot's post-pilot balance) | $7.5734 |
| Balance after (settled, ~75s post-run recheck — same `/credits` lag documented in addendum #1) | $7.2911 |
| **Spent this addendum (2 new `generate()` calls)** | **$0.2823** (~$0.1411/call, consistent with the pilot's $0.1415/call) |

Full before/after readings (immediate + settled) in
`assets/keyframes/review_sequence_report.json`.

### Safety verification

- `HERMES_HOME` used throughout: `/home/chegusan/.hermes-jorgito-test` only
  (`generate_review_sequence.py` carries the same refusal guard as
  addendum #1/`hatch_pet_run.py`; `build_review_row.py` is pure image
  processing, no `HERMES_HOME` needed at all).
- Real `~/.hermes/config.yaml`: md5 `66684dd3b378e4584ab08ab097024ed4`,
  mtime `1786786713` — **identical to every prior check in this doc**,
  confirmed again after this addendum's 2 API calls.
- Real `~/.hermes/pets/`: empty before and after.

### Decision

**Addendum #2 done, `review` state only, awaiting human visual gate** on
`assets/keyframes/review_row_contact_sheet.png` and
`assets/keyframes/review_row_preview.gif`. Per the task's explicit scope,
stopped after `review` — no other state was touched. If approved, the
natural next step is generating 2-3 real poses per remaining state with
this same pattern (not attempted here).

### Files changed (addendum #2)

- `scripts/prompts_single_pose.py` (modified — added optional
  `action_override` param to `build_single_pose_prompt`).
- `scripts/generate_review_sequence.py` (new).
- `scripts/build_review_row.py` (new).
- `assets/keyframes/raw_single_pose/review_pose2_midturn.png` (new).
- `assets/keyframes/raw_single_pose/review_pose3_turned.png` (new).
- `assets/keyframes/processed/review_pose2_midturn.png` (new).
- `assets/keyframes/processed/review_pose3_turned.png` (new).
- `assets/keyframes/review_sequence_report.json` (new).
- `assets/keyframes/review_row_atlas_fragment.png` (new).
- `assets/keyframes/review_row_contact_sheet.png` (new).
- `assets/keyframes/review_row_preview.gif` (new).
- `assets/keyframes/review_row_report.json` (new).
- `docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md` (this addendum).
- `docs/08_PROJECT_STATE.md` (updated).

---

## Addendum #3 — refactor to reusable functions + `waiting` row

**Status: DONE, `waiting` state only, awaiting human visual gate.** Human
gave PASS on addendum #2's `review` row. Per the task, before touching a
second state: generalize addendum #2's `review`-only scripts (they were
written for one state, not parameterized) so the remaining 4 states don't
each need a new near-duplicate ~250-line pair of files. Then apply the
validated pattern to `waiting`.

### Step 0 — refactor

Two new modules replace the state-specific logic in
`scripts/generate_review_sequence.py` / `scripts/build_review_row.py`:

- **`scripts/pose_sequence.py`** (new, 211 lines) —
  `generate_pose_sequence(state, action_descriptions, n_poses)`. Same
  chaining/grounding/processing as addendum #2's script (pose 0 grounds on
  `BASE_IMAGE` alone, pose *i>0* grounds on `BASE_IMAGE` + pose *i-1*'s raw
  output; one `imagegen.generate(n=1, ...)` call per pose, no retry, no
  fallback; same chroma-key/fit-to-cell processing), generalized to take the
  state name and per-pose action text as arguments instead of being
  hardcoded to `review`'s page-turn prompts.
- **`scripts/state_row.py`** (new, 223 lines) —
  `build_state_row(state, poses, row_frame_count)`. Same ping-pong + Phase 4
  `_vary()` wobble + `atlas.validate_atlas()` + contact-sheet/GIF/report
  logic as addendum #2's `build_review_row.py`, generalized: pose count and
  row length are no longer hardcoded to 3-into-6, via a new
  `_pingpong_order(n_poses, row_frame_count)` helper (`[0,1,...,n-1,n-1,...,
  1,0]`, cycling if the row doesn't divide evenly by `2*n_poses` — for
  `n_poses=3, row_frame_count=6` this reduces to exactly `[0,1,2,2,1,0]`,
  `review`'s original order). `_vary()` itself is still copied verbatim,
  unmodified, from `phase-4-full-atlas`'s `scripts/full_atlas.py`
  (commit `7353a27`).

Each further state now needs only a ~30-line runner script (see
`scripts/generate_waiting_sequence.py` / `scripts/build_waiting_row.py`
below) — state name, per-pose action text, and pose-file paths — instead of
a new copy of the full generation/assembly logic. Both new modules stay
inside this project's 100-300-line-per-module discipline.

`scripts/generate_review_sequence.py` and `scripts/generate_single_pose.py`
(the scripts that actually produced `review`'s 3 committed poses) are left
untouched, not refactored into thin wrappers over the new module. Reasoning:
they document exactly what commands produced the already-committed,
human-approved `review` assets (different, non-uniform filenames —
`review_singlepose_pilot.png` from a separate pilot script, then
`review_pose2_midturn.png`/`review_pose3_turned.png`); rewriting them as thin
wrappers without ever re-running them (re-running costs real API money,
explicitly out of scope here) would add unverified code to the repo. Only
`scripts/build_review_row.py` — pure image processing, no network, no
`HERMES_HOME` — was rewritten as a thin wrapper, because it's the piece that
*is* safe to actually re-run for verification.

### Step 0 — dry-check: refactor reproduces `review` unchanged

`scripts/build_review_row.py` rewritten as a ~30-line config-only wrapper
calling `state_row.build_state_row("review", POSE_FILES, 6)` against the
same 3 already-committed processed review poses. Re-ran it (no API calls,
no `HERMES_HOME` — pure Pillow processing):

```
review row: 6 frames, 6/6 unique hashes
  col0 (pose1): fd6e4f6455889d04
  col1 (pose2): e1479549f5bf67b3
  col2 (pose3): ebd74364db9e3ff6
  col3 (pose3): e91911268077781b
  col4 (pose2): 8bf546ebff5d0e11
  col5 (pose1): 3bc84d95348d49fe
```

Identical to addendum #2's original 6 hashes. `git status --porcelain --
assets/keyframes/` showed **zero diff** after the re-run — the regenerated
`review_row_atlas_fragment.png`, `review_row_contact_sheet.png`,
`review_row_preview.gif`, and `review_row_report.json` are byte-for-byte
identical (same md5s) to the committed addendum #2 outputs. The generalized
code reproduces `review`'s exact result; no new `review` spend.

### Step 1 — confirm `waiting`'s row frame count

`agent.pet.generate.atlas.ROW_SPECS`: `("waiting", 6, 6)` — row index 6, **6
frames**, same as `review`. `docs/04_ASSET_SPEC.md` / `Jorgito  Plan.md`:
"Waiting: Still/sitting pose with small eye/head movement" /
"Jorgito quieto/sentado; mirada de espera; movimiento mínimo."

### Step 2 — generate 3 real chained poses

New `scripts/generate_waiting_sequence.py` (thin runner over
`pose_sequence.generate_pose_sequence`). Three actions, a centered →
glance-left → glance-right micro-progression:

1. **pose1 (centered/settled):** "sitting calmly in a relaxed, upright
   posture, hands/feet settled and still, head facing forward, calm neutral
   expression, no props, as if quietly waiting for something to happen."
2. **pose2 (glance left)**, grounded on canonical + pose1's raw output:
   "sitting calmly in the exact same relaxed, upright posture as before,
   only the head turned and tilted gently to look off toward the left...
   as if checking whether something is coming from that direction."
3. **pose3 (glance right)**, grounded on canonical + pose2's raw output:
   same posture, head turned/tilted to look right instead.

All 3 calls succeeded (`imagegen.generate(n=1, ...)`, one call each, no
retries, no fallback provider). Elapsed: 23.4s / 50.8s / 52.1s.

**Visual note for the human gate:** the 3 poses came out visually closer
together than the prompt asked for. All three retain essentially the same
3/4-left body orientation; the differences that came through are in stance
(front-paw/seated posture shifts slightly), tail curl, and eye direction,
rather than a strongly legible head-turn toward each side. This wasn't
retried — one API call per pose, no retry loop, no fallback provider, per
this project's guardrails — so it's reported as-is for the human to judge,
same as every other visual gate in this project.

### Step 3 — process through chroma-key/fit-to-cell

Same pipeline as `review`'s poses: `atlas.remove_background(rgba,
chroma_key=None, threshold=90.0)` (auto-detect backdrop, correct for
lossless PNG generator output) + `atlas._fit_to_cell()`, applied inline
inside `generate_pose_sequence` immediately after each successful call.
Output: `assets/keyframes/processed/waiting_pose{1,2,3}.png`, each 192x208
RGBA.

### Step 4 — build the real `waiting` row

New `scripts/build_waiting_row.py` (thin runner over
`state_row.build_state_row`). Ping-pong order `_pingpong_order(3, 6)` =
`[0,1,2,2,1,0]` (identical formula to `review`'s row), Phase 4 `_vary()`
wobble applied on top of each real pose:

| col | pose | sha256[:16] |
|---|---|---|
| 0 | pose 1 (centered) | `d20da4762b777bd7` |
| 1 | pose 2 (glance left) | `8e68447ef865b50f` |
| 2 | pose 3 (glance right) | `0ed1208169dbf00b` |
| 3 | pose 3 (glance right) | `b9177f31632bcb0d` |
| 4 | pose 2 (glance left) | `180f3fe216b26ff1` |
| 5 | pose 1 (centered) | `c649d95a17bbd0e1` |

**6/6 unique.**

### Step 5 — validation

Full-size (1536×1872) atlas image via `atlas.compose_atlas({"waiting":
frames})`, only the `waiting` row filled. Hermes's real, unmodified
`atlas.validate_atlas()`:

```json
{
  "ok": true,
  "width": 1536,
  "height": 1872,
  "errors": [],
  "warnings": [
    "state 'idle' has no frames", "state 'running-right' has no frames",
    "state 'running-left' has no frames", "state 'waving' has no frames",
    "state 'jumping' has no frames", "state 'failed' has no frames",
    "state 'running' has no frames", "state 'review' has no frames"
  ],
  "filled_states": ["waiting"]
}
```

`ok: true`, zero errors — same clean result as `review`'s row.

### Step 6 — visual gate evidence

- `assets/keyframes/waiting_row_contact_sheet.png` — all 6 row frames,
  labeled `col{i}: pose{N}`, sent to the user.
- `assets/keyframes/waiting_row_preview.gif` — looping animated preview
  (280ms/frame, upscaled 3x), sent to the user.
- `assets/keyframes/waiting_row_atlas_fragment.png` — full-size atlas image
  used for `validate_atlas()`, waiting row only.
- `assets/keyframes/waiting_row_report.json` — row order, all 6 hashes,
  full `validate_atlas()` output, file paths.

### Cost

| | |
|---|---|
| Balance before (settled, = review addendum #2's post-run balance) | $7.2911 |
| Balance after (settled, re-checked once `total_usage` had moved for all 3 calls) | $6.8646 |
| **Spent this addendum (3 new `generate()` calls)** | **$0.4265** (~$0.1422/call, consistent with `review`'s ~$0.1411-0.1415/call) |

Full before/after readings (immediate + settled) in
`assets/keyframes/waiting_sequence_report.json`.

### Safety verification

- `HERMES_HOME` used throughout: `/home/chegusan/.hermes-jorgito-test` only
  (`generate_pose_sequence` carries the same refusal guard as every prior
  Phase 2B script; `build_state_row` is pure image processing, no
  `HERMES_HOME` needed at all).
- Real `~/.hermes/config.yaml`: md5 `66684dd3b378e4584ab08ab097024ed4`,
  mtime `1786786713` — **identical to every prior check in this doc**,
  confirmed again before and after this addendum's 3 API calls.
- Real `~/.hermes/pets/`: empty before and after. Full `find
  /home/chegusan/.hermes -maxdepth 2` listing diffed before/after this
  addendum's work — no changes.

### Decision

**Addendum #3 done, `waiting` state only, awaiting human visual gate** on
`assets/keyframes/waiting_row_contact_sheet.png` and
`assets/keyframes/waiting_row_preview.gif` — **with the visual caveat above**
(poses read as a subtler variation than a clear left/right head-turn). Per
the task's explicit scope, stopped after `waiting` — no other state was
touched. If approved as-is or with the caveat accepted, the natural next
step is the same pattern (`generate_pose_sequence` + `build_state_row`) for
the remaining 4 states (`failed`, `jumping`, `waving`, `running`), each
needing only a new thin runner script.

### Files changed (addendum #3)

- `scripts/pose_sequence.py` (new — generalized pose-sequence generation).
- `scripts/state_row.py` (new — generalized row assembly).
- `scripts/build_review_row.py` (rewritten as a thin wrapper over
  `state_row.build_state_row`; re-run, byte-identical to addendum #2's
  committed outputs — see Step 0).
- `scripts/generate_waiting_sequence.py` (new — thin `waiting` runner).
- `scripts/build_waiting_row.py` (new — thin `waiting` runner).
- `assets/keyframes/raw_single_pose/waiting_pose{1,2,3}.png` (new).
- `assets/keyframes/processed/waiting_pose{1,2,3}.png` (new).
- `assets/keyframes/waiting_sequence_report.json` (new).
- `assets/keyframes/waiting_row_atlas_fragment.png` (new).
- `assets/keyframes/waiting_row_contact_sheet.png` (new).
- `assets/keyframes/waiting_row_preview.gif` (new).
- `assets/keyframes/waiting_row_report.json` (new).
- `docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md` (this addendum).
- `docs/08_PROJECT_STATE.md` (updated).

---

## Addendum #4 — `failed` row (3 poses, 8 frames)

**Status: DONE, `failed` state only, awaiting human visual gate.** Applied
the now-generalized pattern (`scripts/pose_sequence.py` +
`scripts/state_row.py`, unmodified from addendum #3) to `failed`, per
`docs/04_ASSET_SPEC.md`'s "Failed: Friendly confused reaction; optional tiny
smoke puff" and the Plan's "Jorgito mostrando un error/reacción cómica
leve". No new refactor needed — only a thin per-state runner pair, same
shape as `waiting`'s.

### Step 1 — confirm `failed`'s row frame count

`agent.pet.generate.atlas.ROW_SPECS`: `("failed", 5, 8)` — row index 5, **8
frames**, longer than `review`/`waiting`'s 6. Read directly from the real
source (`/home/chegusan/.hermes/hermes-agent/agent/pet/generate/atlas.py`),
not re-derived from the doc excerpt above.

### Step 2 — generate 3 real chained poses, with the `waiting` caveat in mind

New `scripts/generate_failed_sequence.py` (thin runner over
`pose_sequence.generate_pose_sequence`). `waiting`'s addendum #3 flagged
that its 3 poses read as too visually similar (same body orientation, only
subtle stance/gaze differences) — each action description here was written
to force a **structurally different body pose**, not just an expression
shift, so the progression reads at a glance:

1. **pose1 (neutral confused/surprised):** both arms down at sides, torso
   leaned back slightly, head tilted, eyebrows raised, small "huh?" mouth —
   no smoke, no props.
2. **pose2 (arm raised, scratching head)**, grounded on canonical + pose1's
   raw output: one arm now bent and raised with the hand/paw scratching the
   top of the head, the other arm still down, head tilted further, eyes
   looking up-and-off as if puzzling over the problem.
3. **pose3 (both arms up, smoke puff)**, grounded on canonical + pose2's raw
   output: both arms raised in an exaggerated shrug/puzzled gesture, a small
   comedic sweat-drop, a tiny wisp of white smoke puffing from just above the
   head, gentle and cute — explicitly NOT scary or aggressive.

All 3 calls succeeded (`imagegen.generate(n=1, ...)`, one call each, no
retries, no fallback provider). Elapsed: 20.3s / 22.6s / 42.4s.

**Result: clearly distinguishable poses.** Unlike `waiting`, the 3 raw
outputs show visibly different arm/body positions (arms down → one arm up →
both arms up) — confirmed by direct visual inspection of the raw generated
images, not just the prompt intent.

**Visual defect for the human gate:** pose3's raw generation includes a
soft drop-shadow ellipse beneath the character, on a slightly different
shade of green than the flat chroma-key background. `atlas.remove_background
(chroma_key=None, threshold=90.0)` (auto-detect) did not fully key out that
shadow — it survives as a small green patch under the feet in the processed
cell and in every row column that uses pose 3 (columns 2 and 3). Poses 1 and
2 have clean flat backgrounds with no shadow and keyed out cleanly. Not
retried (one call per pose, no retry loop, per guardrails) — flagged as-is,
same practice as `waiting`'s caveat.

### Step 3 — process through chroma-key/fit-to-cell

Same pipeline as `review`/`waiting`: `atlas.remove_background(rgba,
chroma_key=None, threshold=90.0)` + `atlas._fit_to_cell()`, applied inline
inside `generate_pose_sequence` immediately after each successful call.
Output: `assets/keyframes/processed/failed_pose{1,2,3}.png`, each 192x208
RGBA (pose3 carries the shadow-patch defect noted above).

### Step 4 — build the real `failed` row (8 frames, 3 real poses)

New `scripts/build_failed_row.py` (thin runner over
`state_row.build_state_row`). `_pingpong_order(3, 8)` cycles the base
6-length ping-pong pattern once: `[0, 1, 2, 2, 1, 0, 0, 1]` (pose1, pose2,
pose3, pose3, pose2, pose1, pose1, pose2) — the generalized helper handles
the longer row without any state-specific logic. Phase 4 `_vary()` wobble
applied on top of each real pose, same as every prior row.

| col | pose | sha256[:16] |
|---|---|---|
| 0 | pose 1 (neutral confused) | `88756f92b416e19a` |
| 1 | pose 2 (arm scratching head) | `b019552be7f98fbc` |
| 2 | pose 3 (both arms up, smoke) | `6c6c37c0e1c66b9d` |
| 3 | pose 3 (both arms up, smoke) | `284b69c91ad99f01` |
| 4 | pose 2 (arm scratching head) | `73c34bd407d5cd57` |
| 5 | pose 1 (neutral confused) | `98f7e9f91fcbb9d4` |
| 6 | pose 1 (neutral confused) | `616b2918b58514b0` |
| 7 | pose 2 (arm scratching head) | `d75da4c563831207` |

**8/8 unique.**

### Step 5 — validation

Full-size (1536×1872) atlas image via `atlas.compose_atlas({"failed":
frames})`, only the `failed` row filled. Hermes's real, unmodified
`atlas.validate_atlas()`:

```json
{
  "ok": true,
  "width": 1536,
  "height": 1872,
  "errors": [],
  "warnings": [
    "state 'idle' has no frames", "state 'running-right' has no frames",
    "state 'running-left' has no frames", "state 'waving' has no frames",
    "state 'jumping' has no frames", "state 'waiting' has no frames",
    "state 'running' has no frames", "state 'review' has no frames"
  ],
  "filled_states": ["failed"]
}
```

`ok: true`, zero errors — same clean geometry result as `review`/`waiting`'s
rows (the un-keyed shadow patch is a background-removal artifact, not
something `validate_atlas()` checks for).

### Step 6 — visual gate evidence

- `assets/keyframes/failed_row_contact_sheet.png` — all 8 row frames,
  labeled `col{i}: pose{N}`, **sent to the user via SendUserFile**.
- `assets/keyframes/failed_row_preview.gif` — looping animated preview
  (280ms/frame, upscaled 3x), **sent to the user via SendUserFile**.
- `assets/keyframes/failed_row_atlas_fragment.png` — full-size atlas image
  used for `validate_atlas()`, `failed` row only.
- `assets/keyframes/failed_row_report.json` — row order, all 8 hashes, full
  `validate_atlas()` output, file paths.

### Cost

| | |
|---|---|
| Balance before (settled, = waiting addendum #3's post-run balance) | $6.8646 |
| Balance after (settled, re-checked once `total_usage` had moved for all 3 calls) | $6.4435 |
| **Spent this addendum (3 new `generate()` calls)** | **$0.4210** (~$0.1403/call, consistent with prior addenda's ~$0.14/call) |

Full before/after readings (immediate + settled) in
`assets/keyframes/failed_sequence_report.json`.

### Safety verification

- `HERMES_HOME` used throughout: `/home/chegusan/.hermes-jorgito-test` only
  (`generate_pose_sequence` carries the same refusal guard as every prior
  Phase 2B script; `build_state_row` is pure image processing, no
  `HERMES_HOME` needed at all).
- Real `~/.hermes/config.yaml`: md5 `66684dd3b378e4584ab08ab097024ed4`,
  mtime `1786786713` — **identical to every prior check in this doc**,
  confirmed again before and after this addendum's 3 API calls.
- Real `~/.hermes/pets/`: empty before and after. Full `find
  /home/chegusan/.hermes -maxdepth 2` listing diffed before/after this
  addendum's work — no changes.

### Decision

**Addendum #4 done, `failed` state only, awaiting human visual gate** on
`assets/keyframes/failed_row_contact_sheet.png` and
`assets/keyframes/failed_row_preview.gif` — **with the visual caveat above**
(pose 3's un-keyed shadow patch, visible in columns 2 and 3). Per the task's
explicit scope, stopped after `failed` — no other state was touched. If
approved as-is, with the shadow patch accepted, or with a targeted retry of
pose 3 only, the natural next step is the same pattern for the remaining 3
states (`jumping`, `waving`, `running`), each needing only a new thin
runner script.

### Files changed (addendum #4)

- `scripts/generate_failed_sequence.py` (new — thin `failed` runner).
- `scripts/build_failed_row.py` (new — thin `failed` runner).
- `assets/keyframes/raw_single_pose/failed_pose{1,2,3}.png` (new).
- `assets/keyframes/processed/failed_pose{1,2,3}.png` (new).
- `assets/keyframes/failed_sequence_report.json` (new).
- `assets/keyframes/failed_row_atlas_fragment.png` (new).
- `assets/keyframes/failed_row_contact_sheet.png` (new).
- `assets/keyframes/failed_row_preview.gif` (new).
- `assets/keyframes/failed_row_report.json` (new).
- `docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md` (this addendum).
- `docs/08_PROJECT_STATE.md` (updated).

---

## Addendum #5 — `failed` row chroma-key fix (pose 3 shadow patch)

**Status: DONE, `failed` state only, PASS.** Branch
`phase2b-fix-failed-chromakey` (base `phase2b-hatch-pet-regen`). Fixes the
one processing defect addendum #4 flagged: pose 3's un-keyed drop-shadow,
visible as a small green patch under the feet in row columns 2 and 3.
**Zero API/generation calls** — purely a deterministic reprocessing of the
already-committed raw pose-3 image
(`assets/keyframes/raw_single_pose/failed_pose3.png`).

### Root cause

`atlas.remove_background(chroma_key=None, threshold=90.0)` auto-detects the
backdrop key from the corner color, then keys out matching pixels. For a
strongly saturated key (this pose's auto-detected key was `(2, 253, 5)`,
`max-min = 251 >= 120`), `remove_background` takes its **fast path**: a
global near-key color match with no connectivity requirement (unlike the
border-flood-fill it uses for desaturated keys). Pose 3's raw generation
included a soft drop-shadow ellipse blended toward — but not fully matching
— the flat backdrop color; its pixels measured ~56–110 color-distance from
the key (sampled directly from the processed cell), just outside the 90
threshold, so the fast path left them opaque.

Simply widening `remove_background`'s own `threshold` was ruled out:
because the fast path has no connectivity gate, a wider threshold would
also remove any interior pixel that happens to be close to green — and
this character has **green eyes** (an eye-region pixel measured ~100–110
distance from the same key, right in the shadow's range). Widening the
global threshold enough to clear the shadow risked punching a hole in the
eyes. `remove_background` itself lives in
`/home/chegusan/.hermes/hermes-agent/agent/pet/generate/atlas.py` — the
real, non-isolated `~/.hermes` tree this project's guardrails say never to
edit — so the fix could not live there even if it had been the right shape.

### Fix

Added a second, **connectivity-gated** pass in `scripts/pose_sequence.py`
(shared logic, not a `failed`-only hack):

- `_flood_extend_transparency(rgba, key, threshold)` — reuses
  `atlas.remove_background`'s own border-flood-fill *shape* (BFS over
  4-connected near-key pixels), but seeds the flood from the pixels
  `remove_background` already made transparent (not just the image border),
  with a looser threshold (`DESPILL_THRESHOLD = 170.0`, comfortably above
  the shadow's measured ~110 max and comfortably below the nearest real
  character color at ~218). Because removal requires connectivity to
  already-removed background, an isolated key-ish interior pixel (the eyes)
  stays untouched regardless of threshold — it's never reachable without
  crossing genuinely non-key-colored face pixels.
- `_remove_background_despilled(rgba, chroma_key, threshold)` — wraps
  `atlas.remove_background` + the extension pass. Both
  `generate_pose_sequence` (fresh generation) and the new `reprocess_pose`
  (after-the-fact fix, no generation) call this shared function, so every
  future state's pipeline gets the despill pass automatically, and a
  processing-only defect never again needs a `hatch_pet()`/`generate()`
  re-spend to fix.
- `reprocess_pose(state, name, raw_path=None)` — re-runs chroma-key +
  fit-to-cell against an already-committed raw pose, no network, no
  `HERMES_HOME`. New thin runner `scripts/fix_failed_pose3_chromakey.py`
  calls `reprocess_pose("failed", "pose3")` then rebuilds the row via the
  existing `build_failed_row.main()`.

Poses 1/2 were not reprocessed — addendum #4 already confirmed they have no
shadow and keyed out cleanly; their processed cells are untouched
(`git diff --stat` on `failed_pose1.png`/`failed_pose2.png`: empty).

### Verification

**Pixel-level, before/after:** greenish opaque pixels (`r<60, b<60,
g>120`) in the processed `failed_pose3.png` cell: **1474 → 1**. Visual
crop, zoomed on the feet, sent to the user
(`assets/keyframes/failed_pose3_chromakey_fix_before_after.png`) —
green patch fully gone, claws/feet detail unaffected, eyes intact (not
eaten by the widened tolerance, confirming the connectivity gate worked as
designed).

**`validate_atlas()`, real Hermes, re-run on the rebuilt `failed` row:**

```json
{
  "ok": true,
  "width": 1536,
  "height": 1872,
  "errors": [],
  "warnings": [
    "state 'idle' has no frames", "state 'running-right' has no frames",
    "state 'running-left' has no frames", "state 'waving' has no frames",
    "state 'jumping' has no frames", "state 'waiting' has no frames",
    "state 'running' has no frames", "state 'review' has no frames"
  ],
  "filled_states": ["failed"]
}
```

Frame hashes, before → after (columns 2/3 are the only ones that changed —
exactly the two columns using pose 3; all other columns byte-identical to
addendum #4):

| col | pose | before (addendum #4) | after (this fix) |
|---|---|---|---|
| 0 | pose1 | `88756f92b416e19a` | `88756f92b416e19a` (unchanged) |
| 1 | pose2 | `b019552be7f98fbc` | `b019552be7f98fbc` (unchanged) |
| 2 | pose3 | `6c6c37c0e1c66b9d` | `fbef9264dc07852a` (changed — patch removed) |
| 3 | pose3 | `284b69c91ad99f01` | `6a6e4cbb1aadaf0d` (changed — patch removed) |
| 4 | pose2 | `73c34bd407d5cd57` | `73c34bd407d5cd57` (unchanged) |
| 5 | pose1 | `98f7e9f91fcbb9d4` | `98f7e9f91fcbb9d4` (unchanged) |
| 6 | pose1 | `616b2918b58514b0` | `616b2918b58514b0` (unchanged) |
| 7 | pose2 | `d75da4c563831207` | `d75da4c563831207` (unchanged) |

**8/8 unique**, `validate_atlas() ok: true` — pose-variation fix from
addendum #4 not regressed.

**Surgical-fix confirmation — every other row/state untouched:** `sha256sum`
over every file under `assets/keyframes/` *except* `failed`-prefixed ones
(idle/review/waiting rows' PNGs/GIFs/JSONs, atlas fragments, contact
sheets, reference assets), recorded before this fix and re-checked after:
**all byte-identical**. `git status --porcelain` after the fix shows only
`failed`-scoped assets plus `scripts/pose_sequence.py` (the shared code)
and the new `scripts/fix_failed_pose3_chromakey.py` runner — nothing else.

**Zero API/generation calls, zero spend:** `scripts/fix_failed_pose3_chromakey.py`
never imports `imagegen`, never sets `HERMES_HOME`, never touches the
network — pure Pillow reprocessing of an already-committed raw file.

**Real `~/.hermes` untouched:** `~/.hermes/config.yaml` md5
`66684dd3b378e4584ab08ab097024ed4`, mtime `1786786713` — identical to every
prior check in this document. `find ~/.hermes -maxdepth 2` listing
diffed before/after this fix: no changes. `~/.hermes/pets/`: empty before
and after (isolated profile was never even activated — this fix never
calls `_activate_isolated_home()`).

### Cost

$0.00 — no `generate()` calls, no `HERMES_HOME` activation.

### Files changed (addendum #5)

- `scripts/pose_sequence.py` (modified — added
  `_flood_extend_transparency`, `DESPILL_THRESHOLD`,
  `_remove_background_despilled`, `reprocess_pose`; inline processing call
  in `generate_pose_sequence` switched to the despilled wrapper).
- `scripts/fix_failed_pose3_chromakey.py` (new — thin one-off runner).
- `assets/keyframes/processed/failed_pose3.png` (reprocessed).
- `assets/keyframes/failed_row_atlas_fragment.png` (rebuilt).
- `assets/keyframes/failed_row_contact_sheet.png` (rebuilt).
- `assets/keyframes/failed_row_preview.gif` (rebuilt).
- `assets/keyframes/failed_row_report.json` (rebuilt).
- `assets/keyframes/failed_pose3_chromakey_fix_before_after.png` (new —
  before/after evidence crop, sent to the user).
- `docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md` (this addendum).
- `docs/08_PROJECT_STATE.md` (updated).

### Decision

**PASS.** The `failed` row's only outstanding visual-gate caveat (pose 3's
shadow patch) is resolved with real pixel-level and `validate_atlas()`
evidence, at zero cost, with every other row proven byte-identical. Ready
for the human's final visual-gate sign-off on `failed` alongside `waiting`
(still pending from addendum #3/#4, unaffected by this fix). PR opened
against `phase2b-hatch-pet-regen`.

### Next phase/task

None dispatched automatically. Once `waiting` and `failed` both clear the
human visual gate, the natural next step is applying the same
`pose_sequence.py` + `state_row.py` pattern (now despill-protected by
default) to the remaining 3 states (`jumping`, `waving`, `running`) — not
started here, out of this fix's scope.

---

## Addendum #6 — `waving` row (3 poses, 4 frames)

**Status: DONE, `waving` state only, awaiting human visual gate.** Applied
the generalized pattern (`scripts/pose_sequence.py` + `scripts/state_row.py`,
unmodified since addendum #5's despill fix, so this row benefits from that
fix by default) to `waving`, per `docs/04_ASSET_SPEC.md`'s "Waving: Simple
clear arm wave". Branch `phase2b-pose-sequence-wave`, forked from
`phase2b-fix-failed-chromakey` (so this row's despill pipeline is the fixed
one, no shadow-patch risk re-derived).

### Step 1 — confirm `waving`'s real row key and frame count

`agent.pet.generate.atlas.ROW_SPECS`: `("waving", 3, 4)` — row index 3, key
is **`waving`** (not `wave`), **4 frames** (shorter than every other row
generated so far: `review`/`waiting` are 6, `failed` is 8). Read directly
from the real source
(`/home/chegusan/.hermes/hermes-agent/agent/pet/generate/atlas.py`), not
assumed — this project's established gotcha (`jumping`'s real key/count also
differed from a naive guess) applied here too.

### Step 2 — generate 3 real chained poses

New `scripts/generate_waving_sequence.py` (thin runner over
`pose_sequence.generate_pose_sequence`). Learning from `waiting`'s "too
subtle" caveat (addendum #3), each action description pins a distinctly
different arm silhouette/angle rather than a small variation on one pose:

1. **pose1 (arm starting to raise):** one arm raised partway up and out to
   the side, only about chest height, elbow bent, hand starting to open — a
   clearly low, early-stage wave position. Other arm/tail resting naturally,
   friendly smile.
2. **pose2 (peak of the wave)**, grounded on canonical + pose1's raw output:
   arm raised straight up high above the head, fully extended, hand wide
   open palm-forward — the highest, most vertical point of the arm.
3. **pose3 (mid-swing, opposite side)**, grounded on canonical + pose2's raw
   output: arm swept diagonally to the opposite side of the body from where
   it started, roughly shoulder height, hand open — intended as the far side
   of a side-to-side swing, explicitly not a return to rest.

All 3 calls succeeded (`imagegen.generate(n=1, ...)`, one call each, no
retries, no fallback provider). Elapsed: 27.0s / 24.8s / 20.3s.

**Result: visually distinct, with a caveat.** Direct inspection of the 3
processed poses (side-by-side and cropped arm-region comparisons) confirms
3 different arm silhouettes: pose1 is low and held away from the body
(wide gesture), pose2 is the clear high peak, pose3 is mid-height with the
elbow tucked closer to the head (narrower gesture, hand near the face) —
not a byte-similar repeat of pose1 or pose2. **Caveat for the human gate:**
pose3 reads as "arm swept inward near the face" more than "swept to the
literal opposite side of the body" the prompt asked for — its overall
height is closer to pose1's than to a dramatically different position.
Judged as clearing the "unmistakably distinct" bar (three different
silhouettes, not a subtle wobble) but not as strong a side-to-side read as
the suggested progression intended. Not retried (one call per pose, no
retry loop, per guardrails) — flagged as-is, same practice as
`waiting`/`failed`'s caveats.

### Step 3 — process through chroma-key/fit-to-cell (despill-protected)

Same pipeline as every state since addendum #5:
`_remove_background_despilled` (`atlas.remove_background(chroma_key=None,
threshold=90.0)` + the border-flood despill extension) +
`atlas._fit_to_cell()`. Output: `assets/keyframes/processed/waving_pose{1,2,3}.png`,
each 192x208 RGBA. No shadow-patch or unkeyed-background defects observed
in any of the 3 poses.

### Step 4 — build the real `waving` row (4 frames, 3 real poses)

New `scripts/build_waving_row.py` (thin runner over
`state_row.build_state_row`). `_pingpong_order(3, 4)` = `[0, 1, 2, 2]`
(pose1, pose2, pose3, pose3) — the shortest row built so far, so the base
6-length ping-pong cycle (`[0,1,2,2,1,0]`) is truncated rather than
repeated; the generalized helper handles this without any state-specific
logic. Phase 4 `_vary()` wobble applied on top of each real pose (different
wobble phase per column keeps columns 2/3 hash-distinct despite sharing
pose3).

| col | pose | sha256[:16] |
|---|---|---|
| 0 | pose 1 (arm starting to raise) | `00a8655454319163` |
| 1 | pose 2 (peak of the wave) | `3780b1da4b1b5c05` |
| 2 | pose 3 (mid-swing, opposite side) | `8e3f10e3943ac684` |
| 3 | pose 3 (mid-swing, opposite side) | `64aead8fc5ce9f05` |

**4/4 unique.**

### Step 5 — validation

Full-size (1536×1872) atlas image via `atlas.compose_atlas({"waving":
frames})`, only the `waving` row filled. Hermes's real, unmodified
`atlas.validate_atlas()`:

```json
{
  "ok": true,
  "width": 1536,
  "height": 1872,
  "errors": [],
  "warnings": [
    "state 'idle' has no frames", "state 'running-right' has no frames",
    "state 'running-left' has no frames", "state 'jumping' has no frames",
    "state 'failed' has no frames", "state 'waiting' has no frames",
    "state 'running' has no frames", "state 'review' has no frames"
  ],
  "filled_states": ["waving"]
}
```

`ok: true`, zero errors, 4/4 unique hashes == `waving`'s real frame count.

### Step 6 — visual gate evidence

- `assets/keyframes/waving_row_contact_sheet.png` — all 4 row frames,
  labeled `col{i}: pose{N}`, **sent to the user via SendUserFile**.
- `assets/keyframes/waving_row_preview.gif` — looping animated preview
  (280ms/frame, upscaled 3x), **sent to the user via SendUserFile**.
- `assets/keyframes/waving_row_atlas_fragment.png` — full-size atlas image
  used for `validate_atlas()`, `waving` row only.
- `assets/keyframes/waving_row_report.json` — row order, all 4 hashes, full
  `validate_atlas()` output, file paths.

### Cost

| | |
|---|---|
| Balance before (settled) | $6.0193 |
| Balance after (immediate; may lag actual settlement) | $5.8775 |
| **Spent this addendum (3 new `generate()` calls)** | **$0.1418** (~$0.047/call — notably cheaper than prior addenda's ~$0.14/call; reported as measured, not adjusted) |

Full before/after readings (immediate) in
`assets/keyframes/waving_sequence_report.json`.

### Safety verification

- `HERMES_HOME` used throughout: `/home/chegusan/.hermes-jorgito-test` only
  (`generate_pose_sequence` carries the same refusal guard as every prior
  Phase 2B script; `build_state_row` is pure image processing, no
  `HERMES_HOME` needed at all).
- Real `~/.hermes/config.yaml`: md5 `66684dd3b378e4584ab08ab097024ed4`,
  mtime `1786786713` — **identical to every prior check in this doc**,
  confirmed after this addendum's 3 API calls.
- Real `~/.hermes/pets/`: empty, confirmed after this addendum's work.

### Decision

**Addendum #6 done, `waving` state only, awaiting human visual gate** on
`assets/keyframes/waving_row_contact_sheet.png` and
`assets/keyframes/waving_row_preview.gif` — **with the visual caveat
above** (pose 3 reads as "swept inward near the face" rather than a
dramatically opposite-side position, though still visually distinct from
poses 1/2). Per the task's explicit scope, stopped after `waving` — no
other state was touched. PR opened against `phase2b-fix-failed-chromakey`
(this branch's base — already includes the despill fix, so the diff here
is `waving`-only).

### Files changed (addendum #6)

- `scripts/generate_waving_sequence.py` (new — thin `waving` runner).
- `scripts/build_waving_row.py` (new — thin `waving` runner).
- `assets/keyframes/raw_single_pose/waving_pose{1,2,3}.png` (new).
- `assets/keyframes/processed/waving_pose{1,2,3}.png` (new).
- `assets/keyframes/waving_sequence_report.json` (new).
- `assets/keyframes/waving_row_atlas_fragment.png` (new).
- `assets/keyframes/waving_row_contact_sheet.png` (new).
- `assets/keyframes/waving_row_preview.gif` (new).
- `assets/keyframes/waving_row_report.json` (new).
- `docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md` (this addendum).

## Addendum #7 — `running-right` row (3 poses, 8 frames) — LAST Phase 2B state

**Status: DONE, `running-right` state only, awaiting human visual gate.**
Applied the generalized pattern (`scripts/pose_sequence.py` +
`scripts/state_row.py`, unmodified since addendum #5's despill fix) to
`running-right`. This is the **9th and last** Hermes pet state generated
in Phase 2B — `idle`/`running`(digging)/`review`/`waiting`/`failed`/
`jumping`/`waving` already approved, `running-left` is a free horizontal
mirror of this row and is not separately generated. Branch
`phase2b-pose-sequence-running-right`, forked from `phase2b-pose-sequence-wave`.

### Step 1 — confirm `running-right`'s real row key and frame count

`agent.pet.generate.atlas.ROW_SPECS`: `("running-right", 1, 8)` — row index
1, key is **`running-right`** (hyphenated, not `running_right`/`run_right`),
**8 frames** — the longest row generated in Phase 2B so far (tied with
`failed`). Read directly from the real source
(`/home/chegusan/.hermes/hermes-agent/agent/pet/generate/atlas.py`), not
assumed — this project's established gotcha (`jumping`'s and `waving`'s
real key/count also differed from a naive guess). Note `running` (row 7, 6
frames) is a *different* state — the in-place working/digging pose, not
locomotion — confirmed not to collide with this row.

### Step 2 — generate 3 real chained poses

New `scripts/generate_running_right_sequence.py` (thin runner over
`pose_sequence.generate_pose_sequence`). A three-pose running stride cycle,
each action description pinning a clearly different leg/arm silhouette
(learned from `waiting`'s "too subtle" caveat):

1. **pose1 (stride, leg 1 forward):** right leg reaching far forward about
   to plant, left leg extended straight back, arms in opposite running
   swing, forward lean, tail trailing — a clearly open, wide-stride
   silhouette.
2. **pose2 (compact passing position)**, grounded on canonical + pose1's
   raw output: both legs momentarily close together/crossing under the
   body, more upright/compact than the reaching stride, arms tucked —
   a clearly compact, legs-together silhouette.
3. **pose3 (stride, leg 2 forward — mirror of pose1)**, grounded on
   canonical + pose2's raw output: left leg reaching far forward, right leg
   back, arms swapped — the mirror-opposite leg placement of pose1.

All 3 calls succeeded (`imagegen.generate(n=1, ...)`, one call each, no
retries, no fallback provider). Elapsed: 21.3s / 38.9s / 32.9s.

**Result: visually distinct, with a caveat.** Pairwise pixel-diff (>40
per-channel-sum threshold, over the full 192x208 processed cell) measured
41.5-42.4% of pixels differing between the "stride" poses (1, 3) and the
"passing" pose (2), and 38.0% between poses 1 and 3 themselves despite
being mirror-intended — comfortably clearing the "unmistakably distinct"
bar (compare to a subtle wobble, which would read well under 10%), and
bounding-box extents confirm a real stance change (pose1 top=15px, more
crouched/lower; poses 2/3 top=5px, more upright). **Caveat for the human
gate:** the model rendered all three poses with the character facing/
leaning toward the LEFT of the frame (matching its own internal
left-facing convention for this sprite, as seen in every other approved
state) rather than the prompted rightward-facing run direction, and the
stride reads more as a energetic trot/hop than a dramatic full sprint
stride. Not retried (one call per pose, no retry loop, per guardrails) —
flagged as-is, same practice as `waiting`/`failed`/`waving`'s caveats.
Since `running-left` is derived from this row via horizontal mirror (not
separately generated), a left-facing `running-right` source is a real
naming/direction mismatch worth the human gate's attention, not just a
style nit.

### Step 3 — process through chroma-key/fit-to-cell (despill-protected)

Same pipeline as every state since addendum #5:
`_remove_background_despilled` (`atlas.remove_background(chroma_key=None,
threshold=90.0)` + the border-flood despill extension) +
`atlas._fit_to_cell()`. Output:
`assets/keyframes/processed/running-right_pose{1,2,3}.png`, each 192x208
RGBA. No shadow-patch or unkeyed-background defects observed in any of the
3 poses (confirmed by direct inspection of the contact sheet — clean
transparency, no magenta/green fringe).

### Step 4 — build the real `running-right` row (8 frames, 3 real poses)

New `scripts/build_running_right_row.py` (thin runner over
`state_row.build_state_row`). `_pingpong_order(3, 8)` = `[0, 1, 2, 2, 1, 0,
0, 1]` — the base 6-length ping-pong cycle (`[0,1,2,2,1,0]`) cycles around
to fill the extra 2 columns, same generalized behavior used for every
prior row, no state-specific logic needed.

| col | pose | sha256[:16] |
|---|---|---|
| 0 | pose 1 (stride, leg 1 forward) | `66a4efff9e43dac7` |
| 1 | pose 2 (compact passing) | `e48faf9d240f1a82` |
| 2 | pose 3 (stride, leg 2 forward) | `47f3603eae80713c` |
| 3 | pose 3 (stride, leg 2 forward) | `f305977021e0e636` |
| 4 | pose 2 (compact passing) | `0567bd6f6433cfb1` |
| 5 | pose 1 (stride, leg 1 forward) | `ff666d96621c61a4` |
| 6 | pose 1 (stride, leg 1 forward) | `e08a8d555c820d09` |
| 7 | pose 2 (compact passing) | `2d42602357e5db7b` |

**8/8 unique.**

### Step 5 — validation

Full-size (1536x1872) atlas image via `atlas.compose_atlas({"running-right":
frames})`, only the `running-right` row filled. Hermes's real, unmodified
`atlas.validate_atlas()`:

```json
{
  "ok": true,
  "width": 1536,
  "height": 1872,
  "errors": [],
  "warnings": [
    "state 'idle' has no frames", "state 'running-left' has no frames",
    "state 'waving' has no frames", "state 'jumping' has no frames",
    "state 'failed' has no frames", "state 'waiting' has no frames",
    "state 'running' has no frames", "state 'review' has no frames"
  ],
  "filled_states": ["running-right"]
}
```

`ok: true`, zero errors, 8/8 unique hashes == `running-right`'s real frame
count.

### Step 6 — visual gate evidence

- `assets/keyframes/running-right_row_contact_sheet.png` — all 8 row
  frames, labeled `col{i}: pose{N}`, **sent to the user via SendUserFile**.
- `assets/keyframes/running-right_row_preview.gif` — looping animated
  preview (280ms/frame, upscaled 3x), **sent to the user via SendUserFile**.
- `assets/keyframes/running-right_row_atlas_fragment.png` — full-size atlas
  image used for `validate_atlas()`, `running-right` row only.
- `assets/keyframes/running-right_row_report.json` — row order, all 8
  hashes, full `validate_atlas()` output, file paths.

### Cost

| | |
|---|---|
| Balance before (immediate) | $5.5956 |
| Balance after (immediate; may lag actual settlement) | $5.3142 |
| **Spent this addendum (3 new `generate()` calls)** | **$0.2813** (~$0.094/call) |

Full before/after readings (immediate) in
`assets/keyframes/running-right_sequence_report.json`.

### Safety verification

- `HERMES_HOME` used throughout: `/home/chegusan/.hermes-jorgito-test` only
  (`generate_pose_sequence` carries the same refusal guard as every prior
  Phase 2B script; `build_state_row` is pure image processing, no
  `HERMES_HOME` needed at all).
- Real `~/.hermes/config.yaml`: md5 `66684dd3b378e4584ab08ab097024ed4`,
  mtime `1786786713` — **identical to every prior check in this doc**,
  confirmed after this addendum's 3 API calls.
- Real `~/.hermes/pets/`: empty, confirmed after this addendum's work.

### Decision

**Addendum #7 done, `running-right` state only, awaiting human visual
gate** on `assets/keyframes/running-right_row_contact_sheet.png` and
`assets/keyframes/running-right_row_preview.gif` — **with the visual
caveat above** (left-facing render despite a rightward-facing prompt; more
trot than dramatic sprint stride — though still visually distinct pose-to-
pose). This is the last of the 9 Hermes pet states for Phase 2B; pending
this gate's approval, all real-pose row generation work for this phase is
complete. PR opened against `phase2b-pose-sequence-wave` (this branch's
base).

### Files changed (addendum #7)

- `scripts/generate_running_right_sequence.py` (new — thin `running-right`
  runner).
- `scripts/build_running_right_row.py` (new — thin `running-right` runner).
- `assets/keyframes/raw_single_pose/running-right_pose{1,2,3}.png` (new).
- `assets/keyframes/processed/running-right_pose{1,2,3}.png` (new).
- `assets/keyframes/running-right_sequence_report.json` (new).
- `assets/keyframes/running-right_row_atlas_fragment.png` (new).
- `assets/keyframes/running-right_row_contact_sheet.png` (new).
- `assets/keyframes/running-right_row_preview.gif` (new).
- `assets/keyframes/running-right_row_report.json` (new).
- `docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md` (this addendum).
- `docs/08_PROJECT_STATE.md` (updated).
