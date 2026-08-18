# Phase Result

## Phase

Phase 4 — Assemble and validate the full 9-row atlas (`idle`, `running-right`,
`running-left`, `waving`, `jumping`, `failed`, `waiting`, `running`, `review`)
and install it as a real Hermes pet in the **isolated** test profile only.

## Status

**PASS** (self-assessment on identity/legibility; validation and installation
gates are objective and both PASS — see below). Visual gate for the final
contact sheet still pending the user's actual approval, same two-step process
as Phases 1 and 3.

## Evidence

### 0. `running-left` derivation: mirror, not generation

`docs/03_INTERFACES_AND_CONTRACTS.md`'s asset-transform interface names
`mirror_frame(image) -> image` as the intended primitive, and
`agent/pet/generate/atlas.py` already ships exactly that as
`mirror_frames(frames)`, with a docstring stating it exists specifically
*"to derive `running-left` from an approved `running-right` row"*. Reused
directly (no reimplementation) in `scripts/full_atlas.py:derive_running_left()`.
Zero image generation, zero GPU, deterministic Pillow `transpose(FLIP_LEFT_RIGHT)`
under the hood.

```text
$ venv/bin/python3 scripts/build_full_atlas.py
deriving running-left (mirror of running-right)...
  -> assets/keyframes/processed/running-left.png (192x208, RGBA)
```

Visually confirmed in the contact sheet (§3 below): wings/tail/dragon body
mirror cleanly left↔right with no impossible asymmetry, no stray text, no
duplicated/ghost props — satisfies `docs/06_TEST_PLAN.md`'s P3.3.

### 1. Method: reused Hermes's real atlas pipeline, not an invented format

Per the task's correction (documented in `docs/phase_results/PHASE_0_RESULT.md`,
"Problems" §): the real atlas is **not** a fixed 8×9/1536×1872 spec applied
blindly — it's `agent.pet.generate.atlas.py`'s own `ROW_SPECS` (state name,
row index, **per-row frame count**), which *is* 9 rows / 8-column-max /
1536×1872 by construction for anything built through the generator, but with
per-state frame counts that vary (idle=6, running-right=8, running-left=8,
waving=4, jumping=5, failed=8, waiting=6, running=6, review=6) — not a
uniform 8 columns everywhere.

New module `scripts/full_atlas.py` (88 lines, single responsibility: build +
validate the full atlas) does no spritesheet-geometry work itself — it only:

- Maps our processed-keyframe filenames (Phase 1/3 naming) onto
  `atlas.ROW_SPECS`'s row names (`run`→`running`, `wave`→`waving`,
  `jump`→`jumping`, others 1:1), matching `docs/03`'s Jorgito semantic
  mapping table exactly.
- Repeats each state's single static-pose cell across that row's *real* frame
  count from `ROW_SPECS` (not a hardcoded 6) — same "steady repeat plays back
  as held still" approach `scripts/build_phase1_test_pet.py` used for a
  3-state subset in Phase 1, now applied uniformly via the real per-row counts
  instead of copy-pasted constants.
- Calls `atlas.compose_atlas(frames_by_state)` — Hermes's own atlas packer —
  to produce the actual `Image`.
- Calls `atlas.validate_atlas(...)` — Hermes's own validator, per Phase 0's
  explicit recommendation (§5 of `PHASE_0_RESULT.md`), not a project-invented
  checker.

Two thin wrapper scripts sit on top, each with one job:

- `scripts/build_full_atlas.py` (pure image processing, no `HERMES_HOME`,
  no pet-store writes) — builds the atlas, runs the validator, writes
  evidence files, and builds the final contact sheet (reusing
  `keyframe_processing.build_contact_sheet` from Phase 3 rather than
  duplicating contact-sheet code).
- `scripts/install_full_atlas_pet.py` (requires `HERMES_HOME`, refuses to run
  against the real `~/.hermes` — same guard `build_phase1_test_pet.py` used)
  — rebuilds the atlas deterministically, re-validates before writing
  anything, and calls `agent.pet.store.register_local_pet()`, the same
  local-pet registration path Hermes's own `/hatch` command uses.

