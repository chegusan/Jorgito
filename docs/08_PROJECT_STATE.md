# 08 — Current Project State

Keep this file short. Replace stale status rather than accumulating a diary.

## Current phase

Phase 1 — Minimal visual proof (not started)

## Last gate

Status: Phase 0 — PASS (see `docs/phase_results/PHASE_0_RESULT.md`)

## Active objective

Generate and validate `idle`, `review`, `running` for Jorgito using the
canonical reference image, per Phase 1 of `Jorgito  Plan.md`.

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

## Open questions

- How to pass `assets/reference/jorgito_canonical.png` as a grounding
  reference into the pet-generation pipeline: extend `_handle_hatch_command`
  with a `--reference` flag, or call `orchestrate.generate_base_drafts()` /
  `hatch_pet()` directly from a small script. Decide during Phase 1 planning.
- Which `SpriteProvider` (`nous/openai/openai-codex/openrouter/krea`)
  `resolve_provider()` picks by default in this environment, and whether it
  can reuse the existing Codex/ChatGPT login instead of requiring a fresh
  `OPENAI_API_KEY`. Not yet exercised — first real image-gen call happens in
  Phase 1.
- No graphics-protocol terminal (Kitty/iTerm/Sixel) was available during
  Phase 0; only the unicode half-block fallback was exercised. Revisit in
  Phase 5 if a graphics-capable terminal becomes available.

## Next action

Begin Phase 1: generate `idle`/`review`/`running` grounded on
`assets/reference/jorgito_canonical.png` via Hermes's native pet pipeline,
in the isolated `HERMES_HOME` test profile, respecting the 1-generation +
1-repair budget per state from `docs/04_ASSET_SPEC.md`.
