# Phase Result

## Phase

Phase 3 — Deterministic processing of 5 additional manually-generated
keyframes (`waiting`, `failed`, `jump`, `wave`, `running-right`)

## Status

**PASS** (self-assessment; visual gate — identity + per-pose legibility —
still pending the user's actual approval on
`assets/keyframes/contact_sheet_phase3.png`, same two-step process as
Phase 1: this agent's own read is not the final call).

## Evidence

### 0. Generation path: 100% manual, 0 tokens/GPU spent by this session

All 5 raw keyframes were generated **manually by the user**, outside this
agent session, via local ComfyUI with `assets/reference/jorgito_canonical.png`
as the grounding reference — same approach and same magenta chroma-key
convention as Phase 1's 3 keyframes. They arrived already committed to
`assets/keyframes/raw/{waiting,failed,jump,wave,running-right}.jpeg`
(commit `0feac60`, 1984×2144 JPEG each, confirmed by inspection). This
phase covers only the deterministic processing of those 5 already-provided
raw images — no image-generation model or API call was made by this agent
in this session, matching the task's "cero tokens de API, cero GPU"
framing.

### 1. Method: reused Phase 1's deterministic processing, factored into a shared module

Rather than duplicating Phase 1's chroma-key/fit-to-cell/contact-sheet
logic into a second near-identical script, that logic was extracted into a
new shared module, **`scripts/keyframe_processing.py`**, and both phase
scripts became thin wrappers over it:

- `scripts/process_phase1_keyframes.py` — unchanged behavior (regression-
  verified, see §2), now calling the shared module with `STATES =
  ["idle", "review", "run"]`.
- `scripts/process_phase3_keyframes.py` (new) — calls the same shared
  module with `STATES = ["waiting", "failed", "jump", "wave",
  "running-right"]`.

The shared module still reuses Hermes's own
`agent.pet.generate.atlas.remove_background()` /
`atlas._fit_to_cell()` (same reuse rationale as Phase 1 — pure-Pillow,
deterministic, already handles this exact magenta-backdrop format; not
reimplemented here) and adds the same JPEG-tolerant chroma threshold and
contact-sheet composition Phase 1 added on top of `atlas.py`.

**Generalization choice:** a parameterized-by-state-list module (one
function per pipeline step, phase scripts pass in `STATES` +
`chroma_key`) rather than hardcoding a 3- or 5-item list, or a second
copy-pasted script — this keeps the chroma-key/fit-to-cell/contact-sheet
code in exactly one place for however many future phases add more manually-
sourced keyframes (e.g. `running-left`'s eventual atlas-assembly phase
won't need this module again since it's a mirror operation, not a new
raw-image process, but any *new* pose keyframe would reuse it as-is).

### 2. Regression check: Phase 1 outputs byte-identical after the refactor

Before touching Phase 3, re-ran the refactored `process_phase1_keyframes.py`
and diffed its outputs against the already-committed, user-approved
(`"Están perfectos"`) Phase 1 assets:

```text
$ venv/bin/python3 scripts/process_phase1_keyframes.py
processing 'idle'...   -> assets/keyframes/processed/idle.png (192x208, RGBA)
processing 'review'... -> assets/keyframes/processed/review.png (192x208, RGBA)
processing 'run'...    -> assets/keyframes/processed/run.png (192x208, RGBA)
building contact sheet... -> assets/keyframes/contact_sheet_phase1.png (1824x712)
$ git status --short assets/keyframes/processed/idle.png assets/keyframes/processed/review.png \
    assets/keyframes/processed/run.png assets/keyframes/contact_sheet_phase1.png
(no output — zero diff, byte-identical to the committed, approved files)
```

This confirms the extraction into `keyframe_processing.py` is a pure
refactor for Phase 1 (same `chroma_key=(255, 0, 255)` default, same
threshold, same fit/contact-sheet code path) — nothing about the already-
approved Phase 1 assets changed.

### 3. Problem found + fix: Phase 3's raw backdrop is not pure magenta

Running the naive port of Phase 1's method (fixed
`chroma_key=(255, 0, 255)`) against the 5 new raw JPEGs produced **badly
broken output** — most of each cell still opaque background, not a minor
fringe issue:

