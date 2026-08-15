# Phase Result

## Phase

Phase 1 — Minimal visual proof (`idle`, `review`, `running`)

## Status

BLOCKED

## Evidence

### 1. Method used (per PHASE_0_RESULT.md recommendation)

Camino A as literally specified in the plan ("Codex CLI + `hatch-pet` skill")
does not exist on this machine (confirmed again in Phase 0). Per Phase 0's
recommendation, this phase used Hermes's own native pet-generation pipeline
directly (`agent/pet/generate/{imagegen,atlas,prompts}.py`,
`agent/pet/store.py`), grounded on
`assets/reference/jorgito_canonical.png` via `reference_images=[...]`.

`orchestrate.hatch_pet()` was deliberately **not** called: it always
generates every non-mirrored row (8 image-generation calls: idle,
running-right, waving, jumping, failed, waiting, running, review) in one
pass, which would blow the 3-generation hard budget for this phase. Instead
a small standalone script, `scripts/generate_phase1.py` (committed in this
branch), drives the same underlying building blocks
(`imagegen.generate()`, `atlas.extract_strip_frames()`,
`atlas.normalize_cells()`, `atlas.compose_atlas()`, `atlas.validate_atlas()`,
`store.register_local_pet()`) for only the 3 requested states — one
generation call per state, matching the plan's Phase 1 scope exactly. This
keeps the change at "small deterministic script reusing existing Hermes
configuration/behavior" (AGENTS.md complexity rung 1/4), not a new
generation engine.

All commands were run with
`HERMES_HOME=/home/chegusan/.hermes-jorgito-test` (the isolated profile from
Phase 0). `/home/chegusan/.hermes/` was not touched — verified unchanged
after this session (see Files changed).

### 2. First attempt — provider `openai` (default resolution)

```text
$ cd /home/chegusan/SGTraining/Jorgito-worktrees/phase-1-minimal-visual-proof
$ HERMES_HOME=/home/chegusan/.hermes-jorgito-test \
    /home/chegusan/.hermes/hermes-agent/venv/bin/python3 scripts/generate_phase1.py

resolved provider: openai (supports_references=True)

=== generating row: idle (6 frames) ===
Traceback (most recent call last):
  ...
  File "/home/chegusan/.hermes/hermes-agent/agent/pet/generate/imagegen.py", line 250, in generate
    raise GenerationError(last_error or "image generation produced no output")
agent.pet.generate.imagegen.GenerationError: OpenAI image editing failed: Error code: 400 -
{'error': {'message': 'Billing hard limit has been reached.', 'type': 'billing_limit_user_error',
'param': None, 'code': 'billing_hard_limit_reached'}}
```

`resolve_provider(require_references=True)` picked `openai` (first available
reference-capable provider in `_REF_CAPABLE` preference order — `nous` and
`openai-codex` are not registered/configured in this environment; `openai`
and `openrouter` are). The call failed at the provider boundary with a
billing hard limit on the account behind `OPENAI_API_KEY`. **No image was
generated or downloaded** — the failure happens before any bytes are
returned, so this did not consume any of the 3-generation budget.

### 3. Second attempt — provider `openrouter` (Hermes's own QA override)

Rather than treating a single provider's billing block as a full stop,
`openrouter` was also registered and reported `is_available() == True` in
this environment (confirmed via direct inspection:
`agent.image_gen_registry.get_provider("openrouter").is_available()`
returns `True` because it resolves a non-empty `api_key` from Hermes's
runtime credential resolution — not from a plain `OPENROUTER_API_KEY` env
var, which is unset here). Hermes ships an official, documented override for
exactly this situation — `HERMES_PET_IMAGE_PROVIDER=<name>` — described in
`imagegen.py`'s own docstring as "an optional QA override to force a
pet-gen backend." Using it is existing Hermes configuration/behavior (rung
1 of AGENTS.md's complexity ladder), not a new tool or workaround, so it was
used to force `openrouter` instead of installing/configuring anything new:

```text
$ HERMES_HOME=/home/chegusan/.hermes-jorgito-test HERMES_PET_IMAGE_PROVIDER=openrouter \
    /home/chegusan/.hermes/hermes-agent/venv/bin/python3 scripts/generate_phase1.py

openrouter image gen failed (401) on openai/gpt-5.4-image-2: Missing Authentication header
resolved provider: openrouter (supports_references=True)

=== generating row: idle (6 frames) ===
Traceback (most recent call last):
  ...
agent.pet.generate.imagegen.GenerationError: OpenRouter image generation failed (401): Missing Authentication header
```

Again, no image was generated or downloaded — the failure is a 401 at the
OpenRouter API boundary, before any bytes are returned. This also did not
consume any of the 3-generation budget.

### 4. No further providers available without new credentials

```text
$ HERMES_HOME=/home/chegusan/.hermes-jorgito-test venv/bin/python3 -c "... list_providers() ..."
deepinfra  False
fal        False
krea       False
nous       False
openai     True   (billing hard limit — see #2)
openai-codex False
openrouter True   (401 missing auth header — see #3)
xai        False
```

