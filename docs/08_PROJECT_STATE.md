# 08 — Current Project State

Keep this file short. Replace stale status rather than accumulating a diary.

## Current phase

Phase 3 — Deterministic processing of 5 additional manually-generated
keyframes (`waiting`, `failed`, `jump`, `wave`, `running-right`) —
**processing self-assessed PASS, visual gate pending user approval** on
`assets/keyframes/contact_sheet_phase3.png`; see
`docs/phase_results/PHASE_3_RESULT.md`. Phase 1 — **PASS** (below).

## Last gate

Status: Phase 3 processing — **self-assessed PASS, pending user visual
approval**. All 5 new keyframes chroma-keyed + fit to 192×208 cells at
0.00% residual magenta each (better than Phase 1's 0.01-0.10% range),
composited into `assets/keyframes/contact_sheet_phase3.png`. Reused Phase
1's method via a new shared module (`scripts/keyframe_processing.py`)
instead of duplicating it; Phase 1's own outputs verified byte-identical
after that refactor. One real fix was needed: Phase 3's raw backdrop had
drifted from pure magenta (a ComfyUI/JPEG-export shade shift, not just
compression noise), so keying uses `chroma_key=None` (atlas.py's built-in
per-image auto-detection) instead of Phase 1's fixed `(255, 0, 255)`. Full
detail in `docs/phase_results/PHASE_3_RESULT.md`. `running-left`
intentionally not included — deferred to a future full-atlas-assembly
phase (mirror of `running-right`, no new generation needed).

Status: Phase 1 — **PASS**. F1-A (identity): approved by the user verbatim
("Están perfectos") on `assets/keyframes/contact_sheet_phase1.png`. F1-B
(P1.2/P1.3 thinking/working readability at real terminal scale): tested by
packaging idle/run/review into a real Hermes pet
(`scripts/build_phase1_test_pet.py`) in the isolated profile
`HERMES_HOME=/home/chegusan/.hermes-jorgito-test` and rendering with the
real `hermes pets show` CLI + a direct-API check at the project's true
default scale. Result is render-tier-dependent: clean PASS on kitty/iTerm2/
sixel (real pixels — shovel+dirt reads as `run`, book+glasses reads as
`review`, matching the confirmed convention below); DEGRADED on the
universal unicode half-block fallback, where the 3 states collapse into a
similar-looking blob at the 16-col default width. Full evidence and the
one open (non-blocking) product decision for the user in
`docs/phase_results/PHASE_1_RESULT.md`. Phase 0 — PASS (see
`docs/phase_results/PHASE_0_RESULT.md`).

## Active objective

**Pending: user visual approval** of `assets/keyframes/contact_sheet_phase3.png`
— identity match to `jorgito_canonical.png` + per-action legibility for
waiting/failed/jump/wave/running-right (same gate process as Phase 1's
F1-A). Separately, Phase 1's still-open unicode-fallback readability
question (see Phase 1 entries above) stands independently and isn't
blocking. Once Phase 3's 5 keyframes are approved, the natural next step is
full-atlas assembly — mirroring `running-left` from `running-right` and
packaging all 8/9 states into a real Hermes pet — per
`docs/06_TEST_PLAN.md`.

## Confirmed decisions

- Primary target: Hermes CLI/TUI.
- OS: Arch Linux.
- Start with native/minimal Hermes-Petdex integration.
- Prepare for a future controlled adapter but do not implement it in MVP.
- Preserve Jorgito identity and action readability; perfection is not required.
- Thinking/review = book + glasses.
- Working/running = shovel + moving earth.
- Every phase has a validation gate.
- Complexity budget applies.
- Isolated Hermes testing uses `HERMES_HOME=/home/chegusan/.hermes-jorgito-test`
  (env var override, verified in source), never `hermes profile create`
  (which nests under `~/.hermes/profiles/`). The real `/home/chegusan/.hermes/`
  must stay untouched until Phase 5.
- Phase 1 asset generation should go through Hermes's own built-in pet
  pipeline (`agent.pet.generate.orchestrate`, reachable via `/hatch` or
  direct Python call with `reference_images=[...]`) rather than an external
  Codex `hatch-pet` skill, which is not installed/available on this machine.
- Reference-image grounding for a *subset* of states (not the full 9-row
  atlas) is done by calling `imagegen.generate()` / `atlas.*` /
  `store.register_local_pet()` directly — one call per requested state —
  rather than `orchestrate.hatch_pet()`, which always generates all 8
  non-mirrored rows in a single pass and would blow a 3-generation budget.
  See `scripts/generate_phase1.py`.

## Open questions

- Which `SpriteProvider` `resolve_provider()` picks by default in this
  environment: answered — `openai` (first available in `_REF_CAPABLE`
  order), with `openrouter` also registered/available as a fallback via
  Hermes's own `HERMES_PET_IMAGE_PROVIDER` override. Neither is currently
  *functional* (see Phase 1 blocker below) — this is a credentials/billing
  problem, not a code/architecture question.
- No graphics-protocol terminal (Kitty/iTerm/Sixel) was available during
  Phase 0; only the unicode half-block fallback was exercised. Revisit in
  Phase 5 if a graphics-capable terminal becomes available.
- Which provider the user wants to fix/configure to unblock native
  generation for *future* phases (e.g. Phase 3's full 8-row atlas): still
  open, not needed for Phase 1 since manual keyframes bypassed it.

## Next action

Waiting on the user's visual approval of
`assets/keyframes/contact_sheet_phase3.png` (Phase 3's gate — see "Active
objective" above). Independently, Phase 1's still-open unicode-fallback
question in `docs/phase_results/PHASE_1_RESULT.md`'s "Bloqueantes" is
unresolved but non-blocking. `running-left` remains explicitly deferred to
a future full-atlas-assembly phase per
`docs/phase_results/PHASE_3_RESULT.md`.
