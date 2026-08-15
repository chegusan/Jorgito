# Phase Result

## Phase

Phase 0 — Environment and compatibility audit

## Status

PASS

## Evidence

### 1. Hermes version / help / pet-related subcommands

```text
$ hermes --version
Hermes Agent v0.19.0 (2026.7.20) · upstream a88512b1
Install directory: /home/chegusan/.hermes/hermes-agent
Install method: git
Python: 3.11.15
OpenAI SDK: 2.24.0
Update available: 1 commit behind — run 'hermes update'
```

`hermes --help` exposes a top-level `pets` subcommand (among ~50 others). Full
`pets` command tree:

```text
hermes pets {list,install,select,show,off,scale,remove,doctor}
```

- `hermes pets doctor` — checks pet setup + terminal graphics support.
- `hermes pets list [query] [--installed] [--limit N]` — browse the petdex gallery.
- `hermes pets install <slug> [--force] [--select]`.
- `hermes pets show [slug] [--state STATE] [--cycle] [--once] [--mode MODE] [--scale S]`
  — `--state` accepts `idle/run/review/failed/wave/jump` per its help text
  (note: `waiting` is not listed in the help string, see Problems).
- `hermes pets select [slug]`, `hermes pets off`, `hermes pets scale`, `hermes pets remove`.
- In addition, interactive chat/TUI exposes an `/hatch <description>` slash
  command (`hermes_cli/cli_commands_mixin.py:_handle_hatch_command`) that runs
  a full in-process pet-generation pipeline — see item 4.

There is no separate `hermes pets doctor` vs. general `hermes doctor` collision
— both exist independently (`hermes doctor` = general config/deps check,
`hermes pets doctor` = pet-specific).

### 2. Isolated test profile

Mechanism used: **`HERMES_HOME` environment variable**, not `hermes profile create`.

Reason: `hermes profile create <name>` (confirmed by reading
`hermes_cli/profiles.py`) creates the new profile at
`~/.hermes/profiles/<name>/` — literally inside the protected
`/home/chegusan/.hermes/` tree. To honor the hard restriction of not writing
anything under that path, the audit instead set:

```bash
export HERMES_HOME=/home/chegusan/.hermes-jorgito-test
```

Verified in source (`hermes_constants.py:get_hermes_home()`): resolution order
is context-override → `HERMES_HOME` env var → platform default
(`~/.hermes`). With `HERMES_HOME` set, every Hermes pet command (doctor,
install, select, show) operated exclusively under
`/home/chegusan/.hermes-jorgito-test/`.

Isolation confirmed after all testing:

```text
$ ls -la /home/chegusan/.hermes/pets      → empty (0 entries), mtime unchanged
$ stat /home/chegusan/.hermes/config.yaml → mtime unchanged from before audit start
$ /home/chegusan/.hermes/active_profile   → does not exist (was never created)
```

No file under `/home/chegusan/.hermes/` was created, modified, or deleted
during this audit.

### 3. Known stock pet install + state cycling (in isolated profile)

```text
$ hermes pets install boba --select
✓ installed Boba → /home/chegusan/.hermes-jorgito-test/pets/boba
✓ Boba is now the active pet (display.pet.slug=boba, enabled)
```

`pet.json` (real, on-disk schema — much smaller than docs/03 implies):

```json
{
  "id": "boba",
  "displayName": "Boba",
  "description": "A tiny otter sipping bubble tea while keeping you company in Codex.",
  "spriteVersionNumber": 2,
  "spritesheetPath": "spritesheet.webp"
}
```

Spritesheet: `spritesheet.webp`, lossless WebP with alpha, **1536×2288 px**
(8 columns × 11 rows of 192×208 cells) — see Problems for the discrepancy vs.
docs/03's "8×9, 1536×1872" spec.

Rendering test (all 7 states Hermes recognizes, via a real pty since the
sandboxed shell has no TTY by default — `script -qc "... --once --mode
unicode" /dev/null`):

```text
idle    → rendered (true-color unicode half-block frames, 56 lines)
run     → rendered (56 lines)
review  → rendered (56 lines)
waiting → rendered (56 lines)
failed  → rendered (56 lines)
jump    → rendered (47 lines)
wave    → rendered (38 lines)
```

