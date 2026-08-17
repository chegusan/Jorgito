# 08 — Current Project State

Keep this file short. Replace stale status rather than accumulating a diary.

## Current phase

Phase 1 — Minimal visual proof (deterministic processing PASS — awaiting
user's visual identity/readability gate; see
`docs/phase_results/PHASE_1_RESULT.md`)

## Last gate

Status: Phase 1 — PASS on deterministic processing (see
`docs/phase_results/PHASE_1_RESULT.md`); F1-A/F1-B visual approval is the
user's call, still pending. Phase 0 — PASS (see
`docs/phase_results/PHASE_0_RESULT.md`).

## Active objective

Generate and validate `idle`, `review`, `running` for Jorgito using the
canonical reference image, per Phase 1 of `Jorgito  Plan.md`. The earlier
native image-generation attempt was blocked (both `openai` and `openrouter`
failed before returning any image — see prior note below, still relevant
for future phases). That blocker was bypassed for Phase 1 itself: the user
generated the 3 raw keyframes manually (no API tokens spent) and committed
them to `assets/keyframes/raw/`. This agent then processed them
deterministically (chroma-key removal + fit-to-192x208-cell, reusing
`agent.pet.generate.atlas`'s existing functions) into
`assets/keyframes/processed/{idle,review,run}.png` and built
`assets/keyframes/contact_sheet_phase1.png` for visual review. Waiting on
the user to open the contact sheet (PR #1) and approve F1-A (identity)
before F1-B (terminal readability) is attempted.

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

Waiting on the user to visually review
`assets/keyframes/contact_sheet_phase1.png` (attached to PR #1) and approve
F1-A (identity match) / F1-B (thinking/working readability). If approved,
next step is installing the 3 processed cells into a test pet package and
rendering with `hermes pets show --mode unicode` under
`HERMES_HOME=/home/chegusan/.hermes-jorgito-test` to formally exercise
F1-B, then moving to Phase 2 (cost comparison) / Phase 3 (full atlas)
planning per `docs/06_TEST_PLAN.md`.
