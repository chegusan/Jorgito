# 02 — File and Code Rules

## Why this exists

Multi-agent systems tend to create oversized files, duplicated abstractions, and poorly connected modules. These rules prevent that.

## Module rules

Each module must answer one sentence:

> What single responsibility does this file own?

If the answer contains multiple unrelated responsibilities, split it.

Recommended layout if deterministic tooling is needed:

```text
src/
  contracts/
    petdex.py
  assets/
    transforms.py
    atlas.py
  validation/
    package.py
  cli/
    commands.py
tests/
  test_transforms.py
  test_atlas.py
  test_package.py
```

Do not create this structure unless code is actually needed.

## Size guidance

- Ideal module: 100–300 lines.
- Review at >350 lines.
- Above 500 lines requires explicit coordinator approval.
- Functions normally <60 lines.
- Prefer pure functions for image transformations and validation.

Line counts are guidance, not a reason to split cohesive code artificially.

## Connections between files

Connections should be explicit through:
- imports;
- typed function parameters;
- small data structures/contracts;
- filenames that reveal responsibility.

Avoid:
- runtime monkey patches;
- hidden global registries;
- stringly-typed cross-module behavior;
- duplicated constants;
- implicit filesystem conventions scattered across modules.

## Source of truth

One owner per concept:

| Concept | Source of truth |
|---|---|
| Project constraints | `00_PROJECT_BRIEF.md` |
| Architecture | `01_ARCHITECTURE.md` |
| Code/file policy | `02_FILE_AND_CODE_RULES.md` |
| Interface/state contracts | `03_INTERFACES_AND_CONTRACTS.md` |
| Visual identity | `04_ASSET_SPEC.md` |
| Phase sequence | `05_DEVELOPMENT_PLAN.md` |
| Validation | `06_TEST_PLAN.md` |
| Current progress | `08_PROJECT_STATE.md` |
| Permanent decisions | `09_DECISIONS.md` |

Do not restate entire documents elsewhere. Link to them.

## Documentation links

When one document depends on another, reference its filename rather than copying content.

Example:

> Visual acceptance follows `04_ASSET_SPEC.md`.

## Generated artifacts

Keep generated intermediate frames separate from approved outputs:

```text
work/
  generated/
  repaired/
  contact_sheets/
build/
  jorgito/
```

Only approved files enter `build/`.
