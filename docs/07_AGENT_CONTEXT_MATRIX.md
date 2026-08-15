# 07 — Agent Context Matrix

## Principle

No subagent receives the full conversation or every project file.

The coordinator owns the complete context.

## Coordinator

Give:
- `AGENTS.md`
- `docs/00_PROJECT_BRIEF.md`
- `docs/01_ARCHITECTURE.md`
- `docs/02_FILE_AND_CODE_RULES.md`
- `docs/03_INTERFACES_AND_CONTRACTS.md`
- `docs/04_ASSET_SPEC.md`
- `docs/05_DEVELOPMENT_PLAN.md`
- `docs/06_TEST_PLAN.md`
- `docs/08_PROJECT_STATE.md`
- `docs/09_DECISIONS.md`
- phase results

Asset:
- canonical image only when visually relevant.

## Environment / Compatibility Agent

Give:
- `AGENTS.md`
- `docs/00_PROJECT_BRIEF.md`
- `docs/01_ARCHITECTURE.md`
- Phase 0 section of `docs/05_DEVELOPMENT_PLAN.md`
- Phase 0 section of `docs/06_TEST_PLAN.md`
- `templates/TASK_HANDOFF.md`

Do NOT give:
- full asset spec unless needed;
- conversation history.

Expected output:
- environment facts;
- commands tested;
- PASS/FAIL;
- no implementation beyond compatibility fixes.

## Asset Generation Agent

Give:
- `AGENTS.md`
- `docs/00_PROJECT_BRIEF.md`
- `docs/03_INTERFACES_AND_CONTRACTS.md`
- `docs/04_ASSET_SPEC.md`
- exact state task;
- `assets/reference/jorgito_canonical.png`
- only required upstream format notes.

Do NOT give:
- entire architecture/research transcript;
- unrelated source code.

Expected output:
- requested keyframes/row only;
- generation count;
- visual notes.

## Deterministic Image/Atlas Agent

Give:
- `AGENTS.md`
- `docs/02_FILE_AND_CODE_RULES.md`
- `docs/03_INTERFACES_AND_CONTRACTS.md`
- `docs/04_ASSET_SPEC.md`
- approved input frames;
- exact transformation task;
- relevant tests.

Expected output:
- small deterministic script(s);
- generated derived frames/atlas;
- tests.

## Integration Agent

Give:
- `AGENTS.md`
- `docs/00_PROJECT_BRIEF.md`
- `docs/01_ARCHITECTURE.md`
- `docs/03_INTERFACES_AND_CONTRACTS.md`
- Phase 4/5 sections of `docs/05_DEVELOPMENT_PLAN.md`
- relevant sections of `docs/06_TEST_PLAN.md`
- `docs/08_PROJECT_STATE.md`
- built pet package.

Expected output:
- local install/config changes;
- test evidence;
- no new state-inference layer for MVP.

## QA Agent

Give:
- `AGENTS.md`
- `docs/04_ASSET_SPEC.md`
- `docs/06_TEST_PLAN.md`
- build output;
- canonical image;
- latest phase result.

Do NOT give generation prompts unless diagnosing a failure.

Expected output:
- PASS/FAIL;
- specific defects;
- no self-initiated redesign.

## Coding/Repair Agent

Give only:
- `AGENTS.md`
- `docs/02_FILE_AND_CODE_RULES.md`
- relevant interface contract;
- exact failing test;
- files it may edit.

This role should never receive broad permission to refactor the whole repository.

## What to send at project start

To the coordinator:
1. this complete context pack;
2. canonical Jorgito image;
3. the master project prompt;
4. access to the actual Hermes environment/repository;
5. credentials/tool access only when needed.

Do not send the full ChatGPT conversation unless the coordinator encounters an ambiguity not covered here.