Sample raw output header line: `Boba — mode=unicode  (Ctrl+C to stop)`,
followed by true-color (`\x1b[38;2;r;g;b`) half-block glyphs — confirms actual
pixel data is being read from the spritesheet and drawn, not a placeholder.

`hermes pets doctor` after install:

```text
petdex doctor
  pets dir:        /home/chegusan/.hermes-jorgito-test/pets
  installed:       1 (boba)
  display.pet.enabled:     True
  display.pet.slug:        boba
  active (resolved):       boba
  display.pet.render_mode: auto
  detected graphics:       unicode
  effective mode (TTY):    off
  ✓ ready
```

`detected graphics: unicode` — this environment (tmux, `TERM=tmux-256color`,
no Kitty/iTerm/Sixel) has no true graphics protocol, so Hermes falls back to
its true-color unicode half-block renderer. This is Hermes's documented
fallback path (`agent/pet/constants.py`), not a failure — it produced visible,
readable frames.

Row taxonomy (from `agent/pet/constants.py`, matches docs/03 exactly):

```text
CODEX_STATE_ROWS = [idle, running-right, running-left, waving, jumping,
                     failed, waiting, running, review]
```

Hermes activity-state names (`PetState` enum) map onto these row names via
`STATE_ALIASES`, e.g. `wave→waving`, `jump→jumping`, `run→running`.

### 4. Camino A — Codex `hatch-pet`

- `codex --version` → `codex-cli 0.145.0`; `codex login status` →
  `Logged in using ChatGPT` (already authenticated).
- `codex --help` top-level commands: no `hatch-pet` and no generic `skill`
  subcommand.
- Codex ships a **skills** mechanism at `~/.codex/skills/.system/` (system
  skills: `imagegen`, `openai-docs`, `plugin-creator`, `review-agent`,
  `skill-creator`, `skill-installer`) — **no `hatch-pet` skill present**.
- `codex plugin list` (openai-curated marketplace, 184 plugins) — searched for
  `pet|hatch|mascot|sprite`: **zero matches**. `hatch-pet` is not installable
  from the currently configured marketplace on this machine.
- Filesystem-wide `find / -iname "*hatch-pet*"` → no results.

**Important discovery:** Hermes itself already ships an in-process
reimplementation of the hatch-pet pipeline, not merely a plan to use Codex's:

- `agent/pet/generate/{orchestrate,atlas,prompts,imagegen}.py`. The
  `atlas.py` module docstring states explicitly: *"The frame-segmentation,
  fit-to-cell, and transparency-residue logic is adapted from OpenAI's
  `hatch-pet` skill (openai/skills, Apache-2.0)."*
- Exposed today via the interactive **`/hatch <description>`** slash command
  (`hermes_cli/cli_commands_mixin.py:_handle_hatch_command`), which runs:
  base draft(s) → per-state grounded row generation → atlas slice/compose →
  `validate_atlas()` → install as active pet, all in one process, no
  external Codex call required.
- The underlying Python API (`orchestrate.generate_base_drafts(concept, *,
  reference_images: list[Path] | None, ...)` and `orchestrate.hatch_pet(...)`)
  **does support reference-image grounding** — but the current `/hatch`
  slash-command wrapper does not pass a reference image through (it only
  forwards the free-text concept). Using `assets/reference/jorgito_canonical.png`
  as grounding will require either a small extension of `_handle_hatch_command`
  to accept a `--reference <path>` argument, or a short standalone script that
  imports `agent.pet.generate.orchestrate` directly and calls
  `generate_base_drafts(concept, reference_images=[canonical_path])`. Either
  is a small, in-repo change — no upstream/fork needed.
- Image generation is provider-abstracted (`agent/pet/generate/imagegen.py`,
  `_REF_CAPABLE = ("nous", "openai", "openai-codex", "openrouter", "krea")`);
  `"openai-codex"` is one of the reference-capable providers, meaning
  generation can potentially reuse the already-authenticated Codex/ChatGPT
  login instead of requiring a fresh `OPENAI_API_KEY`. Exact provider
  resolution (`resolve_provider()`) was read but not exercised — no image
  generation was run in Phase 0 per the plan's "no generar assets antes de
  PASS" rule.

