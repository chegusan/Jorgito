# Proyecto: Jorgito — mascota Petdex para Hermes CLI

Actúen como un equipo multiagente de desarrollo encargado de crear, validar e integrar **Jorgito**, una mascota animada compatible con Petdex y destinada principalmente al **CLI/TUI de Hermes Agent en Arch Linux**.

El objetivo NO es construir un nuevo sistema de mascotas.

El objetivo es aprovechar al máximo la infraestructura que ya proporcionan:

* Hermes Agent
* Petdex
* el formato de sprites Petdex/Codex
* las herramientas oficiales existentes para creación de mascotas
* las suscripciones disponibles cuando puedan sustituir costes de API
* scripts determinísticos para composición, validación y transformación de imágenes

El proyecto debe optimizar simultáneamente:

1. funcionalidad;
2. compatibilidad;
3. simplicidad;
4. consistencia visual;
5. tiempo de desarrollo;
6. consumo de tokens;
7. coste económico;
8. facilidad de mantenimiento.

---

# 1. Principios obligatorios

## Regla principal

Antes de escribir código nuevo, comprobar si la funcionalidad ya existe en:

1. Hermes;
2. Petdex;
3. Codex/hatch-pet;
4. herramientas de sistema existentes.

Orden obligatorio de complejidad:

1. configuración existente;
2. assets compatibles;
3. scripts determinísticos pequeños;
4. adapter externo pequeño;
5. modificación upstream;
6. fork o infraestructura propia.

No avanzar al siguiente nivel si el anterior puede resolver correctamente el problema.

---

# 2. Arquitectura objetivo del MVP

La arquitectura deseada es:

```text
Hermes Agent
      ↓
estado interno existente
      ↓
mapping Petdex existente de Hermes
      ↓
spritesheet estándar
      ↓
Jorgito animado en CLI/TUI
```

No desarrollar inicialmente:

* nueva API;
* daemon;
* servidor;
* sistema de eventos propio;
* hooks duplicados;
* estado custom;
* spritesheet v2 salvo necesidad demostrada;
* Petdex Desktop;
* fork de Petdex;
* fork de Hermes;
* sistema de emociones;
* sonidos;
* miniagentes visuales;
* memoria de mascota;
* lógica que consuma LLM mientras la mascota se ejecuta.

La mascota debe ser un componente puramente visual.

---

# 3. Identidad canónica de Jorgito

Existe una imagen de referencia aprobada por el usuario.

Esa imagen debe tratarse como la **fuente canónica de identidad**.

No rediseñar al personaje salvo simplificaciones necesarias para legibilidad en terminal.

Características que deben conservarse:

* pequeño dragón amigable;
* ojos verdes muy grandes con blanco visible;
* expresión amable y ligeramente torpe;
* cuernos pequeños;
* proporciones compactas;
* cuerpo rojo/carmesí/borgoña;
* placas amarillas en cuello y abdomen;
* alas rojas con membranas amarillas;
* dos patas traseras;
* dos brazos delanteros;
* cola larga enrollada;
* estética pixel-art limpia;
* silueta claramente reconocible.

Prioridades visuales:

1. reconocer inmediatamente a Jorgito;
2. entender inmediatamente la acción;
3. buena lectura a tamaño reducido;
4. consistencia entre frames;
5. perfección artística.

No perseguir pixel-perfect consistency si hacerlo multiplica el coste.

Se aceptan pequeñas variaciones entre frames siempre que identidad, silueta y acción permanezcan claras.

---

# 4. Estados funcionales

Para el MVP utilizar exclusivamente los estados que Hermes ya reconoce.

Mapping funcional objetivo:

```text
Hermes idle
→ Jorgito idle

Hermes review
→ THINKING
→ Jorgito leyendo un libro con anteojos

Hermes run
→ WORKING
→ Jorgito usando una pala y moviendo/cavando tierra

Hermes waiting
→ Jorgito esperando al usuario

Hermes failed
→ Jorgito mostrando un error/reacción cómica leve

Hermes jump
→ celebración

Hermes wave
→ saludo / finalización positiva
```

Las acciones `review` y `run` son prioritarias porque comunican los dos estados principales del agente.

## Thinking / review

Jorgito debe:

* llevar anteojos;
* sostener o leer un libro;
* parecer concentrado;
* seguir siendo claramente reconocible;
* mantener una animación simple y cíclica.

La animación puede utilizar:

* pequeños movimientos de cabeza;
* cambio de página;
* parpadeo;
* leve desplazamiento del libro.

No agregar elementos innecesarios.

## Working / run

Jorgito debe:

* sostener una pala;
* cavar o mover tierra;
* mostrar actividad física repetitiva;
* conservar una silueta clara.

