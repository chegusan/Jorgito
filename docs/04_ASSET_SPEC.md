# 04 — Jorgito Asset Specification

## Canonical reference

`assets/reference/jorgito_canonical.png`

This file is the identity source of truth.

## Identity invariants

Must remain visually obvious:
- large green eyes with visible white;
- small horns;
- crimson/burgundy body;
- yellow belly/neck;
- yellow wing membranes;
- compact friendly dragon proportions;
- two arms and two hind legs;
- curled tail;
- friendly/non-aggressive face.

## Readability priority

At actual CLI scale, the user should quickly recognize:
1. Jorgito;
2. what Jorgito is doing.

Tiny detail is lower priority.

## Required hero actions

### Review / Thinking
- glasses clearly visible;
- book clearly visible;
- reading/concentrating pose;
- minimal loop;
- possible page movement or blink.

### Running / Working
- shovel clearly visible;
- repeated digging/moving-earth action;
- earth should remain a small visual accent;
- body silhouette must stay readable.

## Secondary actions

### Idle
Breathing, blink, small tail movement.

### Waiting
Still/sitting pose with small eye/head movement.

### Failed
Friendly confused reaction; optional tiny smoke puff.

### Jumping
Short celebratory jump; slight wing opening.

### Waving
Simple clear arm wave.

### Running left/right
Simple motion. Mirror when safe.

## Generation rule

Do not generate all frames individually unless evidence shows it is cheaper and more consistent than keyframe + deterministic derivation.

Initial visual test uses only:
- idle;
- review;
- running.

Maximum normal retry budget per test state:
- 1 initial generation;
- 1 repair/regeneration.

A third attempt requires coordinator approval.