Of the 5 providers `imagegen._REF_CAPABLE` will accept for grounded pet rows
(`nous, openai, openai-codex, openrouter, krea`), only `openai` and
`openrouter` are registered/configured in this environment at all, and both
are non-functional for reasons outside this project's scope (account
billing; a broken/stale credential behind Hermes's `openrouter` runtime
resolution). `nous`, `openai-codex`, and `krea` have no credentials
configured here. Per AGENTS.md rung 8 ("ask the user if confirmation or
decisions are needed, do not assume unless stated otherwise") and the task's
own instruction to stop and report rather than chase workarounds,
**generation stopped here** rather than attempting to add new provider
credentials.

### 5. Zero images generated — nothing to visually evaluate yet

Because both available providers failed before returning any image bytes,
`idle`, `review`, and `running` were **not generated**. There is no contact
sheet, no raw asset, and no `jorgito-test` pet to show in this phase. The
F1-A (identity) and F1-B (terminal readability) tests from
`Jorgito  Plan.md` / `docs/06_TEST_PLAN.md` could not be run — there is
nothing to evaluate.

## Tests executed

- `HERMES_HOME=... venv/bin/python3 scripts/generate_phase1.py` (default
  provider resolution → `openai` → billing hard limit, no image produced).
- `HERMES_HOME=... HERMES_PET_IMAGE_PROVIDER=openrouter venv/bin/python3
  scripts/generate_phase1.py` (forced `openrouter` → 401 missing auth
  header, no image produced).
- `HERMES_HOME=... venv/bin/python3 -c "..."` — direct inspection of
  `agent.image_gen_registry.list_providers()` / `get_provider(name)
  .is_available()` for all 8 registered providers and all 5
  reference-capable names, to confirm no other viable provider is
  configured in this environment.
- No F1-A/F1-B visual or in-terminal tests were run (nothing was generated
  to test).

## Cost

- image generations: **0** (both attempts failed before any image was
  returned by the provider)
- retries: 0 beyond the one documented provider-switch (openai → openrouter,
  via Hermes's own `HERMES_PET_IMAGE_PROVIDER` override, not a same-provider
  retry of a bad result)
- approximate model/tool usage: 2 failed API calls (1 to OpenAI's
  gpt-image-2 edit endpoint, 1 to OpenRouter's `openai/gpt-5.4-image-2`),
  both rejected before generating pixels; no billable image generation
  occurred
- development time: ~1 session (Phase 1 attempt, this result)

## Files changed

- Added: `scripts/generate_phase1.py` — the Phase 1 generation script
  (3-generation-budget row driver on top of Hermes's own pet-gen
  primitives). Kept even though it produced no output this run — it is
  correct, tested up to the provider boundary, and is the artifact the next
  attempt should reuse once a working provider is available.
- Added: `docs/phase_results/PHASE_1_RESULT.md` (this file).
- Updated: `docs/08_PROJECT_STATE.md` (phase status, blocker, next action).
- No files added under `work/` or `build/phase1/` — both directories were
  created but remain empty (no bytes were ever produced to write there).
- Verified `/home/chegusan/.hermes/` was not touched: `pets/` dir still
  empty, `config.yaml` mtime unchanged, no `active_profile` file created —
  same check as Phase 0.

## Problems

- OpenAI billing hard limit on the account behind the environment's
  `OPENAI_API_KEY` blocks all `openai`-backed pet-sprite generation until
  the account's billing is fixed by the user (add funds / raise the limit /
  switch keys).
- Hermes's `openrouter` image-gen provider reports `is_available() == True`
  in this environment (it resolves a non-empty `api_key` from Hermes's
  runtime credential store) but the live call fails with `401 Missing
  Authentication header` calling `openai/gpt-5.4-image-2` on OpenRouter.
  This looks like a stale/misconfigured credential specifically for
  OpenRouter image generation inside this Hermes profile/runtime — outside
  this project's scope to fix (would require inspecting/editing credential
  storage, which was not authorized for this phase).
- No other reference-capable provider (`nous`, `openai-codex`, `krea`) is
  configured in this environment; enabling one would require new API keys,
  which is a user decision (AGENTS.md rung 8), not something to assume.

## Bloqueantes

Sí. Ambos proveedores de imagen referencia-capaces disponibles en este
entorno (`openai`, `openrouter`) fallan antes de producir ninguna imagen:
`openai` por límite de facturación de la cuenta, `openrouter` por un header
de autenticación faltante/inválido. Ningún otro proveedor referencia-capaz
tiene credenciales configuradas. Esto bloquea toda generación de imagen para
Fase 1 hasta que el usuario resuelva uno de los dos (o configure un tercer
proveedor) — no es algo que este agente pueda o deba resolver
unilateralmente.

## Decision

stop

## Next phase/task

Fase 1 no puede continuar hasta que el usuario resuelva al menos uno de:

1. Levantar/arreglar el límite de facturación en la cuenta de OpenAI detrás
   de `OPENAI_API_KEY` (usada por Hermes para `gpt-image-2`), o
2. Corregir la credencial de OpenRouter que Hermes está resolviendo para
   `openrouter` (actualmente devuelve 401 "Missing Authentication header"
   pese a que `is_available()` la reporta como configurada), o
3. Configurar explícitamente otro proveedor referencia-capaz (`nous` o
   `krea`) con credenciales nuevas.

Una vez resuelto, la Fase 1 puede reintentarse ejecutando exactamente:

```bash
cd /home/chegusan/SGTraining/Jorgito-worktrees/phase-1-minimal-visual-proof
HERMES_HOME=/home/chegusan/.hermes-jorgito-test \
  [HERMES_PET_IMAGE_PROVIDER=<name> si hace falta forzar un proveedor] \
  /home/chegusan/.hermes/hermes-agent/venv/bin/python3 scripts/generate_phase1.py
```

`scripts/generate_phase1.py` ya implementa el resto de la Fase 1 (3
generaciones exactas, extracción de frames, atlas parcial de 3/9 filas,
`validate_atlas()`, instalación como pet de prueba `jorgito-test`); falta
únicamente construir el contact sheet (`build/phase1_contact_sheet.png`) y
correr `hermes pets show jorgito-test --state {idle,review,run}` para F1-B,
ambos pasos triviales una vez que existan frames reales. No se debe volver a
intentar generación sin que el usuario confirme que uno de los proveedores
de arriba ya funciona, para no gastar más intentos contra un proveedor roto.