La pala debe ser visible incluso a tamaño reducido.

El movimiento puede consistir en:

1. levantar pala;
2. bajarla;
3. recoger tierra;
4. moverla;
5. regresar a posición inicial.

Mantener el terreno/tierra visualmente mínimo para no saturar el sprite.

---

# 5. Estrategia de generación de assets

Usar una estrategia escalonada.

## Camino A — Primera opción

Evaluar primero el workflow oficial:

```text
Codex CLI
+
hatch-pet
+
imagegen integrado
+
imagen canónica de Jorgito
```

Motivo:

* ya está diseñado para crear mascotas compatibles;
* utiliza reference-image grounding;
* genera filas de animación;
* realiza slicing determinístico;
* construye el spritesheet;
* valida el resultado;
* reduce considerablemente el código propio necesario.

No generar manualmente 72 imágenes independientes si `hatch-pet` puede producir correctamente las filas.

### Restricción de coste

NO lanzar inmediatamente una generación completa.

Primero hacer una prueba limitada.

---

# 6. FASE 0 — Auditoría del entorno

## Objetivo

Confirmar exactamente qué soporta la instalación actual antes de modificar nada.

## Tareas

Detectar:

```bash
hermes --version
hermes pets doctor
```

Comprobar disponibilidad de:

```bash
hermes pets
hermes pets show
/pet
/hatch
```

Detectar:

* `$HERMES_HOME`;
* versión de Hermes;
* terminal actual;
* protocolo gráfico soportado;
* modo de fallback si no existe protocolo gráfico;
* versión de Node/Bun;
* disponibilidad de `npx petdex`;
* disponibilidad de Codex CLI;
* autenticación de Codex;
* disponibilidad del skill `hatch-pet`.

No instalar herramientas hasta saber cuáles faltan.

## Test de validación F0

Instalar temporalmente una mascota conocida de Petdex:

```bash
hermes pets install <pet-existente> --select
hermes pets show
```

Luego:

```bash
hermes pets show --state idle
hermes pets show --state review
hermes pets show --state run
hermes pets show --state waiting
hermes pets show --state failed
hermes pets show --state jump
hermes pets show --state wave
```

### PASS

* Hermes muestra correctamente una mascota Petdex.
* Las animaciones funcionan en el terminal utilizado.
* Los estados pueden invocarse.

### FAIL

No generar todavía ningún asset de Jorgito.

Resolver primero la compatibilidad/rendering.

---

# 7. FASE 1 — Prototipo visual mínimo

## Objetivo

Comprobar que podemos transformar la referencia de Jorgito en sprites legibles SIN generar toda la mascota.

Generar únicamente:

1. `idle`;
2. `review`;
3. `run`.

No generar los otros estados todavía.

## Método preferido

Utilizar Codex `hatch-pet` o sus componentes de generación manteniendo la imagen canónica como referencia.

Intentar obtener:

```text
idle → Jorgito normal
review → libro + anteojos
run → pala + tierra
```

No buscar perfección.

## Test de validación F1-A — identidad

Crear un contact sheet con frames representativos.

Preguntas:

* ¿Sigue siendo claramente Jorgito?
* ¿Se mantienen ojos verdes?
* ¿Se mantiene rojo/borgoña + amarillo?
* ¿Se reconocen alas?
* ¿Se reconoce la cola?
* ¿Cambió excesivamente la anatomía?
* ¿aparecieron detalles innecesarios?

### PASS

La identidad es claramente reconocible.

### FAIL

Una sola ronda de corrección.

Si después de dos intentos la generación automática sigue alterando demasiado al personaje, detener Camino A y pasar a Camino B.

NO entrar en loops de regeneración.

---

# 8. Test F1-B — legibilidad real en terminal

Empaquetar temporalmente esas animaciones en un pet de prueba.

Mostrar:

```bash
hermes pets show jorgito-test --state idle
hermes pets show jorgito-test --state review
hermes pets show jorgito-test --state run
```

Evaluar al tamaño real usado en CLI.

Criterios:

### review

Debe entenderse que:

```text
Jorgito está leyendo/pensando.
```

### run

Debe entenderse que:

```text
Jorgito está trabajando/cavando.
```

No evaluar sólo imágenes ampliadas.

### PASS

Acciones entendibles en terminal.

### FAIL

Simplificar silueta/props antes de aumentar resolución o detalle.

---

# 9. FASE 2 — Decisión A vs B

Después de Fase 1 calcular:

* cantidad de generaciones realizadas;
* regeneraciones necesarias;
* consumo aproximado;
* tiempo;
* consistencia;
* cantidad de trabajo manual;
* calidad final.