Conclusion for Camino A: the literal external tool (`codex hatch-pet`) does
**not** exist on this machine and is not present in the configured plugin
marketplace. However, an equivalent, already-integrated capability exists
natively inside the installed Hermes Agent build, ranks higher on
AGENTS.md's complexity ladder ("existing Hermes configuration/behavior")
than reaching for external Codex tooling, and needs only a minimal
reference-image plumbing change to be usable for Jorgito. This should replace
the plan's assumption of "Codex CLI + hatch-pet skill" for Phase 1.

### 5. OpenAI pet-atlas validator

- No standalone `hatch-pet` CLI/binary/validator exists on this system (see
  item 4) — nothing to run `--help` against.
- The actual atlas-validation logic docs/03 refers to is embedded as Python
  inside Hermes: `agent/pet/generate/atlas.py:validate_atlas(atlas) -> dict`
  (`{ok, width, height, errors, warnings, filled_states}`), checking exact
  geometry (`ATLAS_WIDTH × ATLAS_HEIGHT` = 1536×1872 for the 9-row spec used
  by the *generator*), per-cell occupancy, and transparency invariants. This
  is callable via Python import; there is no CLI entry point for it today.
- The public `petdex` CLI is available and runnable via `npx petdex` (no
  install needed beyond npm's cache; confirmed `petdex 1.2.2`). Its command
  set: `list, install, login, logout, whoami, submit <path> [--force], edit,
  telemetry, version`. There is **no local/offline validate-only command** —
  `submit <path>` is the closest thing, but it requires `petdex login`
  (Clerk OAuth, not currently signed in) and is a **publish action** (uploads
  to the public gallery), not a dry-run validator. It was not run beyond
  `--help`, since running it would require creating a public-facing account
  action out of scope for an audit task.
- Recommendation for Phase 4: validate locally with Hermes's own
  `agent.pet.generate.atlas.validate_atlas()` (already installed, already
  adapted from the OpenAI spec, no network/auth required) rather than
  `petdex submit`, per AGENTS.md "use existing upstream validators" +
  "smallest solution that works."

### 6. Canonical reference image

`assets/reference/jorgito_canonical.png`: **1254×1254 px, RGB (no alpha —
opaque cream/beige background), PNG.** Visually confirmed (rendered and
inspected directly): pixel-art baby dragon, thumbs-up pose, facing left;
large green eyes with visible white sclera; two small tan horns; crimson/
burgundy body with darker burgundy back-plates/spikes; yellow-gold belly and
throat with horizontal banding; folded wings with red struts and yellow-gold
membranes; visible curled tail wrapping toward the viewer; two arms, two
hind legs; friendly, non-aggressive expression; small yellow sparkle
decorations in the background. This matches every identity invariant listed
in docs/04_ASSET_SPEC.md.

`assets/reference/Code_Generated_Image.png`: **128×128 px, RGBA (transparent
background), PNG.** Same color palette/species (crimson/burgundy + yellow,
green eyes), but a different pose — rearing on hind legs with wings spread
and mouth open, "roaring/flying" — consistent with the plan's description of
it as a secondary, non-canonical reference (useful only for wing/tail
articulation, not as the identity source of truth).

Neither image is pre-sliced into a pet-package layout; both are single
reference illustrations, as expected at this stage.

## Tests executed

- `hermes --version`, `hermes --help`, `hermes pets --help` and all pet
  subcommand `--help`s, `hermes profile --help/list/create --help`.
- Source inspection (read-only) of `hermes_constants.py`, `hermes_cli/
  profiles.py`, `agent/pet/constants.py`, `agent/pet/generate/{atlas,
  orchestrate,imagegen}.py`, `hermes_cli/cli_commands_mixin.py`.
- `HERMES_HOME=/home/chegusan/.hermes-jorgito-test hermes pets doctor`
  (before and after install).
- `HERMES_HOME=... hermes pets list` (gallery browse, 4523 pets).
- `HERMES_HOME=... hermes pets install boba --select`.
- `HERMES_HOME=... hermes pets show --state {idle,run,review,waiting,failed,
  jump,wave} --once --mode unicode`, each via `script -qc "..." /dev/null`
  to allocate a real pty (the plain sandboxed shell reports "no TTY").
- Inspected the real, installed `boba/pet.json` and measured
  `boba/spritesheet.webp` with Pillow (1536×2288 px, RGBA).
- `codex --version`, `codex login status`, `codex --help`, `codex plugin
  list` (184 entries, grepped for pet/hatch/mascot/sprite — none),
  `codex plugin marketplace list`, filesystem-wide search for `*hatch-pet*`.
- `npx petdex --help`, `npx petdex submit --help`, `npx petdex version`
  (installed petdex@1.2.2 via npx cache; no login performed, no submit run).
- Verified real `/home/chegusan/.hermes/` was untouched: `pets/` dir still
  empty, `config.yaml` mtime unchanged, no `active_profile` file created.
- Loaded and visually inspected both reference PNGs directly.

## Cost

- image generations: 0
- retries: 0
- approximate model/tool usage: this audit only (no image-gen model calls;
  read-only source inspection + local CLI commands)
- development time: ~1 session (Phase 0 audit only)

## Files changed

- Added: `docs/phase_results/PHASE_0_RESULT.md` (this file)
- Updated: `docs/08_PROJECT_STATE.md` (phase status, confirmed decisions,
  open questions)
- Created outside the project repo (not a project file, kept for reuse in
  Phase 1): `/home/chegusan/.hermes-jorgito-test/` — isolated HERMES_HOME
  test profile with `boba` installed and selected. `/home/chegusan/.hermes/`
  was not modified.

## Problems

- `hermes pets show --help` lists valid `--state` values as
  `idle/run/review/failed/wave/jump` — `waiting` is missing from that help
  string even though it is a real, working state (`PetState.WAITING`,
  confirmed rendering above). Cosmetic help-text gap in the installed Hermes
  build, not a functional blocker.
- The real installed-pet atlas shape (`boba`: 8 cols × 11 rows, 1536×2288)
  does not match docs/03_INTERFACES_AND_CONTRACTS.md's stated "8 columns; 9
  state rows; 1536×1872" exactly. Root cause understood: Hermes's renderer
  computes `rows = sheet.height // FRAME_H` dynamically and treats any
  `row_count >= 9` as the 9-name `CODEX_STATE_ROWS` taxonomy (ignoring extra
  trailing rows) — so 9 rows is a **floor**, not an exact requirement, for
  pets built outside Hermes's own generator. Hermes's *own* atlas builder
  (`agent/pet/generate/atlas.py`) still targets exactly 1536×1872 (9 rows) by
  construction. Recommend updating docs/03 to note "minimum 9 rows; Hermes's
  own generator always emits exactly 9" rather than implying every
  real-world pet is exactly 9 rows.
- No offline/local "OpenAI pet atlas validator" CLI exists on this machine;
  only Hermes's internal Python function and the public `petdex submit`
  (login + publish, not a dry-run). See item 5 for the recommended
  substitute.
- Camino A as literally specified in the plan ("Codex CLI + hatch-pet
  skill") is not installable from the current marketplace config. A
  materially equivalent, already-integrated path exists inside Hermes
  itself (`/hatch` + `agent.pet.generate.orchestrate`) and should be the
  Phase 1 starting point instead — see item 4. This is not a blocker, but it
  changes *how* Phase 1 should be executed vs. the plan's literal wording.
- This test session's terminal (tmux, no Kitty/Sixel) only exercises the
  unicode half-block fallback renderer. Kitty/iTerm2/Sixel graphics-protocol
  rendering was not exercised because no such terminal was available in this
  environment. Not a blocker for Phase 0 (the fallback path is a supported,
  documented mode and rendered correctly), but Phase 5 real-world testing
  should also be checked in a graphics-protocol-capable terminal if one is
  available, for a higher-fidelity comparison.

## Bloqueantes

Ninguno. No blocking issues prevent proceeding to Phase 1.

## Decision

continue

## Next phase/task

Phase 1 — Minimal visual proof (`idle`, `review`, `running`), using
`assets/reference/jorgito_canonical.png` as grounding. Recommended concrete
approach based on this audit: extend or directly call Hermes's own
`agent.pet.generate.orchestrate.generate_base_drafts()` /
`hatch_pet()` with `reference_images=[canonical_path]` rather than pursuing
an external Codex `hatch-pet` skill (which does not exist on this machine).
Continue using the isolated `HERMES_HOME=/home/chegusan/.hermes-jorgito-test`
profile for all test installs/renders; do not touch
`/home/chegusan/.hermes/` until the real integration phase (Phase 5) is
explicitly reached and approved.