No new spritesheet format, no hand-rolled `pet.json` schema — both come
straight from Hermes's own `atlas.py` / `store.py`.

### 2. Run: build + validate (pure processing)

```text
$ venv/bin/python3 scripts/build_full_atlas.py
deriving running-left (mirror of running-right)...
  -> assets/keyframes/processed/running-left.png (192x208, RGBA)
composing full 9-row atlas via agent.pet.generate.atlas.compose_atlas()...
  -> assets/keyframes/atlas_full.png (1536x1872)
validating via agent.pet.generate.atlas.validate_atlas()...
{
  "ok": true,
  "width": 1536,
  "height": 1872,
  "errors": [],
  "warnings": [],
  "filled_states": [
    "idle", "running-right", "running-left", "waving", "jumping",
    "failed", "waiting", "running", "review"
  ]
}
  -> assets/keyframes/atlas_full_validation.json
building final 9-state contact sheet...
  -> assets/keyframes/contact_sheet_phase4_full.png (5424x712)
```

**P4.1 (upstream validator passes): PASS.** `validate_atlas()` — Hermes's
real, unmodified validator (`agent/pet/generate/atlas.py:1078`) — returns
`ok: true` with correct geometry (`1536×1872`, matching `ATLAS_WIDTH ×
ATLAS_HEIGHT` for the 9-row `ROW_SPECS`), all 9 states filled, **zero
errors, zero warnings**. This checks exact size, per-cell occupancy, the
multi-pose/collapsed-row outlier guards, and the "no transparent-pixel RGB
residue" invariant — all in one call, none reimplemented by this project.

### 3. Self-assessment: identity + per-pose legibility (full-resolution contact sheet)

`assets/keyframes/contact_sheet_phase4_full.png` — all 9 processed cells at
3x scale, labeled with their real `ROW_SPECS` row names:

- `idle`: calm neutral standing pose — same cell reused from Phase 1
  (user-approved, "Están perfectos").
- `running-right` / `running-left`: side-profile running stance, facing
  right / left respectively — the mirror preserves the dynamic running pose,
  wing position, and tail curl with no artifacts.
- `waving`: one arm raised, smiling — greeting reads clearly.
- `jumping`: both arms up, open-mouth joyful expression, off-ground pose —
  celebratory jump reads clearly, distinct from `waving`.
- `failed`: surprised/confused expression, small puff above the head — reads
  as a friendly "something went wrong" beat.
