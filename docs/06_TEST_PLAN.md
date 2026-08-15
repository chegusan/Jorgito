# 06 — Test Plan

## Test philosophy

Test the cheapest assumption first.

Do not spend image-generation budget before environment compatibility is proven.

## Phase 0

### P0.1 Renderer
Known pet displays inside Hermes.

PASS: visible and stable.

### P0.2 State playback
Available pet states can be invoked/cycled.

PASS: renderer changes animation as expected.

---

## Phase 1

### P1.1 Identity
Compare key frames to canonical Jorgito.

PASS if:
- eyes/colors/horns/wings/tail remain recognizable;
- face remains friendly;
- no major anatomy drift.

### P1.2 Thinking readability
Render `review` at real terminal scale.

PASS: user can identify reading/thinking without zooming.

### P1.3 Working readability
Render `running` at real terminal scale.

PASS: shovel and digging/moving-earth action are clear.

---

## Phase 2

### P2.1 Cost comparison
Record:
- generation calls;
- retries;
- manual repair time;
- deterministic processing time.

PASS: choose lower-complexity acceptable route.

---

## Phase 3

### P3.1 Row coherence
Each row loops without obvious broken frame transitions.

### P3.2 State distinctness
Actions are not easily confused.

### P3.3 Left/right derivation
Mirrored state does not create impossible props/text/asymmetry.

---

## Phase 4

### P4.1 Atlas geometry
Upstream validator passes.

### P4.2 Package load
Hermes loads the pet without runtime modification.

---

## Phase 5

Run real Hermes scenarios.

Record event → expected state → observed state.

PASS criteria:
- major states work;
- no crashes;
- no new background AI process;
- no perceptible Hermes slowdown attributable to project code.

---

## MVP acceptance

MVP is accepted when:
- Jorgito renders inside Hermes CLI/TUI;
- thinking = book + glasses;
- working = shovel + earth;
- identity is clearly preserved;
- standard package validates;
- no fork or custom daemon is required;
- runtime use has no recurring model/token cost.
