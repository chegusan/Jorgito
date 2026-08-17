# Phase Result

## Phase

Phase 1 — Minimal visual proof (`idle`, `review`, `running`)

## Status

**PASS.**

- F1-A (identity match to canonical, user's own eyes): **APPROVED.** The
  user reviewed `assets/keyframes/contact_sheet_phase1.png` and said
  verbatim: "Están perfectos."
- F1-B / P1.2 / P1.3 (thinking/working readability at real terminal scale,
  `docs/06_TEST_PLAN.md`): **evidence collected this session, PASS with one
  documented caveat** — see §5–§8 below. Readability is clearly PASS on the
  richer render tiers (kitty/iTerm2/sixel — real pixels, no downscaling
  artifact) and DEGRADED on the truecolor-unicode half-block fallback tier
  at the project's real default scale. This is flagged as a non-blocking
  open decision for the user in "Bloqueantes" below, not a phase blocker:
  it's an inherent, pre-existing Hermes rendering-floor characteristic
  (documented in Hermes's own `agent/pet/constants.py`), not a defect in
  this phase's artwork.

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

This was my own read, not the required approval. **F1-A is now closed**:
the user opened `assets/keyframes/contact_sheet_phase1.png` (attached to
PR #1) and approved it verbatim ("Están perfectos"). The rest of this
document adds F1-B (terminal readability at real CLI scale), exercised in
this follow-up session.

### 5. F1-B setup: packaging idle/run/review into a real Hermes pet

New script: `scripts/build_phase1_test_pet.py`. Reuses Hermes's own
pet-store format instead of reinventing it:

- Reads the 3 already-processed 192×208 cells.
- Tiles each into a spritesheet using `agent.pet.constants.LEGACY_STATE_ROWS`
  (an 8-row taxonomy — narrower than the 9-row Codex grid — chosen so the
  renderer's `rows < 9` branch picks it, landing `idle`/`run`/`review` at
  rows 0/2/4 respectively). Each state's single frame is repeated across all
  `FRAMES_PER_STATE` (6) columns — this project has one static pose per
  state, not an animation, so a steady repeat plays back as "held still"
  rather than flickering into blank padding.
- Calls `agent.pet.store.register_local_pet()` — the same local-pet
  registration path Hermes's own `/pet generate` uses for freshly-hatched
  pets — to write `pets/jorgito-test/{pet.json,spritesheet.webp}`.

Installed **only** into the isolated profile
`HERMES_HOME=/home/chegusan/.hermes-jorgito-test` (pre-existing from an
earlier attempt in this phase, already had an unrelated `boba` test pet in
it). Run:

```text
$ HERMES_HOME=/home/chegusan/.hermes-jorgito-test \
  /home/chegusan/.hermes/hermes-agent/venv/bin/python3 scripts/build_phase1_test_pet.py
HERMES_HOME=/home/chegusan/.hermes-jorgito-test
registered pet 'jorgito-test' -> /home/chegusan/.hermes-jorgito-test/pets/jorgito-test/spritesheet.webp
  exists=True generated=True
$ HERMES_HOME=/home/chegusan/.hermes-jorgito-test hermes pets select jorgito-test
✓ active pet set to Jorgito (Phase 1 test) (display.pet.slug=jorgito-test, enabled)
```

**Real `~/.hermes` isolation check** (hard restriction from the task):

| check | before | after |
|---|---|---|
| `~/.hermes/config.yaml` mtime | `1786786713` | `1786786713` (unchanged) |
| `~/.hermes/pets/` contents | empty | empty |
| `~/.hermes/active_profile` | absent | absent |

Confirmed untouched.

### 6. F1-B rendering: the real Hermes CLI command, real TTY

This sandboxed shell has no TTY, and `hermes pets show`'s `resolve_mode()`
hard-codes `off` when `stdout.isatty()` is `False` — there is no flag to
force it. Used `script -qec "..." <logfile>` to fake a pty so the actual CLI
path runs unmodified:

```text
$ script -qec "HERMES_HOME=/home/chegusan/.hermes-jorgito-test hermes pets show jorgito-test --state idle --once --mode unicode" idle_script.txt
$ script -qec "HERMES_HOME=/home/chegusan/.hermes-jorgito-test hermes pets show jorgito-test --state review --once --mode unicode" review_script.txt
$ script -qec "HERMES_HOME=/home/chegusan/.hermes-jorgito-test hermes pets show jorgito-test --state run --once --mode unicode" run_script.txt
```

All 3 ran successfully end-to-end (`Jorgito (Phase 1 test) — mode=unicode`
header, 25–27KB of valid truecolor-ANSI half-block escape output each, no
errors). Byte-compared a leading slice of the encoded block/color escape
codes against a same-scale direct call into
`agent.pet.render.PetRenderer.frame()` (§7) — identical, confirming the CLI
and the direct-API check use the exact same encoder; the only difference is
the CLI's additional right-margin indent (it right-aligns the sprite to the
terminal's actual width, which is a display concern of the wrapping shell,
not the encoder).

### 7. F1-B readability: real default terminal scale, unicode fallback

Because a byte dump of ANSI escapes isn't visually inspectable, added
`scripts/render_phase1_test_pet.py`, which calls
`agent.pet.render.PetRenderer` directly (same encoder as §6) at the
project's actual default `display.pet.scale` (`0.33`, from
`agent/pet/constants.py`), which resolves to `cols_for_scale(0.33) = 16`
columns — the real width `hermes pets show` would use un-configured. For
each state this dumps the raw ANSI (`*.ans.txt`) and rasterizes the same
half-block pixel grid into a magnified PNG so it's inspectable without a
truecolor terminal (`*_realsize_preview.png`, 20px per real half-block
cell — a 1:1 pixel-for-color reproduction of the grid, just scaled up for
visibility, not an enhancement of the underlying detail).

Combined into `assets/keyframes/terminal_render_phase1/contact_sheet_realsize.png`
(16 cols × 9 char-rows per state, the real Hermes default in this render
tier):

At this resolution **idle / run / review are not reliably distinguishable
from each other** — all three read as a similar red/orange/yellow blob; the
identity (color palette) survives, but the pose-differentiating props
(shovel+dirt for `run`, book+glasses for `review`, per the project's own
confirmed convention in `docs/08_PROJECT_STATE.md`) are lost to the
16×9 downscale. This literally fails the P1.2/P1.3 "user can identify... without
zooming" criterion **for this specific render tier**.

Cross-checked whether this is a scale problem or a downscale-algorithm
problem by re-rendering the *processed cells directly* (not through the
pet-store round-trip) at 24 and 40 columns
(`assets/keyframes/terminal_render_phase1/compare_cols{24,40}.png`): by 24
columns the shovel becomes visible in `run` and by 40 columns both the
shovel/dirt (`run`) and book/glasses (`review`) read clearly. So the props
themselves survive fine at moderate half-block resolution — it's
specifically the 16-column *default-scale floor* that erases them, not a
processing defect from §1–§3.

### 8. F1-B readability: real default scale, native-pixel render tiers

`render.py`'s own protocol preference order is kitty → iTerm2 → sixel →
unicode (`detect_terminal_graphics()`) — unicode half-blocks are the
*universal fallback*, not the primary path. kitty/iTerm2/sixel draw true
scaled pixels with no half-block downsampling floor (this is called out
directly in Hermes's own source comment on `UNICODE_MIN_COLS`: "kitty/GUI
draw true pixels and have no such floor... crisp there but mush in
half-blocks"). At the same real default scale (`0.33`), a 192×208 cell
becomes a 63×68px image — rendered
in `assets/keyframes/terminal_render_phase1/compare_kitty_scale033.png`
(nearest-neighbor-magnified 6x purely so it's visible in this document; the
underlying 63×68px content is a Lanczos downscale of the processed cell,
matching what `render.py`'s kitty/iTerm2/sixel encoders would draw at that
scale — but **not** an actual screenshot from a kitty/iTerm2/sixel
terminal: consistent with `docs/08_PROJECT_STATE.md`'s standing open
question from Phase 0, no graphics-protocol-capable terminal was available
in this environment either. This is a computed proxy, presented as such,
not a captured render):

- `idle`: calm neutral standing pose, eyes open forward.
- `run`: visible shovel + dirt/earth particles at ground level — reads
  clearly as digging/working, matching the project's confirmed convention.
- `review`: visible glasses + a held book near the face — reads clearly as
  reading/thinking, matching the project's confirmed convention.

All 3 are clearly distinguishable **without zooming** in this computed
proxy, which — since it's the same pixel content the encoder would draw,
just not captured from a live terminal (see caveat above) — reads as a
clean P1.2/P1.3 PASS for this render tier, pending an actual live
kitty/iTerm2/sixel session to fully confirm. This is also the render tier
this session's own terminal (tmux-256color) would *not* get (§7's unicode
fallback is what this environment actually resolves to), which is exactly
why both tiers needed checking rather than assuming one.

### 9. Self-assessment summary (F1-B)

Readability at real default scale is tier-dependent:

| render tier | 3 states distinguishable without zooming? |
|---|---|
| kitty / iTerm2 / sixel (real pixels) | **Yes** — clean pass |
| unicode half-block (universal fallback, e.g. tmux/VS Code/plain SSH) | **No** — collapses to a same-looking blob at the 16-col default floor |

This is not this agent's final call any more than F1-A was — flagging the
open question (is the unicode-fallback degradation acceptable as a known,
pre-existing Hermes-wide limitation, or does it need `display.pet.scale`
bumped for that tier before Phase 1 is considered fully closed?) in
"Bloqueantes" below for the user.

## Tests executed

- `venv/bin/python3 scripts/process_phase1_keyframes.py` — full run, see
  §2. Exit 0, all 3 outputs produced.
- Verified each `assets/keyframes/processed/{state}.png` is exactly
  192×208 RGBA (matches the project's standard cell size).
- Residual-magenta pixel count check per processed cell (§3).
- Visual inspection of the contact sheet by this agent (§4) — informal,
  superseded by the user's actual approval ("Están perfectos").
- `venv/bin/python3 scripts/build_phase1_test_pet.py` (HERMES_HOME=isolated
  profile) — pet registered, `exists=True generated=True` (§5).
- `hermes pets select jorgito-test` (isolated profile) — active pet set.
- Real `~/.hermes` isolation check, before and after (§5 table) — untouched.
- `script -qec "hermes pets show ... --once --mode unicode" <log>` x3
  (idle/review/run), faking a TTY since this shell has none — real CLI path
  exercised end-to-end, all 3 succeeded (§6).
- `venv/bin/python3 scripts/render_phase1_test_pet.py` — direct-API render
  at the real default scale (0.33 → 16 cols), same encoder as the CLI;
  produced ANSI dumps + magnified PNG previews for all 3 states (§7).
- Cross-check renders at 24/40 cols and at native kitty/iTerm2/sixel pixel
  scale (§7–§8) to isolate whether illegibility was a processing defect
  (it isn't) vs. a render-tier-specific downscale floor (it is).

## Cost

- image generations: 0 across both sessions (this session did not call any
  image-generation model or API either — F1-B is packaging/rendering only,
  reusing the 3 already-processed cells)
- retries: 0
- approximate model/tool usage: 4 local Python script runs (build pet,
  render pet, 2 comparison renders — all Pillow + Hermes source imports
  only, no network, no LLM/model calls at runtime) + 4 `hermes`/CLI
  invocations (select, 3x `pets show` under a faked TTY)
- development time: ~2 sessions total (deterministic-processing pass +
  this F1-B packaging/render/evidence pass)

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
- Added: `scripts/build_phase1_test_pet.py` — packages the 3 processed
  cells into a real Hermes pet via `agent.pet.store.register_local_pet()`.
- Added: `scripts/render_phase1_test_pet.py` — renders the test pet at the
  real default terminal scale via `agent.pet.render.PetRenderer` directly
  and dumps ANSI + magnified-PNG evidence.
- Added: `assets/keyframes/terminal_render_phase1/` — F1-B evidence:
  `{idle,review,run}.ans.txt`, `{idle,review,run}_realsize_preview.png`,
  `contact_sheet_realsize.png`, `compare_cols{24,40}.png`,
  `compare_kitty_scale033.png`.
- Not touched: `/home/chegusan/.hermes/` — verified untouched before and
  after this session too (§5 table); all pet install/render/select calls
  in this session used `HERMES_HOME=/home/chegusan/.hermes-jorgito-test`
  exclusively.

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
- F1-B unicode-fallback degradation (§7–§9): at the project's real default
  scale (0.33 → 16 cols), the unicode half-block render tier does not meet
  the P1.2/P1.3 "identify without zooming" criterion — idle/run/review
  collapse into a similar-looking blob. The same scale on kitty/iTerm2/
  sixel (real pixels, `render.py`'s preferred tiers) passes cleanly. This
  is a pre-existing Hermes rendering-floor characteristic (documented in
  Hermes's own `UNICODE_MIN_COLS` comment), not an artifact defect from
  §1–§3 — confirmed by the 24/40-col cross-check in §7, where the same
  props read fine at a slightly larger half-block width. Flagging as an
  open decision below rather than deciding unilaterally which tier's
  behavior "counts" for closing Phase 1.

## Bloqueantes

**Ninguno bloquea el cierre técnico de esta tarea** — toda la evidencia de
F1-B pedida (empaquetado real, instalación en perfil aislado, render con el
comando real de Hermes, evaluación de legibilidad) está recolectada y
documentada arriba (§5–§9), y el perfil `~/.hermes` real quedó verificado
intacto antes y después.

Queda **una decisión puntual del usuario, no bloqueante para este commit**:

> ¿La degradación de legibilidad en el fallback unicode de half-blocks al
> `display.pet.scale` default (0.33 → 16 cols) — donde `run`/`review` no se
> distinguen entre sí sin ampliar, aunque sí se distinguen claramente en
> kitty/iTerm2/sixel a la misma escala (§8) — se acepta como limitación
> conocida y preexistente de Hermes (afecta a cualquier pet en ese formato,
> no es específico de Jorgito), o amerita subir el `scale` default del pet
> (o el `unicode_cols` mínimo) antes de considerar la Fase 1 totalmente
> cerrada para usuarios en terminales sin protocolo gráfico (tmux sin
> passthrough, VS Code integrado, SSH plano)?

No se tomó una decisión unilateral acá porque cambiar `display.pet.scale`
es una decisión de producto (afecta el tamaño default de *todos* los pets,
no solo Jorgito) fuera del alcance de "empaquetar y medir legibilidad".

## Decision

continue

## Next phase/task

1. **F1-A: cerrado.** Usuario aprobó `contact_sheet_phase1.png` ("Están
   perfectos").
2. **F1-B: evidencia recolectada, PASS con el caveat documentado arriba.**
   Si el usuario decide que la degradación en el fallback unicode amerita
   acción, la fase 2/3 (o un ajuste puntual de `display.pet.scale`) puede
   abordarlo; si la acepta como limitación conocida de Hermes, Phase 1
   queda cerrada sin trabajo adicional.
3. Antes de la Fase 3 (atlas completo de 8 filas), resolver al menos uno de
   los bloqueantes de proveedor de imagen (OpenAI billing / credencial de
   OpenRouter) si esa fase vuelve a depender del pipeline nativo de
   generación en lugar de más keyframes manuales.