```text
waiting        13315 opaque px,    29 magenta-ish px  (0.22%)
failed         15184 opaque px,  3864 magenta-ish px  (25.45%)
jump           35839 opaque px, 26340 magenta-ish px  (73.50%)
wave           35854 opaque px, 26783 magenta-ish px  (74.70%)
running-right  35854 opaque px, 27309 magenta-ish px  (76.17%)
```

Root cause, found by sampling raw corner-pixel colors directly: Phase 1's
raw backdrop was near-pure magenta (`idle` corners ≈ `(254, 1, 249)`,
distance ≈6 from `(255, 0, 255)`), but Phase 3's ComfyUI-exported JPEGs
have a backdrop shifted well away from pure magenta — e.g. `jump` corners
≈ `(230, 35, 199)` (distance ≈66), `running-right` corners ≈
`(220, 47, 179)` (distance ≈94). This is a **systematic color shift** (a
different, still-fairly-uniform shade of magenta), not JPEG noise around
the right color — widening `JPEG_CHROMA_THRESHOLD` (the fix Phase 1 used
for its noise problem) does not touch this, because
`atlas.remove_background()`'s fast path for strongly-saturated keys keys
off a separate, **hardcoded** internal tolerance (`_near_key_mask(...,
tol=48)`) around whatever `chroma_key` is passed in, not off the
`threshold` argument — confirmed by reading `atlas.py`'s source
(`agent/pet/generate/atlas.py:110,179-183`). A `chroma_key` fixed at
`(255, 0, 255)` is simply the wrong center for that fixed-radius mask on
these images.

**Fix:** pass `chroma_key=None` for the Phase 3 states, letting
`atlas.remove_background()` fall back to its own built-in
`_dominant_corner_color()` detection — sampling each image's *actual*
corner color instead of assuming the ideal one. This is existing `atlas.py`
behavior (`key = chroma_key or _dominant_corner_color(rgba)`), not new code
written for this phase. Re-measured after the fix:

```text
waiting        18989 opaque px,    0 magenta-ish px (0.00%)
failed         19193 opaque px,    0 magenta-ish px (0.00%)
jump           20489 opaque px,    0 magenta-ish px (0.00%)
wave           19444 opaque px,    0 magenta-ish px (0.00%)
running-right  18856 opaque px,    0 magenta-ish px (0.00%)
```

