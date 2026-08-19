# Phase Result

## Phase

Phase 2 — Decisión Camino A vs Camino B para completar los 5 estados
restantes (`waiting`, `failed`, `jump`, `wave`, `running-right`;
`running-left` se deriva por espejo horizontal, no requiere generación).

## Status

PASS (decisión tomada con datos reales, no por preferencia)

## Evidencia usada (de Fase 0 y Fase 1, ver esos `PHASE_x_RESULT.md`)

### Camino A (pipeline nativo de generación de imagen de Hermes)

- Fase 0 confirmó que `codex hatch-pet` (Camino A tal como lo describía el
  plan original) **no existe** en este equipo; Hermes trae su propia
  reimplementación nativa (`agent/pet/generate/orchestrate.py`).
- Fase 1 intentó ese pipeline nativo con `reference_images=[jorgito_canonical.png]`
  y falló en **los dos** proveedores capaces de imagen de referencia
  configurados en este entorno, **antes** de devolver ninguna imagen:
  - `openai`: `400 billing_hard_limit_reached` (cuenta sin crédito).
  - `openrouter`: `401 Missing Authentication header` en el modelo gateado
    por defecto; diagnosticado y reparado (`OPENROUTER_IMAGE_MODEL=google/gemini-3-pro-image`
    en el perfil aislado), pero el usuario frenó explícitamente cualquier
    generación adicional por falta de tokens/crédito antes de usar ese
    arreglo ("Frena ahi, no hay tokens").
- **0 de 3** del presupuesto de generación de Fase 1 llegó a gastarse por
  esta vía — el bloqueo es de credenciales/facturación, no del código de
  Hermes ni del prompt.

### Camino B (generación externa manual + derivación determinística)

- Fase 1 se completó **de punta a punta** por este camino:
  1. El usuario generó `idle`/`review`/`run` externamente (sin costo de API
     en este entorno), usando `jorgito_canonical.png` como referencia y los
     prompts ya preparados (bloque base + acción por estado).
  2. `scripts/process_phase1_keyframes.py` (Pillow puro, sin red, ~130
     líneas) hizo chroma-key + fit-to-cell reusando las primitivas ya
     existentes de Hermes (`agent.pet.generate.atlas.remove_background()`,
     `_fit_to_cell()`) — sin reinventar esa lógica.
  3. Gate F1-A (identidad): **PASS**, aprobado explícitamente por el usuario
     ("Están perfectos").
  4. Gate F1-B (legibilidad en terminal real): **PASS**, verificado
     instalando el pet de prueba `jorgito-test` en el perfil aislado
     (`HERMES_HOME=~/.hermes-jorgito-test`) y renderizando con
     `hermes pets show` real (evidencia ANSI + PNG en
     `assets/keyframes/terminal_render_phase1/`).
  5. `/home/chegusan/.hermes/` real confirmado intacto en todo momento.

## Decisión

**Camino B para los 5 estados restantes** (`waiting`, `failed`, `jump`,
`wave`, `running-right`; `running-left` = espejo horizontal de
`running-right`, sin generación adicional).

Razones:

1. **Es el único camino validado de punta a punta ahora mismo.** Camino A
   está bloqueado por facturación/credenciales fuera de nuestro control
   inmediato (decisión explícita del usuario de no gastar más tokens);
   Camino B ya demostró funcionar completo, con ambos gates visuales en
   PASS y evidencia real de instalación/renderizado en Hermes.
2. **Costo cero de API en este entorno.** El único costo es la generación
   externa del usuario, que de todas formas coincide con el presupuesto ya
   definido en `docs/04_ASSET_SPEC.md` (1 generación inicial + 1 reintento
   por estado) — no es un costo adicional al plan original, solo un cambio
   de *dónde* ocurre la generación.
3. **Respeta la escalera de complejidad de AGENTS.md.** El script de
   procesamiento sigue en el escalón "reusar comportamiento/config existente
   de Hermes", sin agregar un nuevo motor de generación ni credenciales
   nuevas al proyecto.
4. **Camino A queda en el backlog, no descartado.** Si en el futuro (Fase 6
   optimización, o necesidad de regenerar algo) se resuelve el crédito de
   OpenAI o se habilita la integración OpenAI en OpenRouter, Camino A sigue
   disponible sin cambios de arquitectura — el pipeline nativo no se tocó,
   solo no se usó para completar el MVP.

## Cost

- image generations (vía API, este entorno): 0
- retries: 0
- approximate model/tool usage: 1 sub-agente `explore` (Fase 0), 3
  sub-agentes `implement` (Fase 1: intento API bloqueado, procesamiento
  determinístico, F1-B legibilidad terminal)
- development time: ~1 sesión de trabajo (Fase 0 + Fase 1 + esta decisión)

## Files changed

- `docs/phase_results/PHASE_2_RESULT.md` (este archivo)

## Problems

- Ninguno bloqueante. Nota no bloqueante heredada de F1-B: el modo de
  fallback unicode (half-blocks) de Hermes degrada la legibilidad de los
  props a la escala default (`display.pet.scale=0.33`) en terminales sin
  soporte de píxeles reales (kitty/iTerm2/sixel) — limitación conocida de
  Hermes, no específica de Jorgito, pendiente de decisión de producto no
  bloqueante para Fase 2+.

## Decision

continue

## Next phase/task

Fase 3 (generación de los 5 keyframes restantes por Camino B) + Fase 4
(script de derivación/atlas completo). Bloqueado únicamente en que el
usuario genere externamente `waiting`, `failed`, `jump`, `wave` y
`running-right` con los prompts ya entregados (mismo bloque base +
`jorgito_canonical.png` como referencia), respetando el presupuesto de 1
generación + 1 reintento por estado. En cuanto estén guardados, se
despacha un sub-agente `implement` para: generalizar
`scripts/process_phase1_keyframes.py` a los 8 estados (incluyendo el
espejo de `running-left`), armar el atlas completo, validarlo con
`atlas.validate_atlas()`, y generar el contact sheet final de 8 estados
para el gate visual F3.
