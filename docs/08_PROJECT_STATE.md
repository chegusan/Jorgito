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
- Phase 2B addendum #1 — **single-pose pilot, `review` state only, DONE.**
  Instead of a multi-pose row strip per state, generate ONE centered pose per
  API call (`imagegen.generate(n=1, ...)`, already single-image-per-call).
  Piloted on `review` (one of Phase 2B's 4 failed states) to test whether
  this sidesteps the segmentation problem. Result: clean single-subject
  output, no segmentation artifacts, **$0.1415** (vs. ~$2.40 for the
  row-strip run). Superseded by addendum #2 below (single wobbled pose
  wasn't real animation) but the pose it produced is now "pose 1" of that
  addendum's 3-pose sequence.
- Phase 2B addendum #2 — **real pose variation for `review`'s row, DONE,
  human gave PASS.** Human feedback on addendum #1: one static pose expanded
  across a row via deterministic wobble (Phase 4's `_vary()`) isn't real
  animation. Generated 2 additional real poses (3 total: book
  open/starting → mid-page-turn → page turned further), each `generate()`
  call grounded on canonical + the previous pose's raw output (chained
  continuity), then built the real 6-frame `review` row (frame count
  confirmed from Hermes's own `atlas.ROW_SPECS`) in ping-pong order
  (`[1,2,3,3,2,1]`) with the Phase 4 wobble applied on top of each real pose
  (not instead of it). Validated with Hermes's real `atlas.validate_atlas()`
  (`ok: true`, review row only). 6/6 unique frame hashes. **$0.2823** for 2
  new API calls. Visual gate evidence:
  `assets/keyframes/review_row_contact_sheet.png` (labeled) and
  `assets/keyframes/review_row_preview.gif` (looping). See the addendum in
  `docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md`.
- Phase 2B addendum #3 — **refactor to state-parameterized functions +
  `waiting` row, DONE, awaiting human visual gate.** Generalized addendum
  #2's `review`-only scripts into `scripts/pose_sequence.py`
  (`generate_pose_sequence`) + `scripts/state_row.py` (`build_state_row`),
  so each further state needs only a thin ~30-line runner script. Refactor
  verified byte-identical against `review`'s committed outputs (dry
  re-run of the row-assembly step, zero `git diff`, same 6/6 hashes) — no
  new spend on `review`. Applied the pattern to `waiting` (row also 6
  frames, per `atlas.ROW_SPECS`): 3 real chained poses (centered/settled →
  glance left → glance right), `validate_atlas()` `ok: true`, 6/6 unique
  hashes. **$0.4265** for 3 new API calls (~$0.1422/call). Visual-gate
  evidence: `assets/keyframes/waiting_row_contact_sheet.png` /
  `waiting_row_preview.gif`. **Caveat for the visual gate:** the 3 poses
  came out visually closer together than the "look left / look right"
  prompt asked for — differences are mostly in stance/tail/eye direction
  rather than a strongly legible head turn (see the addendum for the
  contact-sheet crop). Not retried (one API call per pose, no
  retry/fallback, per guardrails).
- Phase 2B addendum #4 — **`failed` row, DONE, awaiting human visual gate.**
  Same generalized pattern applied to `failed` (row is 8 frames, per
  `atlas.ROW_SPECS` — longer than `review`/`waiting`'s 6). 3 real chained
  poses depicting a friendly confused/error reaction (neutral confused →
  arm raised scratching head → both arms up with a small smoke puff), each
  action description written to force a structurally different body pose
  (learned from `waiting`'s "too subtle" caveat). Result: the 3 poses read
  as clearly distinguishable at a glance, unlike `waiting`.
  `_pingpong_order(3, 8)` = `[0,1,2,2,1,0,0,1]`, Phase 4 wobble applied on
  top. `validate_atlas()` `ok: true`, 8/8 unique hashes. **$0.4210** for 3
  new API calls (~$0.1403/call). Visual-gate evidence:
  `assets/keyframes/failed_row_contact_sheet.png` /
  `failed_row_preview.gif` (sent to the user). **Caveat for the visual
  gate:** pose 3's raw generation includes a soft drop-shadow that didn't
  fully chroma-key out — a small green patch is visible under the feet in
  columns 2 and 3 (the two columns using pose 3). Not retried (one call per
  pose, no retry/fallback, per guardrails). **Resolved by addendum #5** (see
  below) — no longer an open caveat.
- Phase 2B addendum #5 — **`failed` row chroma-key fix, DONE, PASS.** Fixed
  addendum #4's shadow-patch caveat with a deterministic reprocessing pass
  (`scripts/pose_sequence.py`'s new `_flood_extend_transparency` /
  `_remove_background_despilled`, shared by all states going forward), zero
  API calls, zero cost. Green patch pixel count in `failed_pose3.png`: 1474
  → 1. `validate_atlas()` `ok: true`, 8/8 unique hashes (only columns 2/3
  changed, matching pose 3's columns exactly). Every other row's assets
  confirmed byte-identical via `sha256sum`. Real `~/.hermes` confirmed
  untouched. Before/after crop sent to the user
  (`assets/keyframes/failed_pose3_chromakey_fix_before_after.png`). Branch
  `phase2b-fix-failed-chromakey`, PR opened against
  `phase2b-hatch-pet-regen`. See the addendum in
  `docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md`.
- Phase 2B addendum #6 — **`waving` row, DONE, awaiting human visual gate.**
  Same generalized pattern (despill-protected by default since addendum #5)
  applied to `waving` (real key/count confirmed from `atlas.ROW_SPECS`:
  `("waving", 3, 4)` — 4 frames, the shortest row so far, NOT `wave`/6). 3
  real chained poses (arm starting to raise → peak of the wave → mid-swing
  on the opposite side), `validate_atlas()` `ok: true`, 4/4 unique hashes.
  **$0.1418** for 3 new API calls. Visual-gate evidence:
  `assets/keyframes/waving_row_contact_sheet.png` /
  `waving_row_preview.gif` (sent to the user). **Caveat for the visual
  gate:** pose 3 reads as "swept inward near the face" rather than a
  dramatically opposite-side position — still visually distinct from poses
  1/2 (different silhouette/height), but a weaker side-to-side read than
  intended. Not retried (one call per pose, no retry/fallback, per
  guardrails). Branch `phase2b-pose-sequence-wave`, PR opened against
  `phase2b-fix-failed-chromakey`. See the addendum in
  `docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md`.
- Phase 2B addendum #7 — **`running-right` row, DONE, awaiting human visual
  gate.** Same generalized pattern applied to `running-right` (real key/
  count confirmed from `atlas.ROW_SPECS`: `("running-right", 1, 8)`).
  3 real chained stride poses, `validate_atlas()` `ok: true`, 8/8 unique
  hashes. **$0.2813** for 3 new API calls. **Caveat:** all 3 poses rendered
  LEFT-facing despite every prompt explicitly asking for a rightward-facing
  stride. Branch `phase2b-pose-sequence-running-right`, PR #8 opened
  against `phase2b-pose-sequence-wave`. **Superseded by addendum #8** (see
  below) — the caveat above was resolved by relabeling, not a retry.
- Phase 2B addendum #8 — **relabel `running-right`→`running-left` + derive
  `running-right` as its mirror, DONE, awaiting human visual gate.**
  Zero-cost fix for addendum #7's left-facing caveat: instead of
  re-spending API budget on a retry, the human relabeled addendum #7's
  already-generated, already-validated row as `running-left` (it already
  faces left) and derived `running-right` as its horizontal mirror using
  Hermes's own `atlas.mirror_frames()` (same primitive `phase-4-full-atlas`
  used, direction reversed). **$0.00** — zero new `generate()` calls, pure
  Pillow + Hermes's real `validate_atlas()`. Both rows: `ok: true`, 8/8
  unique hashes each, all 16 hashes pairwise distinct. Visual-gate evidence
  for both rows sent to the user
  (`assets/keyframes/{running-left,running-right}_row_contact_sheet.png` /
  `_row_preview.gif`). Same branch/PR #8 as addendum #7. See the addendum in
  `docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md`.

## Active objective

**All 9 Hermes pet states now have real content** (`idle`, `run`, `review`,
`waiting`, `failed`, `jumping`, `waving`, `running-right`, `running-left` —
per the user's confirmation after addendum #8). Waiting on the user's
visual-gate judgment across every row still pending approval: addendum #3's
`waiting`, addendum #4/#5's `failed`, addendum #6's `waving`, and addendum
#7/#8's `running-left`/`running-right` pair
(`assets/keyframes/{waiting,failed,waving,running-left,running-right}_row_contact_sheet.png`
/ `..._row_preview.gif`). `failed`'s shadow-patch caveat is resolved
(addendum #5); `waving`'s only caveat is pose 3's weaker side-to-side read
(addendum #6); `running-right`'s left-facing caveat is resolved by
relabeling + mirroring, not a retry (addendum #8) — each row's remaining
question for the human gate is pose-quality/identity, same as every other
row. If any row is rejected outright, or as a broader decision, fall back
to Phase 2B's original 4 options (retry same model, try a different
`OPENROUTER_IMAGE_MODEL`, abandon Path A and keep Phase 3/4's Camino B as
final, or tighten the row-strip prompt) — see
`docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md`.

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
unaffected by Phase 2B.

Phase 2B's real-pose-sequence track (addenda #1-#8) now has real content
for all 9 Hermes pet states (see "Active objective" above) — current
blocker is the human's visual gate across every row still pending approval,
not further generation spend. See
`docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md` for per-row evidence and
caveats.
