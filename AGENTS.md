# AGENTS.md — Operating Rules

## Core rule

Build the smallest solution that works correctly.

Before writing new code, prefer in this order:

1. Existing Hermes configuration/behavior
2. Existing Petdex format/tools
3. Asset changes
4. Small deterministic scripts
5. Small external adapter
6. Upstream modification
7. Fork/custom infrastructure
8. Ask the user if confirmation or decisions are needed , do not asume unless stated otherwise

Do not move down the list without evidence that the simpler option is insufficient.

## Phase gates

Every phase ends in PASS or FAIL.

A FAIL blocks the next phase.

Use `templates/PHASE_RESULT.md` for every gate.

## Context discipline

Do not load the complete project into every subagent.

Each subagent receives:
- one task brief;
- only the relevant project docs;
- only the files it may inspect or modify;
- explicit acceptance criteria.

Use `docs/07_AGENT_CONTEXT_MATRIX.md`.

## File discipline

Code and documentation must remain navigable.

### Code
- One clear responsibility per module.
- Prefer modules around 100–300 lines.
- Soft warning at 350 lines.
- Hard review required above 500 lines.
- Functions should normally stay under ~60 lines.
- Split by responsibility, not arbitrarily by line count.
- Avoid circular imports.
- Shared data contracts/types belong in one clearly named module.
- Do not create `utils.py`/`helpers.py` dumping grounds.
- No duplicated state mapping in multiple files.
- No hidden global state unless required by an upstream interface.

### Documentation
- One topic per document.
- Prefer 1–4 pages of Markdown per document.
- Keep current-state files short and replace stale status instead of appending indefinitely.
- Permanent decisions go in `docs/09_DECISIONS.md`.
- Test evidence goes in phase results, not in architecture docs.

## Change discipline

A subagent must not modify unrelated files.

Every completed task must report:
- files read;
- files changed;
- reason for each change;
- tests run;
- result;
- unresolved issues.

## Cost discipline

Before invoking a generative model ask:

> Can this be solved deterministically?

If yes, use deterministic code.

Image work priority:
1. reuse;
2. crop/compose;
3. mirror;
4. transform;
5. generate.

Do not regenerate an entire state when a localized deterministic repair is enough.

## Runtime discipline

The final mascot must not require:
- extra LLM calls while Hermes runs;
- a permanent background AI process;
- Petdex Desktop;
- a custom daemon for the MVP.

## Ownership

The coordinator is the only role allowed to:
- advance phases;
- change scope;
- approve fallback to a more complex architecture;
- declare MVP complete.