- `waiting`: calm seated pose — distinct from `idle`'s standing pose.
- `running` (the WORKING state, not locomotion — per `atlas.py`'s own
  docstring: *"`running` is the working state (in-place processing), NOT
  locomotion"*): visible shovel + dirt/earth accents — matches
  `docs/08_PROJECT_STATE.md`'s confirmed working=shovel+earth convention.
- `review`: visible glasses + held book — matches the confirmed
  thinking=book+glasses convention.

All 9 preserve every identity invariant from `docs/04_ASSET_SPEC.md`
(crimson/burgundy body, tan horns, yellow-gold belly/wings, curled tail,
friendly expression). This is this agent's own read, not the required
approval — same two-step gate as Phases 1 and 3, pending the user opening
`contact_sheet_phase4_full.png` (attached to this phase's PR).

### 4. Install into the isolated profile only

```text
$ HERMES_HOME=/home/chegusan/.hermes-jorgito-test \
  venv/bin/python3 scripts/install_full_atlas_pet.py
HERMES_HOME=/home/chegusan/.hermes-jorgito-test
validate_atlas(): ok=True, filled_states=[idle, running-right, running-left,
  waving, jumping, failed, waiting, running, review]
registered pet 'jorgito' -> /home/chegusan/.hermes-jorgito-test/pets/jorgito/spritesheet.webp
  exists=True generated=True
$ HERMES_HOME=/home/chegusan/.hermes-jorgito-test hermes pets select jorgito
✓ active pet set to Jorgito (display.pet.slug=jorgito, enabled)
```

Real on-disk `pet.json` produced by `store.register_local_pet()` (not
hand-written by this project):

```json
{
  "id": "jorgito",
  "displayName": "Jorgito",
  "description": "Jorgito -- full 9-state atlas (Phase 4): idle / running-right / running-left / waving / jumping / failed / waiting / running / review",
  "spritesheetPath": "spritesheet.webp",
  "createdBy": "generator"
}
```

`spritesheet.webp` measured back with Pillow: `1536x1872 RGBA`, matching the
validated atlas exactly. `hermes pets doctor` after install:

```text
petdex doctor
  pets dir:        /home/chegusan/.hermes-jorgito-test/pets
  installed:       3 (boba, jorgito, jorgito-test)
  display.pet.enabled:     True
  display.pet.slug:        jorgito
  active (resolved):       jorgito
  display.pet.render_mode: auto
  detected graphics:       unicode
  effective mode (TTY):    off
  ✓ ready
```

**P4.2 (Hermes loads the pet without runtime modification): PASS.** No
`agent/pet/*` source file was edited. The store, renderer, and CLI resolved
and rendered `jorgito` exactly as they would any petdex-installed pet.

### 5. Rendering evidence: real Hermes CLI, real TTY, all 9 states

This sandboxed shell has no TTY and `hermes pets show`'s `resolve_mode()`
hard-codes `off` when `stdout.isatty()` is `False` — same constraint as
Phase 1's F1-B. Used `script -qec "..." <logfile>` to fake a pty so the
actual, unmodified CLI path runs end-to-end for every one of the 9 real
atlas row names (confirmed via source read of `hermes_cli/pets.py`: `--state`
takes the raw string and passes it straight to `renderer.frame_count()` /
`renderer.frame()`, which resolve it via `state_row_index()` against
`CODEX_STATE_ROWS` — so `running-right`/`running-left` work even though
they aren't in the short `PetState` enum the CLI's own `--help` text
enumerates, the same help-text gap Phase 0 already flagged for `waiting`):

```text
$ for s in idle running-right running-left waving jumping failed waiting running review; do
    script -qec "HERMES_HOME=/home/chegusan/.hermes-jorgito-test hermes pets show jorgito --state $s --once --mode unicode" \
      assets/keyframes/terminal_render_phase4/$s.script.txt
  done

== idle          == exit=0  lines=59  bytes=25482
== running-right == exit=0  lines=59  bytes=26247
== running-left  == exit=0  lines=59  bytes=26246
== waving        == exit=0  lines=41  bytes=17410
== jumping       == exit=0  lines=50  bytes=22342
== failed        == exit=0  lines=59  bytes=25928
== waiting       == exit=0  lines=59  bytes=24663
== running       == exit=0  lines=59  bytes=27285
== review        == exit=0  lines=59  bytes=26732
```

All 9 succeeded (`exit=0`), each producing 17–27KB of valid truecolor-ANSI
half-block escape output — real pixel data read from the installed
spritesheet and drawn, not a placeholder. `waving`/`jumping` produce fewer
lines than the rest (41/50 vs. 59) because the renderer trims trailing blank
columns per state and steps through each state's real frame count
(`waving`=4, `jumping`=5 vs. 6 for the others, capped at
`FRAMES_PER_STATE`=6) — this is `render.py`'s documented per-row trimming
behavior working correctly on our variable-frame-count atlas, not a defect.

### 6. Rendering evidence: rasterized preview, real default scale (16 cols)

Raw ANSI isn't visually inspectable, so `scripts/render_full_atlas_pet.py`
calls `agent.pet.render.PetRenderer` directly (same encoder as §5) at the
project's actual default `display.pet.scale` (0.33 → 16 columns, per
`agent/pet/constants.py`), producing a magnified PNG per state and a combined
labeled contact sheet:
`assets/keyframes/terminal_render_phase4/contact_sheet_terminal_phase4.png`.

Confirms `renderer.frame_count()` per state matches §5's exact line-count
pattern: `waving`=4, `jumping`=5, all others=6 (`FRAMES_PER_STATE` cap).

Consistent with Phase 1's already-documented finding (`PHASE_1_RESULT.md`
§7–§9): at this real default unicode-fallback scale, the 9 states are **not**
reliably distinguishable from each other — identity (color palette) survives
but pose-differentiating detail (shovel, book/glasses, wave vs. jump arm
position, run-left vs. run-right facing) collapses at the 16-column floor.
This is the same pre-existing, documented Hermes rendering-floor
characteristic (`UNICODE_MIN_COLS` in `agent/pet/constants.py`) already
flagged as a non-blocking open product decision in Phase 1's "Bloqueantes" —
not a new defect introduced by this phase's atlas assembly. The
high-resolution `contact_sheet_phase4_full.png` (§3) is the correct artifact
for the identity/legibility visual gate; this terminal-scale render is
supplementary evidence of real CLI behavior, same role Phase 1's
`compare_kitty_scale033.png` played.

