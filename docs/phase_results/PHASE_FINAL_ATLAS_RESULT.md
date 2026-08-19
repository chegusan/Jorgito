# Phase Final: ATLAS FINAL COMPLETO — reconciliación de 9 estados

**Status: PASS.** Último gate visual de contenido antes de Fase 5 (instalación
en el Hermes real del usuario, tarea separada, pendiente de aprobación).

Este documento reconcilia el trabajo repartido en 5 PRs/ramas de
`github.com/chegusan/Jorgito` en un único atlas de 9 estados, **sin
regenerar ningún frame y sin llamadas a la API de generación de imágenes**.
Toda la composición final se hizo con `agent.pet.generate.atlas` real de
Hermes (`compose_atlas()` / `validate_atlas()`), no una reimplementación.

## Rama de integración

`phase-final-atlas-integration`, creada desde el tip de PR #8
(`phase2b-pose-sequence-running-right` @ `427c804`).

## Procedencia por fila (de dónde vino cada estado)

| Estado | Fuente | Rama | Commit | PR | Frames | Generación |
|---|---|---|---|---|---|---|
| `idle` | `atlas_full.png` fila 0 | `phase-4-full-atlas` | `7353a27` | #3 | 6 | pipeline determinístico (1 keyframe Fase 1 + variación matemática bob/tilt/scale) |
| `running-right` | `running-right_row_atlas_fragment.png` fila 1 | `phase2b-pose-sequence-running-right` | `427c804` (addendum #8) | #8 | 8 | 3 poses IA encadenadas + ping-pong; **derivada por espejo** de `running-left` vía `atlas.mirror_frames()` (addendum #7 generó las poses mirando a la izquierda pese al prompt) |
| `running-left` | `running-left_row_atlas_fragment.png` fila 2 | `phase2b-pose-sequence-running-right` | `427c804` (addendum #8) | #8 | 8 | 3 poses IA encadenadas + ping-pong (addendum #7, relabeled) |
| `waving` | `waving_row_atlas_fragment.png` fila 3 | `phase2b-pose-sequence-wave` | `2ce096a` | #7 (mergeado en cadena #8) | 4 | 3 poses IA encadenadas |
| `jumping` | `jumping_row_atlas_fragment.png` fila 4 | `phase2b-pose-sequence-jump` | `0c4432f` | #5 (cherry-pick directo, nunca mergeado en la cadena #6→#7→#8) | 5 | 3 poses IA encadenadas + ping-pong |
| `failed` | `failed_row_atlas_fragment.png` fila 5 | `phase2b-fix-failed-chromakey` | `fc4678f` | #6 (mergeado en cadena #8) | 8 | 3 poses IA encadenadas (fix de chroma-key shadow en pose 3) |
| `waiting` | `waiting_row_atlas_fragment.png` fila 6 | `phase2b-hatch-pet-regen` | `fd615f1` | mergeado en cadena #8 | 6 | 3 poses IA encadenadas |
| `running` | `atlas_full.png` fila 7 | `phase-4-full-atlas` | `7353a27` | #3 | 6 | pipeline determinístico (1 keyframe Fase 1 "run" + variación matemática) |
| `review` | `review_row_atlas_fragment.png` fila 8 | `phase2b-hatch-pet-regen` | `a7d9006` | mergeado en cadena #8 | 6 | 3 poses IA encadenadas, ping-pong |

`idle`/`running` deliberadamente NO se regeneraron con IA — decisión previa
("run/idle no hace falta regenerar, ya están aprobados"), confirmada de
nuevo acá.

## Cómo se ensambló (sin regenerar nada)

`scripts/build_final_atlas.py`:

1. Cada fila fuente (`*_row_atlas_fragment.png`, y `atlas_full.png` para
   idle/running) es en sí misma un atlas completo 1536x1872 ya compuesto por
   `compose_atlas()` en su rama de origen, con solo su propia fila ocupada.
2. Se recorta la banda de 208px de esa fila propia en su propio archivo
   fuente — recupera exactamente las mismas celdas 192x208 ya validadas,
   byte a byte (operación Pillow pura, cero red, cero API).
3. Las 9 filas recortadas se combinan en un solo `frames_by_state` y se
   llama a `agent.pet.generate.atlas.compose_atlas()` real (no
   reimplementado) para producir el atlas final 1536x1872.
4. Se valida con `agent.pet.generate.atlas.validate_atlas()` real.
5. Se calcula hash sha256 (16 hex) por celda, por fila, para chequear
   unicidad intra-fila (el bug de Fase 4 original: columnas espejadas con
   `sin(theta)==sin(pi-theta))` byte-idénticas).

## Resultado `validate_atlas()`

```json
{
  "ok": true,
  "width": 1536,
  "height": 1872,
  "errors": [],
  "warnings": [],
  "filled_states": ["idle","running-right","running-left","waving",
                     "jumping","failed","waiting","running","review"]
}
```

**9/9 estados llenos, 0 errores, 0 warnings.**

## Unicidad de hashes por fila (chequeo crítico post-Fase 4)

| Estado | count | unique | ¿todas distintas? |
|---|---|---|---|
| idle | 6 | 6 | sí |
| running-right | 8 | 8 | sí |
| running-left | 8 | 8 | sí |
| waving | 4 | 4 | sí |
| jumping | 5 | 5 | sí |
| failed | 8 | 8 | sí |
| waiting | 6 | 6 | sí |
| running | 6 | 6 | sí |
| review | 6 | 6 | sí |

Ninguna fila tiene frames repetidos dentro de sí misma. Hashes completos en
`assets/keyframes/atlas_final_report.json`.

## Archivos de salida

- `assets/keyframes/atlas_final.png` — atlas 1536x1872 RGBA (md5
  `127e61046bfc95912df7d6ec5b189e08`)
- `assets/keyframes/atlas_final.webp` — mismo atlas, WebP sin pérdida (md5
  `c3466f0eda49d478143d0369319df5b6`) — formato real de `pet.json` /
  `spritesheet.webp` en el pet-store de Hermes
- `assets/keyframes/atlas_final_report.json` — validate_atlas() +
  hashes por fila + procedencia
- `assets/keyframes/atlas_final_contact_sheet.png` — contact sheet estático
  etiquetado, celdas a resolución nativa 192x208 (enviado al usuario)
- `assets/keyframes/atlas_final_collage.gif` — collage animado de los 9
  estados en un solo GIF, cada fila ciclando sus propios frames (enviado al
  usuario)

## Instalación (perfil aislado únicamente)

```
HERMES_HOME=/home/chegusan/.hermes-jorgito-test \
  /home/chegusan/.hermes/hermes-agent/venv/bin/python3 \
  scripts/install_final_atlas_pet.py
```

Usa `agent.pet.store.register_local_pet()` real (mismo path que `/hatch`),
slug `jorgito`, sobrescribiendo el pet `jorgito` que Fase 4 había instalado
ahí antes (mismo perfil aislado, reutilizado entre fases).

```
registered pet 'jorgito' -> /home/chegusan/.hermes-jorgito-test/pets/jorgito/spritesheet.webp
  exists=True generated=True
```

## Guardas de seguridad — verificadas antes y después

| Chequeo | Antes | Después |
|---|---|---|
| md5 `~/.hermes/config.yaml` | `66684dd3b378e4584ab08ab097024ed4` | `66684dd3b378e4584ab08ab097024ed4` (sin cambios) |
| `~/.hermes/pets/` (entradas) | 0 | 0 (sin cambios) |
| Llamadas a API de generación de imágenes | — | **0** |

`~/.hermes/hermes-agent/` (el paquete de la app, no un perfil de usuario) se
usó solo como **lectura** — `sys.path` para importar `agent.pet.generate.atlas`
y `agent.pet.store` — nunca se escribió nada ahí.

## Evidencia real de terminal — `hermes pets show`

Los 9 estados se renderizaron con el CLI real de Hermes (`hermes pets show
jorgito --state <estado> --once --mode unicode`) contra el perfil aislado,
usando `script -qec` para forzar un TTY real (el sandbox de esta sesión no
tiene uno; sin él, `hermes pets show` reporta
`cannot render here (no TTY / graphics disabled)`, comportamiento correcto,
no un fallo del atlas). Capturas ANSI truecolor crudas en
`assets/keyframes/terminal_render_final/<estado>.script.txt` (9 archivos,
17–28 KB cada uno, contenido real de escape codes 24-bit).

Además, réplica del render a escala real por defecto (`display.pet.scale` =
0.33 -> 16 columnas), rasterizada a PNG con
`scripts/render_final_atlas_pet.py` (adaptado del script homónimo de Fase 4):
`assets/keyframes/terminal_render_final/contact_sheet_terminal_final.png`
(1928x286, 9 estados lado a lado, etiquetados).

### Hallazgo honesto: el CLI instalado trunca a 6 frames por estado en reproducción

`agent/pet/constants.py: FRAMES_PER_STATE = 6` ("the petdex web app uses CSS
`steps(6)`") — el `PetRenderer` de este Hermes Agent instalado sólo reproduce
los primeros 6 frames de cualquier fila, sin importar cuántas columnas reales
tenga. Confirmado contando las secuencias de redibujado (`\x1b[<n>F`) en las
capturas crudas: `running-right`/`running-left`/`failed` (8 frames reales en
el atlas) sólo reproducen 6 en vivo; `waving` (4) y `jumping` (5) reproducen
completo porque están por debajo del tope.

Esto **no es un defecto del atlas** — `validate_atlas()` pasa, las 8 celdas
de esas filas existen, tienen hashes únicos, y siguen el spec documentado en
`atlas.py` (petdex/Codex 8 columnas). Es una constante de reproducción del
Hermes Agent instalado, ortogonal a este proyecto y ya documentada en su
propio código fuente como decisión deliberada (paridad con el reproductor
CSS del petdex web). Se documenta acá para que quede explícito antes de
Fase 5, no porque bloquee este gate.

## Fix post cross-review (opencode) — guardia de `~/.hermes` real bypassable con symlink

Cross-review independiente encontró un issue **bloqueante**: la guardia que
debe negarse a correr contra el `~/.hermes` real,

```python
if Path(hermes_home).resolve() == Path.home().resolve() / ".hermes":
```

solo resolvía `Path.home()`, no el componente `.hermes` concatenado
después. Si `~/.hermes` fuera alguna vez un symlink (setup común con
dotfile managers tipo stow/chezmoi), el lado izquierdo (`Path(hermes_home).resolve()`)
sigue cualquier symlink en `hermes_home` y llega al directorio real; el lado
derecho se queda con la ruta *sin resolver* del symlink — nunca son iguales,
y la guardia deja pasar la ejecución contra los datos reales. El reviewer lo
reprodujo empíricamente con un symlink de prueba (`bypass_successful = True`).

**Fix aplicado** en `scripts/install_final_atlas_pet.py` y
`scripts/render_final_atlas_pet.py` (guardia duplicada en ambos):

```python
if Path(hermes_home).resolve() == (Path.home() / ".hermes").resolve():
```

Ahora ambos lados resuelven la ruta completa, incluyendo un eventual symlink
en `~/.hermes`.

**Re-verificación explícita del caso symlink** (no alcanza con re-correr el
pipeline normal, según pidió el reviewer): `scripts/test_hermes_home_guard.py`
crea un `HOME` falso en un directorio temporal, con `.hermes` como symlink a
un target real, y reproduce el bypass:

```
[bypass via symlink target] old_guard blocks=False new_guard blocks=True
[direct symlink path]      old_guard blocks=False new_guard blocks=True
[isolated profile]         old_guard blocks=False new_guard blocks=False

All checks passed: the symlink bypass is reproduced against the old guard and closed by the new one.
```

Confirma: (1) la guardia vieja NO bloqueaba el bypass del reviewer — bug
reproducido; (2) la guardia vieja tampoco bloqueaba pasar el propio path del
symlink `~/.hermes` directamente — el bug era más amplio de lo reportado
inicialmente, afecta cualquier invocación mientras `~/.hermes` sea symlink,
no sólo cuando alguien pasa el target resuelto a mano; (3) la guardia nueva
bloquea ambos casos; (4) ningún falso positivo contra un perfil aislado
genuino.

También se re-corrió el pipeline completo end-to-end tras el fix
(`build_final_atlas.py` → `install_final_atlas_pet.py` →
`render_final_atlas_pet.py`) contra el perfil aislado real
(`/home/chegusan/.hermes-jorgito-test`): mismo resultado exacto que antes
(atlas final md5 `127e61046bfc95912df7d6ec5b189e08` sin cambios, 9/9
estados, hashes únicos), y se verificó explícitamente que
`HERMES_HOME=/home/chegusan/.hermes` (el real) es rechazado por la guardia
arreglada:

```
$ HERMES_HOME=/home/chegusan/.hermes install_final_atlas_pet.py
ERROR: refusing to run against the real ~/.hermes profile.
```

### No bloqueantes también resueltos (bajo costo, ya en el archivo)

- `render_final_atlas_pet.py` migrado de `renderer._frames(state)[0]` +
  `_downscale_cells` (privados) a la API pública `renderer.cells(state, 0,
  cols=cols)` — mismo grid de celdas, mismo resultado (contact sheet
  re-generado, byte-idéntico al anterior).
- `build_final_atlas.py`: `ROW_SOURCES` dejó de guardar un `source_row`
  redundante con `atlas.ROW_SPECS`; el crop siempre usa el `row` canónico de
  `ROW_SPECS`, eliminando la posibilidad de que ambos números diverjan.
  Además se agregó `_assert_no_cross_state_collisions()`: compara hashes
  entre todo par de estados que comparten un mismo archivo fuente (hoy sólo
  `idle`/`running`, ambos desde `atlas_full.png`) y aborta si dos estados
  distintos terminaran con frames idénticos — el caso que `validate_atlas()`
  y el chequeo de unicidad intra-fila no detectarían por sí solos, porque
  cada fila individualmente seguiría pareciendo válida y única, sólo que
  con el contenido del estado equivocado.

## Riesgos / decisiones a ojo del usuario

- El estado `running` en el atlas corresponde al `run` corto usado por
  `PetState` / la UI de Hermes (alias `run` -> `running` vía
  `STATE_ALIASES`); no confundir con locomoción — es el estado "trabajando"
  in-place (Fase 1/4 lo generaron así, no se tocó).
- `running-right` es un espejo matemático (`mirror_frames()`) de
  `running-left`, no una generación independiente — decisión ya tomada en
  addendum #8 de PR #8 por costo/tiempo, no en esta fase.
- El hallazgo de truncado a 6 frames arriba puede ser relevante para la
  decisión de Fase 5 si se quiere que `running-right`/`running-left`/`failed`
  se vean con sus 8 frames completos en producción; no se tocó nada del
  Hermes Agent instalado para resolverlo, queda fuera de alcance de este
  gate de contenido.
