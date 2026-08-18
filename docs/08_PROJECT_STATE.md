# 08 — Current Project State

Keep this file short. Replace stale status rather than accumulating a diary.

## Current phase

Phase 2 — Camino decision (DONE, see `docs/phase_results/PHASE_2_RESULT.md`).
Next up: Phase 3 (generate remaining 5 keyframes) + Phase 4 (full 8-state
atlas script), blocked on user externally generating the remaining
keyframes.

## Last gate

- Phase 0 — PASS (see `docs/phase_results/PHASE_0_RESULT.md`).
- Phase 1 — PASS (F1-A identity + F1-B terminal readability, both approved/
  verified with real evidence). Work lives on branch
  `phase-1-minimal-visual-proof`, **PR #1 open, not yet merged** —
  merging is the user's call, not the orchestrator's.
  See `docs/phase_results/PHASE_1_RESULT.md`.
- Phase 2 — PASS (Camino B chosen for the remaining states, with evidence).
  See `docs/phase_results/PHASE_2_RESULT.md`.
- Phase 2B — **FAIL/BLOCKED**. After the user reviewed Phase 3/4's
  deterministic `_vary()` animation (branch `phase-4-full-atlas`,
  `docs/phase_results/PHASE_4_RESULT.md`) and judged it doesn't read as real
  animation, Path A (`hatch_pet()`) was retried with real, user-funded
  OpenRouter budget. `hatch_pet()` raised `GenerationError`
  (`missing required animation row(s): running-right`) — only 4/8 generated
  rows (`idle`, `waving`, `jumping`, `waiting`) sliced cleanly;
  `running-right`/`failed`/`running`/`review` failed all 3 internal
  attempts. **$2.4019 spent, no atlas produced, no pet installed.**
  Real `~/.hermes` verified untouched before/after. See
  `docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md` for the full per-state
  breakdown and the 4 options put to the user.

## Active objective

Waiting on the user to pick one of Phase 2B's 4 options (retry same model,
try a different `OPENROUTER_IMAGE_MODEL`, abandon Path A and keep Phase 3/4's
Camino B as final, or tighten the row-strip prompt for one more attempt) —
see `docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md`. Not retrying
automatically given the real per-attempt cost (~$2.40 this run).

## Confirmed decisions

- Primary target: Hermes CLI/TUI.
- OS: Arch Linux.
- Start with native/minimal Hermes-Petdex integration.
- Prepare for a future controlled adapter but do not implement it in MVP.
- Preserve Jorgito identity and action readability; perfection is not required.
- Thinking/review = book + glasses.
- Working/running = shovel + moving earth.
- Every phase has a validation gate; visual gates (identity, action
  readability) are approved by the user, never by a sub-agent on its own.
- Complexity budget applies.
- Isolated Hermes testing uses `HERMES_HOME=/home/chegusan/.hermes-jorgito-test`
  (env var override, verified in source), never `hermes profile create`
  (which nests under `~/.hermes/profiles/`). The real `/home/chegusan/.hermes/`
  must stay untouched until Phase 5 — verified intact after every phase so far.
- Phase 1's native-generation attempt (`agent.pet.generate.orchestrate`) is
  blocked by billing/credentials in this environment (OpenAI: no credit;
  OpenRouter: fixed but user paused further spend) — not a code problem.
- **Phase 2 decision: Camino B** (user generates keyframes externally with
  the canonical reference + prepared prompts; a deterministic Pillow script
  reusing Hermes's own `atlas.py` primitives does chroma-key + fit-to-cell +
  atlas assembly). Zero API image-generation cost in this environment.
  Camino A stays available in the backlog if billing/credentials get
  resolved later — not required for MVP completion.
- Retry budget per visual gate: 4 attempts; if a gate doesn't converge in 4
  attempts, escalate to the user instead of continuing to iterate.

## Open questions

- Non-blocking product decision from F1-B: the unicode half-block terminal
  fallback (tmux/VS Code/plain SSH) degrades prop readability at the
  project's default `display.pet.scale=0.33`; pixel-capable terminals
  (kitty/iTerm2/sixel) read fine. Known Hermes limitation, not
  Jorgito-specific. Revisit before/at Phase 5 if it matters for the target
  environment.
- No graphics-protocol terminal (Kitty/iTerm/Sixel) was available during
  Phase 0/1; only the unicode half-block fallback was exercised end-to-end.

## Next action

Phase 3/4 (Camino B, full 8-state atlas via deterministic `_vary()`
transform) already completed end-to-end on branch `phase-4-full-atlas` —
see `docs/phase_results/PHASE_4_RESULT.md` on that branch. That work is
unaffected by Phase 2B. Current blocker is Phase 2B: waiting on the user to
choose one of its 4 options before any further `hatch_pet()` spend — see
`docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md`.