### 7. Real `~/.hermes` isolation check (hard restriction)

| check | session start | after all Phase 4 work |
|---|---|---|
| `~/.hermes/config.yaml` content (md5) | `66684dd3b378e4584ab08ab097024ed4` | `66684dd3b378e4584ab08ab097024ed4` (unchanged) |
| `~/.hermes/config.yaml` mtime | not captured directly at session start (only the parent dir's mtime was, by mistake) | `2026-08-15 10:38:33` — predates this session entirely |
| `~/.hermes/pets/` contents | empty (0 entries) | empty (0 entries) |
| `~/.hermes/pets/` mtime | — | `ago 15 10:38` — predates this session, confirming no write ever landed there |
| `~/.hermes/active_profile` | absent | absent |

Note on methodology: the very first isolation snapshot this session
mistakenly `stat`'d the `~/.hermes` *directory* itself (whose mtime
naturally drifts, since it's the live profile with an active gateway,
sessions, and logs constantly writing — unrelated to this project) instead
of `config.yaml`. Caught and corrected before drawing any conclusion:
`config.yaml`'s own content hash and mtime, and `pets/`'s own mtime, are the
actual protected invariants, and all three are confirmed unchanged /
predate this session. Every pet install/select/render call in this session
used `HERMES_HOME=/home/chegusan/.hermes-jorgito-test` exclusively; nothing
in `scripts/full_atlas.py` or `scripts/build_full_atlas.py` touches
`HERMES_HOME` or pet-store state at all (pure Pillow + `atlas.py` import,
same isolation pattern as Phase 3).

## Tests executed

- `venv/bin/python3 scripts/build_full_atlas.py` — full run: mirror
  derivation, atlas composition, validation, contact-sheet build (§2).
- `agent.pet.generate.atlas.validate_atlas()` on the composed atlas — `ok:
  true`, correct `1536×1872` geometry, all 9 `filled_states`, 0
  errors/warnings (§2, P4.1).
- Visual inspection of `contact_sheet_phase4_full.png` by this agent (§3) —
  informal, pending the user's actual approval (this phase's real gate).
- `HERMES_HOME=... venv/bin/python3 scripts/install_full_atlas_pet.py` —
  pet registered, re-validated before write, `exists=True generated=True`
  (§4).
- `HERMES_HOME=... hermes pets select jorgito` — active pet set (§4, P4.2).
- `HERMES_HOME=... hermes pets doctor` — `✓ ready`, `jorgito` resolved
  active (§4).
- `script -qec "HERMES_HOME=... hermes pets show jorgito --state <s> --once --mode unicode" <log>`
  × 9 (all real `CODEX_STATE_ROWS` row names) — real CLI path, real
  (faked-pty) TTY, all `exit=0` (§5).
- `HERMES_HOME=... venv/bin/python3 scripts/render_full_atlas_pet.py` —
  direct-API render at the real default scale for all 9 states, produced
  the final labeled terminal-scale contact sheet (§6).
- Real `~/.hermes` isolation check, before and after (§7 table) — unchanged
  content/mtime on the protected files, corrected methodology noted.

## Cost

- image generations: 0 (all source keyframes came from Phases 1/3's already-
  approved manual generations; this phase only mirrors, composes, and
  validates — no model/API call)
- retries: 0
- approximate model/tool usage: 3 local Python script runs (build+validate,
  install, terminal render) + 11 `hermes`/CLI invocations (select, doctor,
  9× `pets show` under a faked TTY) — all deterministic Pillow/Hermes-source
  calls, no network, no LLM/model inference at runtime