All 5 came out at **0.00% residue** — cleaner than Phase 1's own 0.01-0.10%
range, not worse. `scripts/keyframe_processing.py`'s `process_keyframe()`
now takes a `chroma_key` parameter (default `(255, 0, 255)`, preserving
Phase 1's exact behavior per §2) so each phase script can choose the right
key strategy for its own raw material; see that function's docstring for
the full detail captured above.

### 4. Run

```text
$ cd /home/chegusan/SGTraining/Jorgito-worktrees/phase-3-comfyui-keyframes
$ /home/chegusan/.hermes/hermes-agent/venv/bin/python3 scripts/process_phase3_keyframes.py
processing 'waiting'...
  -> assets/keyframes/processed/waiting.png (192x208, RGBA)
processing 'failed'...
  -> assets/keyframes/processed/failed.png (192x208, RGBA)
processing 'jump'...
  -> assets/keyframes/processed/jump.png (192x208, RGBA)
processing 'wave'...
  -> assets/keyframes/processed/wave.png (192x208, RGBA)
processing 'running-right'...
  -> assets/keyframes/processed/running-right.png (192x208, RGBA)
building contact sheet...
  -> assets/keyframes/contact_sheet_phase3.png (3024x712)
```

Used the same Hermes-bundled venv as Phase 1
(`/home/chegusan/.hermes/hermes-agent/venv`), only for its Pillow install —
no Hermes runtime state touched (see §6).

### 5. Self-assessment (NOT the final gate — user approves visually)

Visually inspecting `assets/keyframes/contact_sheet_phase3.png` (this agent
can render images): all 5 cells preserve the identity invariants from
`docs/04_ASSET_SPEC.md` (crimson/burgundy body, tan horns, yellow-gold
belly/wing membranes, curled tail) and each pose reads clearly at cell
scale:

- `waiting`: calm, relaxed seated pose, green eyes open forward — reads as
  quiet/idle-adjacent waiting, not alarmed or active.
- `failed`: surprised/confused open-mouth expression with a small puff
  above the head — reads as a mildly comic "something went wrong" beat,
  distinct from `waiting`'s calm.
- `jump`: both arms raised, wide joyful open-mouth smile, dynamic
  off-ground-reading pose — reads clearly as a celebratory jump.
- `wave`: one arm raised at head height, smiling — reads clearly as a
  greeting wave, distinct from `jump`'s two-arms-up pose.
- `running-right`: side-profile dynamic running stance, body/legs extended
  facing right — reads clearly as running toward the right.

Background is fully transparent (checkerboard shows through, 0.00%
magenta residue per §3) in all 5, same visual style/scale as
`contact_sheet_phase1.png`.

This is this agent's own read, not the required approval — same two-step
process as Phase 1 (§4 in `PHASE_1_RESULT.md`): pending the user opening
`assets/keyframes/contact_sheet_phase3.png` (attached to this phase's PR)
and confirming identity + per-action legibility.

### 6. Real `~/.hermes` isolation check

Same hard restriction as Phase 1, re-verified for this session even though
this task is pure image processing and doesn't touch pet/store state at
all:

| check | before | after |
|---|---|---|
| `~/.hermes/config.yaml` mtime | `2026-08-15 10:38:33` | `2026-08-15 10:38:33` (unchanged) |
| `~/.hermes/pets/` contents | empty | empty |
| `~/.hermes/active_profile` | absent | absent |

Confirmed untouched. This script only imports `agent.pet.generate.atlas`
(pure Pillow functions) from `/home/chegusan/.hermes/hermes-agent`'s source
tree — read-only import, no `HERMES_HOME`, no store/config access.

## Tests executed

- `venv/bin/python3 scripts/process_phase1_keyframes.py` (post-refactor) —
  full run, outputs byte-identical (`git status --short` empty) to the
  already-committed, user-approved Phase 1 assets (§2).
- `venv/bin/python3 scripts/process_phase3_keyframes.py` — full run, all 5
  outputs produced at 192×208 RGBA (§4).
- Residual-magenta pixel count check per processed cell, before and after
  the `chroma_key=None` fix (§3) — before: 0.22-76.17% (broken); after:
  0.00% across all 5.
- Raw-corner-pixel sampling on all 8 raw keyframes (Phase 1's 3 + Phase 3's
  5) to root-cause the backdrop color shift (§3).
- Visual inspection of `contact_sheet_phase3.png` by this agent (§5) —
  informal, pending the user's actual approval (this phase's real gate).
- Real `~/.hermes` isolation check, before and after (§6 table) —
  untouched.

## Cost

- image generations: 0 (all 5 raw keyframes were generated manually by the
  user outside this session, per the task framing — no image-generation
  model or API call made by this agent)
- retries: 0
- approximate model/tool usage: 2 local Python script runs (Phase 1
  regression re-run, Phase 3 processing run) + several scratch/inspection
  scripts (corner-color sampling, residual-magenta measurement) — all
  Pillow + Hermes source imports only, no network, no LLM/model calls at
  runtime
- development time: 1 session

## Files changed

- Added: `scripts/keyframe_processing.py` — shared chroma-key/fit-to-cell/
  contact-sheet module, extracted from Phase 1's script so Phase 1 and
  Phase 3 (and any future phase) don't duplicate that logic.
- Modified: `scripts/process_phase1_keyframes.py` — now a thin wrapper over
  `keyframe_processing.py`; behavior regression-verified byte-identical to
  the pre-refactor version (§2).
- Added: `scripts/process_phase3_keyframes.py` — Phase 3's thin wrapper,
  `STATES = ["waiting", "failed", "jump", "wave", "running-right"]`,
  `chroma_key=None` (auto-detect; see §3).
- Added: `assets/keyframes/processed/waiting.png` (192×208 RGBA)
- Added: `assets/keyframes/processed/failed.png` (192×208 RGBA)
- Added: `assets/keyframes/processed/jump.png` (192×208 RGBA)
- Added: `assets/keyframes/processed/wave.png` (192×208 RGBA)
- Added: `assets/keyframes/processed/running-right.png` (192×208 RGBA)
- Added: `assets/keyframes/contact_sheet_phase3.png` (3024×712, the visual
  gate artifact for the user)
- Added: `docs/phase_results/PHASE_3_RESULT.md` (this file)
- Updated: `docs/08_PROJECT_STATE.md` (phase status, next action)
- Not touched: `/home/chegusan/.hermes/` — verified untouched before and
  after this session (§6 table); this task never sets `HERMES_HOME` or
  touches pet-store state, only imports pure-Pillow functions from
  `atlas.py`.
- Not touched: `running-left` — intentionally deferred, see "Problems"
  below.

## Problems

- Phase 3's raw backdrop is not pure magenta the way Phase 1's was — a
  systematic color shift (not just JPEG noise), root-caused and fixed via
  `chroma_key=None` auto-detection (§3). Worth flagging for any *future*
  manually-sourced keyframe batch: don't assume a fixed
  `chroma_key=(255, 0, 255)` will keep working just because the source tool
  and general workflow (ComfyUI + magenta backdrop + canonical reference)
  are unchanged — the exact exported shade can still drift between
  generation sessions/tools, and `atlas.py`'s per-image auto-detection
  (`chroma_key=None`) is a cheap, already-available way to make the keying
  step robust to that instead of hand-tuning a threshold per batch.
- `running-left` is **intentionally not generated or processed in this
  phase**, per the task's explicit scope. It is deferred to a future
  full-atlas-assembly phase (Phase 4 in the task's own framing), where it
  will be derived by horizontal mirror of `running-right.png` rather than
  generated or chroma-keyed separately — no new raw keyframe or ComfyUI
  generation needed for it.
- The two image-provider blockers noted in `PHASE_1_RESULT.md` (OpenAI
  billing hard limit, OpenRouter 401) remain unresolved but are moot for
  this phase too, since all 5 keyframes came from the user's manual ComfyUI
  workflow, not Hermes's native `imagegen` pipeline.

## Bloqueantes

**Ninguno bloquea el cierre técnico de esta tarea de procesamiento.** Todo
el trabajo determinístico pedido (procesar los 5 keyframes, medir residuo
magenta, armar el contact sheet, verificar `~/.hermes` intacto, documentar)
está hecho y evidenciado arriba.

Como en Fase 1, queda la aprobación visual del usuario como el gate real
(no una decisión unilateral de este agente):

> ¿`assets/keyframes/contact_sheet_phase3.png` aprueba el gate visual de
> Fase 3 — identidad consistente con `jorgito_canonical.png` y legibilidad
> de cada acción (waiting = quieto/relajado, failed = confundido/gracioso,
> jump = salto celebratorio, wave = saludo, running-right = corriendo hacia
> la derecha) — o hay algún estado que necesita otra iteración manual en
> ComfyUI antes de continuar?

## Decision

continue

## Next phase/task

1. **Pendiente: aprobación visual del usuario** sobre
   `contact_sheet_phase3.png` (mismo proceso que F1-A en Fase 1).
2. `running-left` queda explícitamente diferido a una fase futura de
   ensamblado de atlas completo (Phase 4), donde se deriva por espejo
   horizontal de `running-right.png` — no requiere nueva generación manual.
3. Una vez aprobados los 8 estados no-espejados (3 de Fase 1 + 5 de Fase 3),
   la siguiente fase natural es el ensamblado del atlas completo de 8/9
   filas (incluyendo el espejo de `running-left`) y su empaquetado como pet
   real de Hermes, siguiendo el mismo patrón que
   `scripts/build_phase1_test_pet.py` mostró para un subconjunto de
   estados.
