# Phase Result

## Phase

Phase 1 — Minimal visual proof (`idle`, `review`, `running`)

## Status

PASS (deterministic processing) — final visual-identity gate (F1-A/F1-B)
still needs the user's own eyes; see "Self-assessment" below.

## Evidence

### 0. Generation path actually used (superseding the earlier API attempt)

An earlier attempt in this same phase tried to generate the 3 keyframes via
Hermes's native `imagegen` pipeline and hit hard blockers on every
reference-capable provider configured in this environment (`openai`: billing
hard limit; `openrouter`: 401 missing-auth). That attempt spent **0** of the
3-generation budget (see git history on this branch, commit
`7e71bfa`) — no image was ever produced through that path.

The user then generated the 3 keyframes **manually** (outside this agent,
no API tokens spent by this session), using
`assets/reference/jorgito_canonical.png` as the grounding reference, and
committed them directly to
`assets/keyframes/raw/{idle,review,run}.jpeg` (commit `b766dc9`, 1984×2144
JPEG each). This phase result covers the deterministic processing of those
3 already-provided raw images — no image-generation model call was made by
this agent in this session.

### 1. Method: deterministic processing only (Camino B, per AGENTS.md)

New script: `scripts/process_phase1_keyframes.py` (Pillow-only, ~130 lines,
no network calls, no API keys, no model inference). For each of the 3 raw
keyframes it:

1. Loads the JPEG and converts to RGBA.
2. Chroma-keys the flat hot-magenta (`#FF00FF`) backdrop to transparent.
3. Crops to the character's content bounding box, scales it to fit inside a
   192×208 px cell (the project's standard sprite-cell size per
   `docs/03_INTERFACES_AND_CONTRACTS.md`) preserving aspect ratio, and
   centers it on a transparent canvas.
4. Saves the result as `assets/keyframes/processed/{state}.png`.

It then composites the 3 processed cells into
`assets/keyframes/contact_sheet_phase1.png`: each cell upscaled 3x on a
checkerboard-transparency backdrop, on a light-gray sheet background, with
an `idle` / `review` / `run` text label under each.

