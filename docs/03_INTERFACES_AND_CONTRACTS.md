# 03 — Interfaces and Contracts

## Pet package contract

The target package must remain Petdex/Codex compatible:

```text
jorgito/
  pet.json
  spritesheet.png | spritesheet.webp
```

The standard atlas uses:
- 8 columns;
- 9 state rows;
- 192 × 208 px per frame;
- standard atlas size 1536 × 1872 px.

Do not introduce a proprietary asset format for the MVP.

## Standard row order

The current OpenAI pet atlas validator defines these state rows:

1. idle
2. running-right
3. running-left
4. waving
5. jumping
6. failed
7. waiting
8. running
9. review

Use existing upstream validators instead of implementing another validator unless required.

## Jorgito semantic mapping

| Petdex state | Jorgito meaning |
|---|---|
| idle | resting / ready |
| running-right | simple movement |
| running-left | mirrored/simple movement |
| waving | greeting / positive acknowledgement |
| jumping | celebration |
| failed | friendly error reaction |
| waiting | waiting |
| running | WORKING: shovel + earth |
| review | THINKING: book + glasses |

## Asset-transform interface

If deterministic scripts are required, prefer small pure operations such as:

```text
mirror_frame(image) -> image
offset_frame(image, dx, dy) -> image
compose_layer(base, overlay) -> image
build_atlas(rows) -> atlas
validate_atlas(path) -> report
```

Avoid building an animation framework.

## State mapping ownership

Hermes owns runtime state detection.

Jorgito owns only the visual interpretation of a Petdex state.

Do not duplicate Hermes state inference in project code during MVP.