- development time: 1 session

## Files changed

- Added: `scripts/full_atlas.py` — core atlas-assembly module (mirror
  derivation, frame-count-aware row building, thin wrappers around
  `atlas.compose_atlas()` / `atlas.validate_atlas()`).
- Added: `scripts/build_full_atlas.py` — pure-processing script: builds +
  validates the atlas, writes evidence, builds the final contact sheet.
- Added: `scripts/install_full_atlas_pet.py` — isolated-profile-only
  installer via `agent.pet.store.register_local_pet()`.
- Added: `scripts/render_full_atlas_pet.py` — real-default-scale terminal
  render evidence + labeled contact sheet.
- Added: `assets/keyframes/processed/running-left.png` (192×208 RGBA,
  mirror of `running-right.png`).
- Added: `assets/keyframes/atlas_full.png` (1536×1872 RGBA — the composed
  atlas image, evidence only; the pet-store copy is the lossless WebP under
  the isolated `HERMES_HOME`, not committed to this repo).
- Added: `assets/keyframes/atlas_full_validation.json` — raw
  `validate_atlas()` output.
- Added: `assets/keyframes/contact_sheet_phase4_full.png` (5424×712 — the
  visual gate artifact for the user).
- Added: `assets/keyframes/terminal_render_phase4/` — real-CLI + real-scale
  evidence: `{state}.script.txt` ×9, `{state}_realsize_preview.png` ×9,
  `contact_sheet_terminal_phase4.png`.
- Added: `docs/phase_results/PHASE_4_RESULT.md` (this file).
- Updated: `docs/08_PROJECT_STATE.md` (phase status, next action).
- Not touched: `/home/chegusan/.hermes/` — verified untouched before and
  after this session (§7); every pet install/select/render call used
  `HERMES_HOME=/home/chegusan/.hermes-jorgito-test` exclusively.
- Not touched (intentionally, out of scope for this phase): any real-profile
  install — that is Phase 5, dispatched separately after this phase's visual
  gate is approved.

## Problems

- First isolation snapshot this session accidentally measured the `~/.hermes`
  *directory's* mtime (which drifts naturally — it's the live, actively-used
  profile) instead of `config.yaml`'s own mtime. Caught before drawing any
  conclusion and corrected in §7 with the actual protected-file checks
  (content hash + own mtime + `pets/` emptiness), all of which confirm
  isolation held. Not a data-integrity issue, just a methodology note for
  future phases: stat the specific protected files/dirs, not their parent.
- Same pre-existing, already-documented (Phase 1) unicode-fallback
  legibility floor applies to the full 9-state atlas at the real default
  scale (§6) — not a new problem, not this phase's to fix (it's a
  cross-cutting `display.pet.scale` product decision, same open item
  already on record in `PHASE_1_RESULT.md`'s "Bloqueantes").
- `running-right`/`running-left` are not listed in `hermes pets show
  --help`'s `--state` text (only the short `PetState` enum names are), but
  they work correctly when passed explicitly — confirmed by reading
  `hermes_cli/pets.py` (no validation against the enum, the raw string
  passes straight to `state_row_index()`) and by the 9/9 successful CLI
  runs in §5. Same category of cosmetic help-text gap Phase 0 already
  flagged for `waiting`; not a functional blocker.

## Bloqueantes

**Ninguno bloquea el cierre técnico de esta fase.** El ensamblado
determinístico, la validación con el validador real de Hermes, la
instalación en el perfil aislado, y la evidencia de render con el comando
real de Hermes para los 9 estados están hechos y documentados arriba. El
perfil `~/.hermes` real quedó verificado intacto (§7).

Queda, como en las Fases 1 y 3, la aprobación visual del usuario como gate
real (no una decisión unilateral de este agente):

> ¿`assets/keyframes/contact_sheet_phase4_full.png` aprueba el gate visual
> final de Fase 4 — identidad consistente con `jorgito_canonical.png` a
> través de los 9 estados, incluyendo que `running-left` (el espejo) se vea
> natural y sin artefactos — o hay algo que necesita otra iteración antes de
> avanzar a la Fase 5 (instalación en el perfil real `~/.hermes`, que se
> despacha por separado)?

