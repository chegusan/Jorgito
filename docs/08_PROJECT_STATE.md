# 08 — Current Project State

Keep this file short. Replace stale status rather than accumulating a diary.

## Current phase

Phase 1 — Minimal visual proof (BLOCKED — see
`docs/phase_results/PHASE_1_RESULT.md`)

## Last gate

Status: Phase 1 — BLOCKED (see `docs/phase_results/PHASE_1_RESULT.md`).
Phase 0 — PASS (see `docs/phase_results/PHASE_0_RESULT.md`).

## Active objective

Generate and validate `idle`, `review`, `running` for Jorgito using the
canonical reference image, per Phase 1 of `Jorgito  Plan.md`. Blocked: both
reference-capable image providers configured in this environment
(`openai`, `openrouter`) fail before producing any image (OpenAI billing
hard limit; OpenRouter 401 missing-auth). Zero of the 3-generation budget
has been spent. Needs a user decision (fix billing, fix the OpenRouter
credential, or configure a third provider) before retrying.

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
- Still open: which provider the user wants to fix/configure to unblock
  Phase 1 (OpenAI billing, OpenRouter credential, or a third provider).

## Next action

Blocked on a user decision — see `docs/phase_results/PHASE_1_RESULT.md`
"Next phase/task". Once a working reference-capable image provider is
confirmed, rerun:

```bash
HERMES_HOME=/home/chegusan/.hermes-jorgito-test \
  [HERMES_PET_IMAGE_PROVIDER=<name>] \
  /home/chegusan/.hermes/hermes-agent/venv/bin/python3 scripts/generate_phase1.py
```

then build `build/phase1_contact_sheet.png` and run
`hermes pets show jorgito-test --state {idle,review,run}` for the F1-B
terminal-readability check.
