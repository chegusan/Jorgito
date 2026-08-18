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
