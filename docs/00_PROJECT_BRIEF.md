# 00 — Project Brief

## Project

Jorgito: a Petdex-compatible animated mascot for Hermes CLI/TUI on Arch Linux.

## Primary objective

Show Jorgito inside Hermes and communicate agent activity visually using the native Petdex/Hermes state system with minimal custom code.

## Optimization priorities

1. Functionality
2. Compatibility
3. Visual clarity
4. Preservation of Jorgito identity
5. Low code complexity
6. Low token usage
7. Low image-generation cost
8. Easy maintenance

## Visual identity

Canonical image: `../assets/reference/jorgito_canonical.png`

Must preserve:
- friendly small dragon;
- huge green eyes with visible white;
- friendly/slightly goofy expression;
- small horns;
- compact rounded proportions;
- crimson/burgundy body;
- yellow neck/belly plates;
- two hind legs;
- two front arms;
- folded wings with yellow membranes;
- long curled tail;
- clean readable pixel-art appearance.

Small frame-to-frame variation is acceptable if identity and action remain obvious.

## Key action choices

- `review` / thinking: Jorgito reads a book while wearing glasses.
- `running` / working: Jorgito uses a shovel and moves/digs earth.

Secondary states should remain deliberately simple.

## Non-goals for MVP

- Petdex Desktop
- custom state protocol
- custom pet runtime
- emotions system
- sound
- mascot memory
- mini-agent visualization
- custom server/daemon
- fork of Hermes/Petdex
- perfect frame-by-frame artistic consistency
