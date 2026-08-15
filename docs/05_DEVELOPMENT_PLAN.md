# 05 — Phased Development Plan

## Phase 0 — Environment and compatibility audit

Goal: prove Hermes can display a known Petdex pet correctly on the current Arch Linux terminal.

Tasks:
- inspect Hermes version/config;
- run pet diagnostics if available;
- identify renderer/protocol;
- install/select a known pet;
- manually show/cycle states;
- verify Codex and `hatch-pet` availability if they will be used.

Gate:
- PASS only when an existing pet renders reliably.

Do not create Jorgito assets before PASS.

---

## Phase 1 — Minimal visual proof

Generate only:
- idle;
- review (book + glasses);
- running (shovel + earth).

Use the approved Jorgito reference.

Evaluate:
- identity preservation;
- action clarity;
- real terminal readability.

Gate:
- PASS only when all three are recognizable and readable in Hermes.

---

## Phase 2 — Choose generation strategy

Compare actual evidence from Phase 1.

### Path A
Use upstream/AI pet-generation workflow if:
- identity is stable;
- retries are low;
- cost is acceptable;
- assets are easy to package.

### Path B
Use keyframes + deterministic transformations if:
- independent generation drifts;
- retries become expensive;
- frames can be cheaply derived.

Do not decide by preference; decide from measured results.

---

## Phase 3 — Complete standard states

Finish all standard Petdex rows.

Keep secondary actions minimal.

Prefer:
- mirrored running-left from running-right when visually safe;
- repeated/held frames;
- deterministic transforms;
- simple cycles.

Gate:
- all states visually valid and coherent.

---

## Phase 4 — Package construction

Produce:
```text
build/jorgito/
  pet.json
  spritesheet.png|webp
```

Use existing atlas/package validators.

Gate:
- structural validation passes with no custom Hermes change.

---

## Phase 5 — Real Hermes integration

Select Jorgito and test real tasks that trigger:
- idle;
- review;
- running;
- waiting;
- failed;
- wave/jump as supported.

Gate:
- expected Jorgito action appears during actual Hermes use.

---

## Phase 6 — Optimization

Only optimize measured problems:
- atlas size;
- visible jitter;
- scale;
- frame redundancy;
- terminal readability.

No speculative optimization.

---

## Phase 7 — Controlled-integration readiness

Document, but do not implement, the smallest future adapter point for richer state control.

MVP ends before this adapter unless native behavior is proven inadequate.