## Mantener Camino A si

* la identidad permanece estable;
* las acciones son claras;
* las filas necesitan como máximo una corrección ocasional;
* el coste es razonable.

Entonces usar el pipeline existente para las demás filas.

## Cambiar a Camino B si

* las generaciones cambian frecuentemente al personaje;
* requieren múltiples retries;
* el coste crece demasiado;
* los movimientos simples pueden derivarse mejor programáticamente.

---

# 10. Camino B — derivación programática

No crear un motor de animaciones.

Usar únicamente transformaciones simples y determinísticas.

Herramientas permitidas:

* Pillow;
* ImageMagick;
* utilidades incluidas en `hatch-pet`;
* scripts Python pequeños.

Transformaciones posibles:

* desplazamiento X/Y;
* mirror horizontal;
* rotaciones mínimas;
* squash/stretch ligero;
* parpadeo mediante modificación localizada;
* movimiento de brazos/props si existe una separación viable;
* composición de partículas o tierra;
* repetición de frames;
* ping-pong;
* frame hold.

Priorizar:

```text
2–4 keyframes reales
→ derivados hasta completar el ciclo
```

en lugar de:

```text
8 generaciones distintas
```

No intentar interpolación mediante nuevos modelos AI salvo que sea claramente más barato y fiable.

---

# 11. FASE 3 — Completar estados Petdex

Una vez aprobado el núcleo visual, completar:

* idle;
* running-right;
* running-left;
* waving;
* jumping;
* failed;
* waiting;
* running;
* review.

Sin embargo, para Hermes los estados prioritarios son:

```text
idle
review
run
waiting
failed
jump
wave
```

Los estados de desplazamiento deben ser simples.

`running-left` debe derivarse mediante mirror de `running-right` si la composición lo permite.

No generar una nueva fila AI para izquierda salvo necesidad visual comprobada.

---

# 12. Diseño mínimo de los estados secundarios

## Idle

* respiración;
* pestañeo;
* pequeña oscilación de cola.

## Waiting

* Jorgito quieto/sentado;
* mirada de espera;
* movimiento mínimo.

## Failed

* reacción confundida;
* pequeña nube de humo opcional;
* expresión amigable, no dramática.

## Jump

* salto corto;
* ligera apertura de alas;
* celebración.

## Wave

* saludo con un brazo;
* expresión feliz.

## Running-right / left

* desplazamiento simple;
* no necesitan narrativa adicional.

---

# 13. FASE 4 — Construcción del paquete Petdex

Resultado esperado:

```text
jorgito/
├── pet.json
└── spritesheet.png
```

o `.webp`.

Utilizar el formato estándar Petdex/Codex compatible con Hermes.

No introducir formatos propietarios.

Validar:

* dimensiones;
* número de filas;
* columnas;
* transparencia;
* frame boundaries;
* metadata;
* nombres de estados;
* loops;
* ausencia de pixels contaminando celdas vecinas.

Usar validadores existentes antes de programar uno nuevo.

---

# 14. Test F4 — validación estructural

Ejecutar todas las validaciones disponibles de Petdex/hatch-pet.

Luego intentar carga local en Hermes.

### PASS

Hermes reconoce el paquete sin modificaciones del runtime.

### FAIL

Corregir primero metadata/atlas.

No modificar Hermes para acomodar un asset incorrecto.

---

# 15. FASE 5 — integración real con Hermes

Instalar/seleccionar Jorgito en el perfil real.

Probar:

```bash
hermes pets show jorgito --cycle
```

Después probar dentro de una sesión real.

Escenarios:

### Test A — idle

No ejecutar tarea.

Esperado:

```text
idle
```

### Test B — thinking

Pedir una tarea que requiera razonamiento/lectura.

Esperado:

```text
review
→ Jorgito leyendo libro con anteojos
```

### Test C — tool execution

Pedir una tarea que use herramientas.

Esperado:

```text
run
→ Jorgito cavando con pala
```

### Test D — waiting

Provocar una aclaración o aprobación.

Esperado:

```text
waiting
```

### Test E — success

Completar una tarea.

Esperado:

```text
wave o jump según evento
```

### Test F — failure

Provocar un error controlado y no destructivo.

Esperado:

```text
failed
```

---

# 16. Criterio de aceptación del MVP

El proyecto está terminado cuando:

1. Jorgito aparece en Hermes CLI.
2. No requiere Petdex Desktop.
3. No requiere modificar Hermes.
4. No requiere proceso adicional en background.
5. Idle funciona.
6. Thinking muestra libro + anteojos.
7. Working muestra pala + tierra.
8. Waiting funciona.
9. Success funciona.
10. Failure funciona.
11. La mascota sigue siendo reconociblemente Jorgito.
12. Las acciones se entienden a tamaño real.
13. El rendimiento de Hermes no cambia de forma perceptible.
14. La mascota no añade llamadas LLM durante ejecución.
15. No existe coste recurrente por usar la mascota una vez creada.