## Correction (post-merge-review): rows were not actually animated

A later hash-level review of the installed `spritesheet.webp` found that
`build_frames_by_state()` (the code documented in §1 above) built each row as
`[cell] * row_counts[row]` — Python list-repetition of the **same** `Image`
object/pixels, not distinct copies. SHA-256 over every cell in the installed
atlas confirmed it: **each of the 9 rows had exactly 1 unique hash across all
its columns.** The atlas passed `validate_atlas()` (geometry/occupancy/
residue checks, which don't compare cell content across columns) and looked
correct in the static contact sheet (§3), but on a real Hermes render every
state was a frozen single pose — nothing animated, contrary to the phase's
own framing of "steady repeat plays back as held still."

### What changed

`scripts/full_atlas.py` (now 131 lines, still comfortably inside AGENTS.md's
100–300 line module budget):

- Added `_vary(cell, i, n) -> Image.Image`: for column `i` of `n`, returns a
  **copy** of `cell` (never the same object) with a deterministic
  sine-phase nudge — vertical bob (±3px), tilt (±1.5°), and breathing scale
  (±2%) — so a row plays back as a subtle bob/breathe loop instead of a
  frozen repeat. Column `i=0` is returned untouched (`cell.copy()`, no
  transform) so the approved reference keyframe pose is preserved exactly.
  Uses `Image.Resampling.NEAREST` for both the rotation and the resize step,
  matching `atlas._fit_to_cell`'s own resample choice (documented there as
  the pixel-art-safe one — LANCZOS/BILINEAR would blur the hard sprite
  edges).
- `build_frames_by_state()` now calls `_vary(cell, i, row_counts[row])` per
  column instead of `[cell] * row_counts[row]`. `running-left` is unaffected
  by this call site — it still derives from `mirror_frames()` on the base
  `running-right` cell (§0, untouched) — and gets its own `_vary` pass with
  the same `n`/phase function as `running-right`, so both directional rows
  bob in the same rhythm.
- Zero new images generated, zero API/model calls (`AGENTS.md`'s cost
  discipline: "transform" ranks above "generate" in image-work priority, and
  this is a pure deterministic Pillow transform of already-approved pixels).

### Re-validation after the fix

```text
$ venv/bin/python3 scripts/build_full_atlas.py
...
{
  "ok": true, "width": 1536, "height": 1872,
  "errors": [], "warnings": [],
  "filled_states": ["idle","running-right","running-left","waving",
    "jumping","failed","waiting","running","review"]
}
```

`validate_atlas()` still passes clean — the fix only touches pixel content
within already-valid cells, not atlas geometry.

### Hash evidence: before vs. after

| state | count | unique hashes BEFORE | unique hashes AFTER |
|---|---|---|---|
| idle | 6 | 1 | 3 |
| running-right | 8 | 1 | 5 |
| running-left | 8 | 1 | 5 |
| waving | 4 | 1 | 3 |
| jumping | 5 | 1 | 5 |
| failed | 8 | 1 | 5 |
| waiting | 6 | 1 | 3 |
| running | 6 | 1 | 3 |
| review | 6 | 1 | 3 |

Every row now has more than one distinct cell hash (raw per-cell hashes in
`assets/keyframes/atlas_full_cell_hashes.json`). Rows with an even frame
count show a symmetric pattern (e.g. 6 frames → 3 unique hashes, in an
up/up/neutral/down/down shape) because `sin(2πi/n)` naturally repeats
magnitudes at symmetric phase points — this is the expected shape of a
sine-sampled bob/breathe cycle at low frame counts, not a partial fix; no row
regressed to 1.

Reinstalled into the isolated profile and re-hashed the actual on-disk
`spritesheet.webp` (not just the in-memory atlas) to confirm the fix survives
the real install path:

```text
$ HERMES_HOME=/home/chegusan/.hermes-jorgito-test venv/bin/python3 scripts/install_full_atlas_pet.py
validate_atlas(): ok=True, filled_states=[idle, running-right, running-left,
  waving, jumping, failed, waiting, running, review]
registered pet 'jorgito' -> /home/chegusan/.hermes-jorgito-test/pets/jorgito/spritesheet.webp
  exists=True generated=True
$ HERMES_HOME=/home/chegusan/.hermes-jorgito-test hermes pets select jorgito
✓ active pet set to Jorgito
$ HERMES_HOME=/home/chegusan/.hermes-jorgito-test hermes pets doctor
  ✓ ready  (active: jorgito)
```

The hash table above was computed against this reinstalled
`spritesheet.webp`, not the pre-install `atlas_full.png`.

### Visual evidence: consecutive frames side by side

`assets/keyframes/terminal_render_phase4/frame_strip_{idle,running-right,
jumping}.png` — each state's real per-column cells (as they land in the
atlas) laid out left→right at 2x, NEAREST-scaled, with column labels. Visual
inspection of `frame_strip_running-right.png` (the clearest case, 8 columns):
the dragon visibly bobs up/down by a couple of pixels and tilts slightly
across columns while identity, colors, and pixel-art edge sharpness are
unchanged from column 0 — no blur, no chroma residue, no silhouette
distortion.

### Real `~/.hermes` isolation re-check (same hard restriction as §7)

| check | before this fix | after this fix |
|---|---|---|
| `~/.hermes/config.yaml` md5 | `66684dd3b378e4584ab08ab097024ed4` | `66684dd3b378e4584ab08ab097024ed4` (unchanged) |
| `~/.hermes/config.yaml` mtime | `2026-08-15 10:38:33` | `2026-08-15 10:38:33` (unchanged) |
| `~/.hermes/pets/` contents | empty | empty (unchanged) |

All install/select/doctor calls during this correction used
`HERMES_HOME=/home/chegusan/.hermes-jorgito-test` exclusively; nothing in
`full_atlas.py`/`build_full_atlas.py`/`install_full_atlas_pet.py` touches
`HERMES_HOME` or pet-store state outside that explicit env var.

### Files changed (this correction)

- Modified: `scripts/full_atlas.py` — added `_vary()`, updated
  `build_frames_by_state()` to call it per column instead of list-repeating
  one cell; updated the module docstring (it previously described the exact
  behavior that caused this bug).
- Modified: `assets/keyframes/atlas_full.png` — rebuilt with varied cells.
- Added: `assets/keyframes/atlas_full_cell_hashes.json` — per-state,
  per-column SHA-256 hashes of the reinstalled `spritesheet.webp` (the
  before/after evidence above).
- Added: `assets/keyframes/terminal_render_phase4/frame_strip_{idle,
  running-right,jumping}.png` — consecutive-frame visual evidence.
- Not modified: `assets/keyframes/atlas_full_validation.json`,
  `assets/keyframes/contact_sheet_phase4_full.png`,
  `assets/keyframes/terminal_render_phase4/contact_sheet_terminal_phase4.png`
  — all three are keyed off column 0 only (the validator's per-row
  occupancy check, and both contact sheets' single reference pose per
  state), which `_vary()` leaves byte-identical to the pre-fix keyframe, so
  they did not change.
- Not touched: `/home/chegusan/.hermes/` (real profile) — verified
  unchanged before and after (table above).

## Decision

continue

## Next phase/task

1. **Pendiente: aprobación visual del usuario** sobre
   `assets/keyframes/contact_sheet_phase4_full.png` (mismo proceso que F1-A
   y el gate de Fase 3).
2. Una vez aprobado, Fase 5 (fuera del alcance de esta tarea, se despacha
   por separado): instalar el pet `jorgito` completo en el perfil real
   `/home/chegusan/.hermes/`, seleccionarlo, y correr escenarios reales de
   Hermes (evento → estado esperado → estado observado) por
   `docs/06_TEST_PLAN.md`'s Phase 5 criteria.
3. La decisión abierta y no bloqueante de Fase 1 sobre la degradación de
   legibilidad en el fallback unicode al scale default sigue en pie,
   confirmada aquí como aplicable a los 9 estados por igual (§6) — sigue
   siendo una decisión de producto pendiente del usuario, no específica de
   esta fase.