**Reuse decision:** steps 2–3 (chroma-key removal, crop/fit-to-cell) are not
reimplemented — this script imports and calls
`agent.pet.generate.atlas.remove_background()` and
`agent.pet.generate.atlas._fit_to_cell()` directly from the installed Hermes
build (`/home/chegusan/.hermes/hermes-agent`, read-only import, same
pattern as `scripts/generate_phase1.py`'s earlier `atlas` import). Both are
pure-Pillow, deterministic, already-tested functions built for exactly this
job (`atlas.py`'s own docstring: "adapted from OpenAI's `hatch-pet` skill").
Reimplementing border-flood-fill chroma-keying and content-fit scaling from
scratch would violate AGENTS.md's "reuse existing behavior before writing
new code" and add real bug surface (the flood-fill trapped-pocket handling
in particular is non-trivial) for no benefit. `remove_background()` is
called with an explicit `chroma_key=(255, 0, 255)` (matching the
`_BACKGROUND` spec in `agent/pet/generate/prompts.py`) and a **widened**
threshold (130 vs. atlas.py's PNG-strip default of 90) — the source images
are JPEGs, and JPEG's DCT/chroma-subsampling introduces per-pixel noise
around a nominally-flat backdrop that a stricter PNG-tuned threshold missed
in an initial dry run near the character's dark outline.

### 2. Run

```text
$ cd /home/chegusan/SGTraining/Jorgito-worktrees/phase-1-minimal-visual-proof
$ /home/chegusan/.hermes/hermes-agent/venv/bin/python3 scripts/process_phase1_keyframes.py
processing 'idle'...
  -> assets/keyframes/processed/idle.png (192x208, RGBA)
processing 'review'...
  -> assets/keyframes/processed/review.png (192x208, RGBA)
processing 'run'...
  -> assets/keyframes/processed/run.png (192x208, RGBA)
building contact sheet...
  -> assets/keyframes/contact_sheet_phase1.png (1824x712)
```

Used the Hermes-bundled venv (`/home/chegusan/.hermes/hermes-agent/venv`)
only for its Pillow install — no Hermes runtime state (config, credentials,
`HERMES_HOME`) is touched by this script; it is pure image processing.

### 3. Background-removal quality check

Measured residual near-magenta pixels among opaque (alpha > 16) pixels in
each processed cell:

```text
idle:   18128 opaque px, 1 magenta-ish px  (0.01%)
review: 19789 opaque px, 5 magenta-ish px  (0.03%)
run:    19691 opaque px, 20 magenta-ish px (0.10%)
```

All three are well under 0.1–0.2%, consistent with a clean chroma-key
(visually confirmed too — see contact sheet). No background patch survived
as a solid remnant; the residue is a few anti-aliased edge pixels along
wing/limb outlines, not a segmentation failure.

### 4. Self-assessment (NOT the final gate — user approves visually)

Visually inspecting `assets/keyframes/contact_sheet_phase1.png` myself
(this agent can render images): all 3 cells preserve every identity
invariant from `docs/04_ASSET_SPEC.md` — crimson/burgundy body, large green
eyes with visible white, small tan horns, yellow-gold belly/neck plates and
wing membranes, curled tail, friendly expression — and each hero action
reads clearly at cell scale: `review` shows visible glasses + an open book
in a reading pose; `run` shows a visible shovel with dirt/earth accents in
a digging pose; `idle` is a calm neutral standing pose. Background is fully
transparent (checkerboard shows through) in all 3.

This is my own read, not the required approval — per the task instructions,
**the final visual-identity gate is the user's call, not this agent's**.
The user should open `assets/keyframes/contact_sheet_phase1.png` (or the PR)
and confirm F1-A (identity match to canonical) and, once installed/rendered
in a real terminal, F1-B (thinking/working readability at CLI scale — not
yet exercised in this pass, since that requires installing the cells into a
pet package and rendering, which is beyond this deterministic-processing
task).

## Tests executed

- `venv/bin/python3 scripts/process_phase1_keyframes.py` — full run, see
  §2. Exit 0, all 3 outputs produced.
- Verified each `assets/keyframes/processed/{state}.png` is exactly
  192×208 RGBA (matches the project's standard cell size).
- Residual-magenta pixel count check per processed cell (§3).
- Visual inspection of the contact sheet by this agent (§4) — informal,
  not a substitute for the user's required visual gate.
- Did not run F1-B (real-terminal readability) — no pet package was
  installed/rendered in this pass; out of scope for "process these 3
  keyframes" as scoped by the task.

## Cost

- image generations: 0 (this session did not call any image-generation
  model or API; the 3 keyframes were generated manually by the user outside
  this agent, before this task started)
- retries: 0
- approximate model/tool usage: 1 local Python script run (Pillow only, no
  network, no LLM/model calls at runtime)
- development time: ~1 session (this deterministic-processing pass)

## Files changed

- Added: `scripts/process_phase1_keyframes.py` — the deterministic
  processing script (chroma-key + fit-to-cell + contact sheet).
- Added: `assets/keyframes/processed/idle.png` (192×208 RGBA)
- Added: `assets/keyframes/processed/review.png` (192×208 RGBA)
- Added: `assets/keyframes/processed/run.png` (192×208 RGBA)
- Added: `assets/keyframes/contact_sheet_phase1.png` (1824×712, the visual
  gate artifact for the user)
- Updated: `docs/phase_results/PHASE_1_RESULT.md` (this file — supersedes
  the earlier BLOCKED write-up now that the generation-provider blocker is
  moot; the manual-keyframe path bypassed it entirely)
- Updated: `docs/08_PROJECT_STATE.md` (phase status, next action)
- Not touched: `/home/chegusan/.hermes/` (this script performs no Hermes
  runtime calls at all, only a Pillow import from the installed package's
  source tree — verified no writes occur there, same standing check as
  Phase 0).

## Problems

- The two image-provider blockers from the earlier attempt in this phase
  (OpenAI billing hard limit, OpenRouter 401) are now moot for Phase 1
  specifically, since the keyframes came from the user directly — but they
  remain unresolved and will block any *future* phase (e.g. Phase 3's
  8-row full atlas generation) that needs the native `imagegen` pipeline
  again. Worth the user fixing at least one before that phase starts.
- The JPEG source format (vs. a lossless PNG a model API would normally
  return) required loosening the chroma-key threshold from atlas.py's
  default. This worked cleanly for these 3 images (see §3) but is a
  reminder that manually-sourced JPEG keyframes are lossier raw material
  than the pipeline's native PNG/WebP output — worth keeping in mind if
  future manual keyframes come from a different tool with different JPEG
  quality/compression.
- F1-B (terminal readability at real CLI scale) was not exercised — doing
  so needs the cells installed into an actual pet package and rendered via
  `hermes pets show`, which is beyond "process these 3 raw keyframes" as
  scoped. Flagging so it isn't silently skipped for the overall Phase 1
  acceptance criteria in `docs/06_TEST_PLAN.md`.

## Bloqueantes

Ninguno para esta tarea puntual (procesamiento determinístico). El gate
visual final (F1-A identidad + F1-B legibilidad en terminal real) sigue
pendiente de aprobación del usuario — eso no es un bloqueante técnico, es
el paso de aprobación explícitamente reservado al usuario por la tarea.

## Decision

continue

## Next phase/task

1. Usuario revisa `assets/keyframes/contact_sheet_phase1.png` (adjunto al
   PR #1) y aprueba/rechaza F1-A (identidad) visualmente.
2. Si aprueba: F1-B (legibilidad en terminal real) requeriría instalar estas
   3 celdas en un paquete de pet de prueba (atlas parcial, como ya arma
   `scripts/generate_phase1.py` a partir de frames) y renderizarlo con
   `hermes pets show --mode unicode` en el perfil aislado
   `HERMES_HOME=/home/chegusan/.hermes-jorgito-test` — no incluido en esta
   tarea, que se limitó explícitamente al procesamiento determinístico +
   contact sheet.
3. Antes de la Fase 3 (atlas completo de 8 filas), resolver al menos uno de
   los bloqueantes de proveedor de imagen (OpenAI billing / credencial de
   OpenRouter) si esa fase vuelve a depender del pipeline nativo de
   generación en lugar de más keyframes manuales.