---

# 17. FASE 6 — optimización

Sólo después del MVP.

Medir:

* tamaño de spritesheet;
* tiempo de carga;
* consumo RAM;
* fluidez;
* frame rate;
* legibilidad;
* comportamiento en fallback Unicode.

Optimizar únicamente problemas medidos.

No optimizar por anticipado.

Posibles acciones:

* WebP si reduce peso sin romper compatibilidad;
* eliminar frames redundantes;
* reutilizar ciclos;
* reducir partículas;
* corregir posiciones;
* ajustar escala.

---

# 18. FASE 7 — preparar integración controlada, sin implementarla

Documentar dónde podría añadirse posteriormente:

```text
Hermes state
→ pequeño mapping/control layer
→ Petdex state
```

Pero NO implementarlo en el MVP.

Sólo registrar:

* punto de integración;
* estados disponibles;
* interfaces existentes;
* cambios mínimos necesarios.

El sistema actual debe permanecer basado en el mapping nativo de Hermes.

---

# 19. Política estricta de gasto

Cada agente debe preguntarse antes de utilizar un modelo:

```text
¿Esto puede resolverse mediante código determinístico?
```

Si sí:

```text
NO usar modelo generativo.
```

Para imágenes:

1. reutilizar;
2. mirror;
3. transformar;
4. recomponer;
5. generar nuevo asset.

En ese orden.

Máximo inicial:

```text
3 estados generados para Fase 1.
```

No generar el set completo antes de aprobarlos.

Máximo recomendado por estado durante desarrollo:

```text
1 generación inicial
+
1 reparación
```

Una tercera generación requiere justificar por qué no puede corregirse programáticamente.

---

# 20. Política multiagente

El coordinador debe mantener el número de agentes bajo.

No asignar agentes en paralelo simplemente porque están disponibles.

Usar especialistas sólo cuando permitan reducir trabajo total.

Roles sugeridos:

## Coordinator

* controla fases;
* impide sobreingeniería;
* lleva presupuesto;
* decide PASS/FAIL.

## Research/Compatibility Agent

Sólo Fase 0.

* verifica versiones;
* documentación;
* formatos;
* capacidades existentes.

Cerrar el agente al terminar.

## Asset Agent

Sólo generación/reparación visual.

No programa infraestructura.

## Deterministic Image Agent

Sólo cuando se necesite manipular frames/atlas.

Usar scripts antes que LLM.

## QA Agent

Evalúa contact sheets y tests finales.

No regenera por iniciativa propia.

No mantener cinco agentes activos permanentemente.

---

# 21. Reglas de contexto y tokens

Los subagentes NO necesitan toda la conversación.

Darles sólo:

```text
tarea
+
asset necesario
+
criterios PASS/FAIL
+
salida esperada
```

No reenviar investigaciones enteras a cada worker.

Guardar decisiones en archivos cortos:

```text
PROJECT_STATE.md
ASSET_SPEC.md
TEST_RESULTS.md
```

El coordinator debe leer esos archivos en lugar de reconstruir la historia completa en cada fase.

Cada archivo debe mantenerse breve.

---

# 22. Gate obligatorio entre fases

Formato:

```text
PHASE N RESULT

Status: PASS | FAIL

Evidence:
- ...

Cost:
- generations:
- retries:
- approximate model usage:
- development time:

Problems:
- ...

Decision:
- continue
- repair
- fallback
- stop
```

Una fase FAIL bloquea la siguiente.

---

# 23. Primera acción del sistema

NO empezar generando imágenes.

Primero:

1. inspeccionar entorno;
2. inspeccionar versión instalada de Hermes;
3. comprobar soporte Petdex real;
4. ejecutar `hermes pets doctor`;
5. instalar una mascota conocida;
6. probar los estados;
7. verificar Codex + `hatch-pet`;
8. reportar Fase 0.

Sólo después de PASS pedir/utilizar la imagen canónica de Jorgito para Fase 1.

---

# Resultado esperado

Entregar finalmente:

```text
jorgito/
├── pet.json
├── spritesheet.png|webp
└── opcionalmente:
    ├── README.md
    └── source/
```

Más un informe muy corto con:

* método utilizado;
* tests superados;
* compatibilidad;
* coste/generaciones realizadas;
* instrucciones para instalar;
* posibles mejoras futuras.

La solución correcta es la **más pequeña que funcione bien**.
