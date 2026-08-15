# 01 — Architecture

## Desired MVP path

```text
Hermes Agent
    ↓
Hermes native pet-state mapping
    ↓
Petdex-compatible pet package
    ↓
Hermes CLI/TUI renderer
    ↓
Jorgito
```

## Architectural boundary

Jorgito should be an asset package, not a second agent system.

The pet package contains visual data and metadata. Hermes owns activity/state detection. The renderer owns display.

## Dependency direction

```text
Hermes runtime
    depends on
Pet package contract
    depends on
pet.json + spritesheet
```

Our project should not make Hermes depend on project-specific code during MVP.

## Complexity budget

Escalation order:

1. Native behavior/configuration
2. Pet assets
3. Deterministic asset tooling
4. Tiny adapter
5. Hermes/Petdex modification
6. Fork/custom architecture

The coordinator must document evidence before escalating.

## Future controlled integration

A future optional adapter may map richer Hermes events to existing Petdex states.

Prepare interfaces/documentation for it, but do not implement it until the native MVP is proven insufficient.
