# 08 — Current Project State

Keep this file short. Replace stale status rather than accumulating a diary.

## Current phase

Phase 1 — Minimal visual proof (**PASS**, F1-A approved by user + F1-B
evidence collected with one documented open decision; see
`docs/phase_results/PHASE_1_RESULT.md`)

## Last gate

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

Phase 1 is closed. Next: the user decides whether the unicode-fallback
readability degradation (see "Last gate" above) needs a
`display.pet.scale` adjustment before moving on, or is accepted as a
known, pre-existing Hermes-wide rendering-floor limitation (not specific to
Jorgito's artwork). Either way, Phase 2 (cost comparison) / Phase 3 (full
8-row atlas) planning per `docs/06_TEST_PLAN.md` can proceed.

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

Phase 1 is closed (PASS). Waiting on the user's call on the one open
question in `docs/phase_results/PHASE_1_RESULT.md`'s "Bloqueantes" (accept
the unicode-fallback readability degradation as a known Hermes limitation,
or bump `display.pet.scale`/`unicode_cols` for that tier). Then proceed to
Phase 2 (cost comparison) / Phase 3 (full atlas) planning per
`docs/06_TEST_PLAN.md`.
