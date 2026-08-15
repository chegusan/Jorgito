# Jorgito Petdex Context Pack

This folder is the working context for a multi-agent implementation of Jorgito as a Petdex-compatible mascot inside Hermes CLI/TUI on Arch Linux.

## Start here

1. Read `AGENTS.md`.
2. The coordinator then reads:
   - `docs/00_PROJECT_BRIEF.md`
   - `docs/01_ARCHITECTURE.md`
   - `docs/05_DEVELOPMENT_PLAN.md`
   - `docs/06_TEST_PLAN.md`
   - `docs/08_PROJECT_STATE.md`
3. Give subagents only the role-specific context defined in `docs/07_AGENT_CONTEXT_MATRIX.md`.
4. Do not pass the full conversation history to subagents.

## Canonical asset

`assets/reference/jorgito_canonical.png` is the approved visual identity reference.

## Goal

Build the smallest reliable implementation that:
- runs inside Hermes CLI/TUI;
- uses existing Hermes/Petdex behavior whenever possible;
- preserves Jorgito's visual identity;
- keeps development, code complexity, token use, and generation cost low;
- validates each phase before continuing.
